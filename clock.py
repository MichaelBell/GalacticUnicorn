import time
import math
import network
import ntptime
import machine
from secrets import WIFI_SSID, WIFI_PASSWORD
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

galactic = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

def get_time():
    # Start connection
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connect success or failure
    max_wait = 20
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if max_wait > 0:
        print("Connected")

        try:
            ntptime.settime()
            print("Time set")
        except:
            pass

    wlan.disconnect()
    wlan.active(False)

@micropython.native  # noqa: F821
def from_hv(h, v):
    i = math.floor(h * 6.0)
    f = h * 6.0 - i
    v *= 255.0
    p = 0.0
    q = v * (1.0 - f)
    t = v * f

    i = int(i) % 6
    if i == 0:
        return int(v), int(t), int(p)
    if i == 1:
        return int(q), int(v), int(p)
    if i == 2:
        return int(p), int(v), int(t)
    if i == 3:
        return int(p), int(q), int(v)
    if i == 4:
        return int(t), int(p), int(v)
    if i == 5:
        return int(v), int(p), int(q)


@micropython.native  # noqa: F821
def draw_rainbow():
    phase_percent = (time.ticks_ms() % 60000) * 0.000104719755
    for x in range(width):
        for y in range(height):
            v = ((math.sin((x + y) / stripe_width + phase_percent) + 1.5) / 6.0)
            colour = from_hv(((x - 1) % width) / width, v)

            graphics.set_pen(graphics.create_pen(*colour))
            graphics.pixel(x, y)

stripe_width = 3.0

clear_pen = graphics.create_pen(0, 0, 0)
clock_pen = graphics.create_pen(255, 255, 255)

graphics.set_font("bitmap8")

light = 20
old_day = 0
old_hour = 4
utc_offset = 0

up_button = machine.Pin(GalacticUnicorn.SWITCH_VOLUME_UP, machine.Pin.IN, machine.Pin.PULL_UP)
down_button = machine.Pin(GalacticUnicorn.SWITCH_VOLUME_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)

def adjust_utc_offset(pin):
    global utc_offset
    if pin == up_button:
        utc_offset += 1
    if pin == down_button:
        utc_offset -= 1

up_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=adjust_utc_offset)
down_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=adjust_utc_offset)

while True:
    year, month, day, hour, minute, second, _, _ = time.localtime()
    
    hour = (hour + utc_offset) % 24

    light = light * 0.9 + galactic.light() * 0.1
    if light < 10:
        graphics.set_pen(clear_pen)
        graphics.clear()
        galactic.set_brightness(0.04)
    else:
        galactic.set_brightness(0.014 * light)
        draw_rainbow()
    
    hr = "{:02}".format(hour)
    hr_width = graphics.measure_text(hr, 1)
    
    graphics.set_pen(clock_pen)
    graphics.text("{:02}:{:02}".format(hour, minute), (width // 2) - hr_width, 2, scale=1)
    
    galactic.update(graphics)
    time.sleep(0.01)

    # Get time at start (after first draw), and at 5am every day
    if old_hour != hour:
        if old_hour == 4 and old_day != day:
            get_time()
            old_day = day
        
        old_hour = hour
