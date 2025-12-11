"""Loader for localized configuration from YAML files."""

# Standard Python Libraries
import logging
from pathlib import Path
from typing import Any

# Third-Party Libraries
import yaml

logger = logging.getLogger(__name__)


def load_yaml(filename: str) -> dict[str, Any]:
    """Load YAML configuration file from locales directory.

    Parameters
    ----------
    filename : str
        Name of the YAML file to load (without path)

    Returns
    -------
    dict[str, Any]
        Loaded configuration dictionary

    """
    locales_dir = Path(__file__).parent / "locales"
    file_path = locales_dir / filename

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            logger.debug(f"Loaded configuration from {file_path}")
            return data or {}
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {file_path}: {e}")
        return {}


def load_enums() -> dict[str, dict[int, str]]:
    """Load enum mappings from YAML file.

    Returns
    -------
    dict[str, dict[int, str]]
        Dictionary of enum mappings

    """
    return load_yaml("enums.yaml")


def load_units() -> dict[str, dict[str, Any]]:
    """Load unit metadata from YAML file.

    Returns
    -------
    dict[str, dict[str, Any]]
        Dictionary of unit metadata

    """
    return load_yaml("units.yaml")


def load_sensors() -> dict[str, Any]:
    """Load sensor configurations from YAML file.

    Returns
    -------
    dict[str, Any]
        Dictionary of sensor configurations

    """
    data = load_yaml("sensors.yaml")

    # Process special markers like @cardinal_directions
    enums = load_enums()

    def process_value(value: Any) -> Any:
        """Recursively process values to resolve enum references."""
        if isinstance(value, str) and value.startswith("@"):
            # Reference to enum mapping
            enum_name = value[1:]  # Remove @ prefix
            if enum_name in enums:
                return list(enums[enum_name].values())
            logger.warning(f"Unknown enum reference: {value}")
            return value
        elif isinstance(value, dict):
            return {k: process_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [process_value(v) for v in value]
        return value

    return {key: process_value(config) for key, config in data.items()}

