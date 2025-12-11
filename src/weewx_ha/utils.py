"""Utility functions and data."""

# Standard Python Libraries
from copy import deepcopy
from datetime import datetime, timezone
from enum import Enum
import logging
import re
from typing import Any, Optional

# Third-Party Libraries
import weewx  # type: ignore
from weewx.units import getStandardUnitType  # type: ignore

from .locale_loader import load_enums, load_sensors, load_units

logger = logging.getLogger(__name__)


# Load configuration from YAML files
ENUM_MAPS: dict[str, dict[int, str]] = load_enums()
UNIT_METADATA: dict[str, dict[str, Optional[str]]] = load_units()
_SENSORS_YAML: dict[str, Any] = load_sensors()


def degrees_to_cardinal(degrees: float) -> str:
    """Convert wind direction in degrees to cardinal direction.

    Parameters
    ----------
    degrees : float
        Wind direction in degrees (0-360)

    Returns
    -------
    str
        Cardinal direction (e.g., "N", "NE", "SW", "NNW")

    """
    # Each direction covers 22.5 degrees (360/16)
    # Add 11.25 to center the ranges, then divide by 22.5
    index = int((degrees + 11.25) / 22.5) % 16
    return ENUM_MAPS["cardinal_directions"][index]


class UnitSystem(str, Enum):
    """Enumeration of unit systems supported by WeeWX.

    Casting to int returns the WeeWX unit system value.
    """

    METRIC = ("METRIC", weewx.METRIC)
    METRICWX = ("METRICWX", weewx.METRICWX)
    US = ("US", weewx.US)

    def __new__(cls, value: str, weewx_value: int):
        """Create a new instance of the enumeration."""
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.__dict__["_weewx_value"] = (
            weewx_value  # Using __dict__ to set a protected attribute
        )
        return obj

    def __int__(self):
        """Return the WeeWX unit system value."""
        return self._weewx_value

    def __str__(self):
        """Return the unit system value."""
        return self.value

    @classmethod
    def from_int(cls, value: int) -> "UnitSystem":
        """Get the unit system enumeration value from a WeeWX unit system value."""
        for unit_system in cls:
            if int(unit_system) == value:
                return unit_system
        raise ValueError(f"Invalid unit system value: {value}")


def get_unit_metadata(measurement_name: str, unit_system: UnitSystem) -> dict[str, Any]:
    """Generate metadata for a measurement unit based on the unit system."""
    (target_unit, target_group) = getStandardUnitType(
        int(unit_system), measurement_name
    )

    if target_unit is None:
        # take a guess at the unit based on the measurement name
        if measurement_name == "usUnits":
            pass  # Nothing to do for usUnits, this is a special case
        elif measurement_name.endswith("ET"):
            # Map other evapotranspiration measurements (dayET, monthET, yearET) to the same unit as ET
            (target_unit, _) = getStandardUnitType(int(unit_system), "ET")
        elif measurement_name in {"sunrise", "sunset", "stormStart"}:
            (target_unit, _) = getStandardUnitType(int(unit_system), "dateTime")
        else:
            logger.warning(
                "No unit found for measurement '%s' in unit system %s",
                measurement_name,
                unit_system,
            )
        if target_unit:
            logger.info(
                "Guessed unit '%s' for measurement %s", target_unit, measurement_name
            )

    return UNIT_METADATA.get(
        target_unit,
        {"unit_of_measurement": target_unit},  # Defaults to the WeeWX unit if not found
    )


def get_key_config(weewx_key: str) -> dict[str, Any]:
    """Generate metadata for a WeeWX key."""
    # First, attempt an exact match for the key
    config = KEY_CONFIG.get(weewx_key)
    if config:
        return config

    # Next, remove numeric suffix to check for a base key match
    match = re.match(r"(.*?)(\d+)$", weewx_key)
    if match:
        base_key, suffix = match.groups()
        # If the base key is found in the known keys mapping, construct the friendly name
        config = deepcopy(KEY_CONFIG.get(base_key))
        if config:
            config["metadata"]["name"] = f"{config['metadata']['name']} {suffix}"
            return config

    # If we still haven't found a match, generate a friendly name from the key
    # Add space before digits (e.g., extraAlarm5 -> extraAlarm 5)
    key_with_spaces = re.sub(r"(\d+)", r" \1", weewx_key)

    # Split camel case (e.g., extraAlarm 5 -> Extra Alarm 5)
    key_split = re.sub(r"(?<!^)(?=[A-Z])", " ", key_with_spaces).title()

    # Handle "in", "out", "tx", and "rx" prefixes for indoor, outdoor, transmit, and receive
    if key_split.startswith("In "):
        key_split = key_split.replace("In ", "Indoor ", 1)
    elif key_split.startswith("Out "):
        key_split = key_split.replace("Out ", "Outdoor ", 1)
    elif key_split.startswith("Tx "):
        key_split = key_split.replace("Tx ", "Transmit ", 1)
    elif key_split.startswith("Rx "):
        key_split = key_split.replace("Rx ", "Receive ", 1)

    # Guess at what the metadata should be based on the key
    guess: dict[str, Any] = {"metadata": {}}
    if "alarm" in key_split.lower():
        guess = deepcopy(KEY_CONFIG["extraAlarm"])
    elif "humidity" in key_split.lower():
        guess = deepcopy(KEY_CONFIG["outHumidity"])
    elif "pressure" in key_split.lower():
        guess = deepcopy(KEY_CONFIG["pressure"])
    elif "temperature" in key_split.lower():
        guess = deepcopy(KEY_CONFIG["outTemp"])

    guess["metadata"]["name"] = key_split

    logger.warning("Guessed metadata for key '%s': %s", weewx_key, guess)
    return guess


# Lambda function registry for convert_lambda references in YAML
_LAMBDA_REGISTRY = {
    "beaufort_scale_map": lambda x, cp: ENUM_MAPS["beaufort_scale"].get(
        int(x), f"{int(x)} - Unknown"
    ),
    "degrees_to_cardinal": lambda x, cp: degrees_to_cardinal(x),
    "localtime_to_utc_timestamp": lambda x, cp: datetime.fromtimestamp(x)
    .replace(tzinfo=cp.time_zone)
    .astimezone(tz=timezone.utc)
    .timestamp(),
    "unit_system_to_string": lambda x, cp: str(UnitSystem.from_int(x)),
}


def _build_key_config() -> dict[str, Any]:
    """Build KEY_CONFIG from YAML data with lambda functions.

    Returns
    -------
    dict[str, Any]
        Complete KEY_CONFIG dictionary with lambda functions

    """
    config = deepcopy(_SENSORS_YAML)

    for sensor_name, sensor_config in config.items():
        # Replace convert_lambda string references with actual lambda functions
        if "convert_lambda" in sensor_config:
            lambda_name = sensor_config["convert_lambda"]
            if lambda_name in _LAMBDA_REGISTRY:
                sensor_config["convert_lambda"] = _LAMBDA_REGISTRY[lambda_name]
            else:
                logger.warning(
                    f"Unknown convert_lambda reference '{lambda_name}' for sensor '{sensor_name}'"
                )
                del sensor_config["convert_lambda"]

    return config


KEY_CONFIG: dict[str, Any] = _build_key_config()
