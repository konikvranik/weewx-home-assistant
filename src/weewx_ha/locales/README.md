# Localization System

This directory contains YAML configuration files for sensor definitions, unit metadata, and enum mappings.

## Structure

```
locales/
├── enums.yaml          # Enum mappings (cardinal directions, Beaufort scale)
├── units.yaml          # Unit metadata (units of measurement, formatting)
├── sensors.yaml        # Sensor configurations (names, icons, device classes)
└── cs_enums.yaml.example  # Example Czech translation
```

## Files

### enums.yaml
Defines enum mappings for sensors with `device_class: enum`:
- `cardinal_directions`: Wind direction abbreviations (N, NE, E, etc.)
- `beaufort_scale`: Beaufort wind scale descriptions

### units.yaml
Defines unit metadata for different measurement units:
- `unit_of_measurement`: The unit symbol (e.g., "°C", "m/s")
- `value_template`: Jinja2 template for rounding (e.g., "{{ value | round(1) }}")

### sensors.yaml
Defines configuration for each sensor type:
- `metadata`: Home Assistant discovery metadata
  - `name`: Human-readable sensor name
  - `icon`: Material Design Icon (e.g., "mdi:thermometer")
  - `device_class`: Home Assistant device class
  - `state_class`: State class for statistics
  - `unit_of_measurement`: Override unit (usually from units.yaml)
- `convert_lambda`: Reference to conversion function (e.g., "degrees_to_cardinal")
- `source`: Source key for derived sensors (e.g., "windDir" for "windDirCardinal")
- `integration`: Override integration type (e.g., "binary_sensor")

## Special Syntax

### Enum References
Use `@enum_name` to reference enum values:
```yaml
windDirCardinal:
  metadata:
    options: "@cardinal_directions"  # Expands to list of cardinal direction values
```

### Lambda Functions
Reference lambda functions by name in YAML:
```yaml
beaufort:
  convert_lambda: "beaufort_scale_map"  # Mapped to Python lambda in _LAMBDA_REGISTRY
```

Available lambda functions:
- `beaufort_scale_map`: Maps Beaufort number to scale description
- `degrees_to_cardinal`: Converts degrees to cardinal direction
- `localtime_to_utc_timestamp`: Converts local time to UTC timestamp
- `unit_system_to_string`: Converts WeeWX unit system int to string

## Localization

To create a localized version:

1. Create language subdirectory: `mkdir -p locales/cs`
2. Copy and translate YAML files:
   ```bash
   cp enums.yaml locales/cs/enums.yaml
   cp sensors.yaml locales/cs/sensors.yaml
   ```
3. Translate strings in the copied files
4. Modify `locale_loader.py` to support language selection

### Example Czech Translation

See `cs_enums.yaml.example` for a sample Czech translation of enum values.

## Adding New Sensors

1. Add sensor definition to `sensors.yaml`:
   ```yaml
   newSensor:
     metadata:
       name: "New Sensor"
       icon: "mdi:icon-name"
       device_class: "temperature"
       state_class: "measurement"
   ```

2. No Python code changes needed - sensor will be automatically loaded!

## Adding New Lambda Functions

1. Add function to `_LAMBDA_REGISTRY` in `utils.py`:
   ```python
   _LAMBDA_REGISTRY = {
       "new_converter": lambda x, cp: custom_conversion(x),
   }
   ```

2. Reference in YAML:
   ```yaml
   sensor:
     convert_lambda: "new_converter"
   ```

## Validation

Python syntax validation:
```bash
python3 -m py_compile src/weewx_ha/utils.py src/weewx_ha/locale_loader.py
```

YAML syntax validation:
```bash
python3 -c "import yaml; yaml.safe_load(open('src/weewx_ha/locales/sensors.yaml'))"
```

## Benefits

- **Easy maintenance**: Edit YAML instead of Python code
- **Localization ready**: Simple to create translations
- **No code changes**: Add/modify sensors without touching Python
- **Version control friendly**: YAML diffs are easy to read
- **Validation**: YAML syntax errors caught at load time

