"""Loader for localized configuration from YAML files."""

# Standard Python Libraries
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

# Third-Party Libraries
import yaml  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

# Global language setting (can be set from configuration)
_current_language: Optional[str] = None


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Deep merge two dictionaries, with overlay taking precedence.

    Parameters
    ----------
    base : dict
        Base dictionary (fallback values)
    overlay : dict
        Overlay dictionary (localized values)

    Returns
    -------
    dict
        Merged dictionary with overlay values taking precedence

    """
    result = deepcopy(base)

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _deep_merge(result[key], value)
        else:
            # Use overlay value
            result[key] = deepcopy(value)

    return result


def set_language(language: Optional[str]) -> None:
    """Set the current language for loading localized YAML files.

    Parameters
    ----------
    language : Optional[str]
        Language code (e.g., 'cs', 'en', 'de') or None for default

    """
    global _current_language
    _current_language = language
    logger.info(f"Language set to: {language or 'default (fallback)'}")


def get_language() -> Optional[str]:
    """Get the current language setting.

    Returns
    -------
    Optional[str]
        Current language code or None

    """
    return _current_language


def load_yaml(base_filename: str, language: Optional[str] = None) -> dict[str, Any]:
    """Load YAML configuration file from locales directory with language fallback.

    Supports partial localization: loads base file first, then merges localized
    file on top. Missing keys in localized file will use fallback values.

    Parameters
    ----------
    base_filename : str
        Base name of the YAML file (e.g., 'enums.yaml')
    language : Optional[str]
        Language code to try first, or None to use global setting

    Returns
    -------
    dict[str, Any]
        Loaded configuration dictionary (merged if localized file exists)

    """
    locales_dir = Path(__file__).parent / "locales"

    # Use provided language or global setting
    lang = language or _current_language

    # Always load base file as fallback
    base_file_path = locales_dir / base_filename
    base_data: dict[str, Any] = {}

    try:
        with open(base_file_path, "r", encoding="utf-8") as f:
            base_data = yaml.safe_load(f) or {}
            logger.debug(f"Loaded base configuration from {base_file_path}")
    except FileNotFoundError:
        logger.error(f"Base configuration file not found: {base_file_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing base YAML file {base_file_path}: {e}")
        return {}

    # If no language specified, return base data
    if not lang:
        return base_data

    # Try to load localized file
    name_parts = base_filename.rsplit('.', 1)
    if len(name_parts) == 2:
        name, ext = name_parts
        localized_filename = f"{name}_{lang}.{ext}"
        localized_file_path = locales_dir / localized_filename

        try:
            with open(localized_file_path, "r", encoding="utf-8") as f:
                localized_data = yaml.safe_load(f) or {}
                logger.info(
                    f"Loaded localized configuration from {localized_file_path}, "
                    f"merging with base"
                )
                # Deep merge: base data with localized overlay
                return _deep_merge(base_data, localized_data)
        except FileNotFoundError:
            logger.debug(
                f"Localized file not found: {localized_file_path}, using base only"
            )
        except yaml.YAMLError as e:
            logger.error(
                f"Error parsing localized YAML file {localized_file_path}: {e}, "
                f"using base only"
            )

    # Return base data if localized file not found or error occurred
    return base_data


def load_enums(language: Optional[str] = None) -> dict[str, dict[int, str]]:
    """Load enum mappings from YAML file with language support.

    Parameters
    ----------
    language : Optional[str]
        Language code to load, or None to use global setting

    Returns
    -------
    dict[str, dict[int, str]]
        Dictionary of enum mappings

    """
    return load_yaml("enums.yaml", language)


def load_units(language: Optional[str] = None) -> dict[str, dict[str, Any]]:
    """Load unit metadata from YAML file with language support.

    Parameters
    ----------
    language : Optional[str]
        Language code to load, or None to use global setting

    Returns
    -------
    dict[str, dict[str, Any]]
        Dictionary of unit metadata

    """
    return load_yaml("units.yaml", language)


def load_sensors(language: Optional[str] = None) -> dict[str, Any]:
    """Load sensor configurations from YAML file with language support.

    Parameters
    ----------
    language : Optional[str]
        Language code to load, or None to use global setting

    Returns
    -------
    dict[str, Any]
        Dictionary of sensor configurations

    """
    data = load_yaml("sensors.yaml", language)

    # Process special markers like @cardinal_directions
    enums = load_enums(language)

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

