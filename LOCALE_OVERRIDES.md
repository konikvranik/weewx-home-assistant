# Locale Configuration Overrides

This document describes how to override or extend locale data (sensors, units, enums) using WeeWX configuration.

## Overview

The extension loads locale data from YAML files in the following priority order (lowest to highest):

1. **Base YAML files** (e.g., `sensors.yaml`, `units.yaml`, `enums.yaml`)
2. **Localized YAML files** (e.g., `sensors_cs.yaml`, `units_cs.yaml`, `enums_cs.yaml`)
3. **Configuration overrides** (from `weewx.conf`)

Configuration overrides have the highest priority and can be used to customize or extend any locale data without modifying the YAML files.

## Configuration Structure

Add overrides directly under the `[HomeAssistant]` section in your WeeWX configuration:

```ini
[HomeAssistant]
    # ... other settings ...
    
    [[sensors]]
        # Sensor configuration overrides
        
    [[units]]
        # Unit metadata overrides
        
    [[enums]]
        # Enum mapping overrides
```

## Use Cases

### 1. Override Sensor Name

Change the display name of a sensor:

```ini
[[sensors]]
    [[[outTemp]]]
        [[[[metadata]]]]
            name = "Outside Temperature (Custom)"
```

### 2. Customize Unit Rounding

Change how a unit value is rounded:

```ini
[[units]]
    [[[degree_C]]]
        value_template = "{{ value | round(0) }}"  # No decimals instead of 1
```

### 3. Override Unit of Measurement

Change the unit symbol displayed:

```ini
[[units]]
    [[[degree_C]]]
        unit_of_measurement = "°Celsius"
```

### 4. Customize Enum Values

Override enum text values:

```ini
[[enums]]
    [[[forecast_rule]]]
        0 = "Mostly Clear"
        1 = "Partly Cloudy"
        2 = "Mostly Cloudy"
```

### 5. Add Custom Sensor Configuration

Add configuration for a custom sensor not in default YAML:

```ini
[[sensors]]
    [[[myCustomSensor]]]
        [[[[metadata]]]]
            name = "My Custom Sensor"
            device_class = "temperature"
            state_class = "measurement"
```

### 6. Partial Override

You only need to specify what you want to override. Other properties will be inherited from YAML files:

```ini
[[sensors]]
    [[[outTemp]]]
        [[[[metadata]]]]
            name = "Custom Name"
            # device_class, state_class, etc. will be loaded from YAML
```

## Deep Merge Behavior

The override mechanism uses deep merging:

- Nested dictionaries are merged recursively
- Values in overrides replace values from YAML files
- Missing keys in overrides are preserved from YAML files

### Example

Base `sensors.yaml`:
```yaml
outTemp:
  metadata:
    name: "Outdoor Temperature"
    device_class: "temperature"
    state_class: "measurement"
    icon: "mdi:thermometer"
```

Localized `sensors_cs.yaml`:
```yaml
outTemp:
  metadata:
    name: "Venkovní teplota"
```

Configuration override:
```ini
[[sensors]]
    [[[outTemp]]]
        [[[[metadata]]]]
            name = "Teplota venku (custom)"
```

Final result:
```yaml
outTemp:
  metadata:
    name: "Teplota venku (custom)"  # From config override
    device_class: "temperature"     # From base YAML
    state_class: "measurement"      # From base YAML
    icon: "mdi:thermometer"        # From base YAML
```

## Complete Example

```ini
[HomeAssistant]
    # MQTT settings
    [[mqtt]]
        hostname = localhost
        port = 1883
        client_id = weewx_ha
    
    # Station info
    [[station]]
        name = Weather Station
        model = Vantage Pro2
        manufacturer = Davis Instruments
        time_zone = Europe/Prague
    
    # Basic settings
    node_id = weewx
    lang = cs
    
    # Locale overrides
    [[sensors]]
        # Override sensor names
        [[[outTemp]]]
            [[[[metadata]]]]
                name = "Venkovní teplota (vlastní)"
        [[[barometer]]]
            [[[[metadata]]]]
                name = "Tlak vzduchu (QFE)"
    
    [[units]]
        # Customize unit rounding
        [[[degree_C]]]
            value_template = "{{ value | round(0) }}"
        [[[hPa]]]
            value_template = "{{ value | round(1) }}"
    
    [[enums]]
        # Override enum values
        [[[forecast_rule]]]
            0 = "Převážně jasno"
            1 = "Polojasno"
```

## Best Practices

1. **Use sparingly**: Only override what you actually need to customize
2. **Maintain consistency**: Keep naming and formatting consistent with existing locale data
3. **Document changes**: Add comments explaining why you're overriding default values
4. **Test thoroughly**: Verify that overrides work as expected after configuration changes
5. **Prefer locale files**: For extensive localization, consider contributing to locale YAML files instead

## Logging

The extension logs information about applied overrides:

```
INFO: Config overrides set: ['sensors', 'units']
INFO: Applying config overrides for sensors (2 entries)
INFO: Applying config overrides for units (1 entries)
```

Check WeeWX logs to verify that your overrides are being loaded correctly.

