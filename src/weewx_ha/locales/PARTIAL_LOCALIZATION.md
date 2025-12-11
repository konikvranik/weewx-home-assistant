# Partial Localization Example #

This example demonstrates partial localization where only frequently used
sensors are translated, while technical/rarely used sensors remain in English.

## File: sensors_cs.yaml (partial translation) ##

```yaml
# Only translate common sensors - others will use English from sensors.yaml #

# Temperature sensors #
outTemp:
  metadata:
    name: "Venkovní teplota"

inTemp:
  metadata:
    name: "Vnitřní teplota"

# Humidity sensors   #
outHumidity:
  metadata:
    name: "Venkovní vlhkost"

inHumidity:
  metadata:
    name: "Vnitřní vlhkost"

# Wind sensors #
windSpeed:
  metadata:
    name: "Rychlost větru"

windDir:
  metadata:
    name: "Směr větru"

# Rain sensors #
rain:
  metadata:
    name: "Srážky"

rainRate:
  metadata:
    name: "Intenzita srážek"

# Pressure sensors #
pressure:
  metadata:
    name: "Atmosférický tlak"

# That's it! Technical sensors like ET, THSW, cooldeg, growdeg #
# will automatically use English names from sensors.yaml #
```

## Result in Home Assistant ##

**Translated (Czech):**

- Outdoor Temperature → "Venkovní teplota"
- Indoor Temperature → "Vnitřní teplota"
- Wind Speed → "Rychlost větru"
- Rainfall → "Srážky"

**Not translated (English fallback):**

- Evapotranspiration → "Evapotranspiration"
- THSW Index → "Temperature Humidity Sun Wind Index"
- Cooling Degree Days → "Cooling Degree Days"
- Growing Degree Days → "Growing Degree Days"

## Benefits ##

1. **Less work** - Only ~30 sensors to translate instead of ~107
1. **Better UX** - Common sensors in native language, technical terms in English
1. **Easier maintenance** - Smaller files mean fewer merge conflicts
1. **Progressive** - Add more translations as needed
1. **Professional** - Mix of languages is common in technical applications

## File size comparison ##

- Full translation: `sensors_cs.yaml` = ~16KB (all 107 sensors)
- Partial translation: `sensors_cs.yaml` = ~1.5KB (30 common sensors)
- **Savings: 90% smaller file, same functionality for common use cases**
