from repeated_timer import RepeatedTimer
from neopixel import Adafruit_NeoPixel, Color

class LEDStrip:
    options = {
        "led_count": 16,
        "led_pin": 12,
        "led_freq_hz": 800000,
        "led_dma": 5,
        "led_brightness": 50,
        "led_invert": False,
    }

    states = {
        "current": {
            "color": {"r": 0, "g": 0, "b": 0}
        },
        "wanted": {
             "color": {"r": 0, "g": 0, "b": 0},
             "steps" : 5,
        },
        "blink": {
            "colors": [],
            "delay": 1,
            "current_index": 0
        },
    }

    timers = {
        "update": None,
        "blink": None
    }

    strip = None

    def __init__(self, options = {}):
        self.timers["update"] = RepeatedTimer(0.005, self._update)
        self.timers["blink"] = RepeatedTimer(1, self._blink)
        self.options.update(options)
        self.strip = Adafruit_NeoPixel(
            options["led_count"],
            options["led_pin"],
            options["led_freq_hz"],
            options["led_dma"],
            options["led_invert"],
            options["led_brightness"]
            )
        strip.begin()

    def set(self, args = None):
        print "-- LED SET"
        self.states["blink"]["colors"] = []
        self._set(args["color"])
        return True

    def blink(self, args = None):
        print "-- LED BLINK"
        self.states["blink"]["colors"] = args["colors"]
        if (not self.timers["blink"].is_running()):
            self.timers["blink"].start()
        return True

    def _set(self, color):
        print "Setting RGB values"
        self.states["wanted"]["color"] = color
        if (not self.timers["update"].is_running()):
            self.timers["update"].start()

    def _blink(self):
        num_colors = len(self.states["blink"]["colors"])
        if num_colors == 0:
            self.timers["blink"].stop()
            return
        self.states["blink"]["current_index"] = self.states["blink"]["current_index"] + 1
        if (self.states["blink"]["current_index"] >= num_colors):
            self.states["blink"]["current_index"] = 0
        self._set(self.states["blink"]["colors"][self.states["blink"]["current_index"]])

    def _update(self):
        update_needed = False
        current = self.states["current"]
        wanted = self.states["wanted"]
        for c in ["r","g","b"]:
            if current["color"][c] != wanted["color"][c]:
                # Update needed
                update_needed = True
                if current["color"][c] < wanted["color"][c]:
                    current["color"][c] = current["color"][c] + wanted["steps"]
                    if current["color"][c] > wanted["color"][c]:
                        current["color"][c] = wanted["color"][c]

                if current["color"][c] > wanted["color"][c]:
                    current["color"][c] = current["color"][c] - wanted["steps"]
                    if current["color"][c] < wanted["color"][c]:
                        current["color"][c] = wanted["color"][c]

        if update_needed:
            for i in range(self.strip.numPixels()):
                strip.setPixelColor(i, Color(
                    current["color"]["r"],
                    current["color"]["g"],
                    current["color"]["b"]
                    ))
            strip.show()
        else:
            self.timers["update"].stop()
