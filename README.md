# Galactic Unicorn scripts

For networked examples you need to make a `secrets.py` script which looks like:
```
WIFI_SSID = "..."
WIFI_PASSWORD = "..." 
```

`clock.py` is a clock with a slightly modified version of the rainbow example as the background.
The time synchronises using NTP on start and at 5am every day.  This sets to UTC, you can adjust the hour with the volume up/down buttons.
