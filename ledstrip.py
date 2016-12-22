from repeated_timer import RepeatedTimer
from neopixel import Adafruit_NeoPixel, Color

class LEDStrip:
    options = {
        "led_count": 16,
        "led_pin": 12,
        "led_freq_hz": 800000,
        "led_dma": 5,
        "led_invert": False,
    }

    initial_state = {
        "current": {
            "color": {"r": 0, "g": 0, "b": 0},
            "brightness": 0
        },
        "wanted": {
             "color": {"r": 0, "g": 0, "b": 0},
             "delay": 0.005,
             "steps": 1,
             "brightness": 50
        },
        "blink": {
            "states": [],
            "delay": 2,
            "current_index": 0
        },
    }

    state = None

    timers = {
        "update": None,
        "blink": None
    }

    strip = None

    def __init__(self, options = {}):
        self.timers["update"] = RepeatedTimer(self.initial_state["wanted"]["delay"], self._update)
        self.timers["blink"] = RepeatedTimer(self.initial_state["blink"]["delay"], self._blink)
        self.options.update(options)
        self.strip = Adafruit_NeoPixel(
            self.options["led_count"],
            self.options["led_pin"],
            self.options["led_freq_hz"],
            self.options["led_dma"],
            self.options["led_invert"],
            self.initial_state["wanted"]["brightness"],
            )
        self.strip.begin()
        self.state = self.initial_state.copy()

    def set(self, args = None):
        if (self.timers["blink"].is_running()):
            self.timers["blink"].stop()
        self._set(args["state"])
        return True

    def blink(self, args = None):
        if (self.timers["blink"].is_running()):
            self.timers["blink"].stop()
        self.state["blink"] = self.initial_state["blink"].copy()
        self.state["blink"].update(args)
        self.timers["blink"].set_interval(self.state["blink"]["delay"])
        self.timers["blink"].start()
        return True

    def _set(self, args):
        self.state["wanted"].update(args)
        self.timers["update"].set_interval(self.state["wanted"]["delay"])
        if (not self.timers["update"].is_running()):
            self.timers["update"].start()

    def _blink(self):
        num_states = len(self.state["blink"]["states"])
        if num_states == 0:
            self.timers["blink"].stop()
            return
        self.state["blink"]["current_index"] = self.state["blink"]["current_index"] + 1
        if (self.state["blink"]["current_index"] >= num_states):
            self.state["blink"]["current_index"] = 0
        self._set(self.state["blink"]["states"][self.state["blink"]["current_index"]])


    def _update(self):
        update_needed = False
        current = self.state["current"]
        wanted = self.state["wanted"]
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

        if current["brightness"] != wanted["brightness"]:
            # Update needed
            update_needed = True
            if current["brightness"] < wanted["brightness"]:
                current["brightness"] = current["brightness"] + wanted["steps"]
                if current["brightness"] > wanted["brightness"]:
                    current["brightness"] = wanted["brightness"]
            if current["brightness"] > wanted["brightness"]:
                current["brightness"] = current["brightness"] - wanted["steps"]
                if current["brightness"] < wanted["brightness"]:
                    current["brightness"] = wanted["brightness"]

        if update_needed:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(
                    current["color"]["r"],
                    current["color"]["g"],
                    current["color"]["b"]
                    ))
            self.strip.setBrightness(current["brightness"])
            self.strip.show()
        else:
            self.timers["update"].stop()
