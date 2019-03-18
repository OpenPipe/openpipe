"""
Produce the system clock time at regular intervals
"""
from time import time, sleep
from openpipe.engine import PluginRuntime


class Plugin(PluginRuntime):

    optional_params = """
    interval:   0   # Pause time between insertions, 0 means forever
    max_count:  1     # Max number of item insertions
    """

    def on_input(self, item):
        interval = self.params['interval']
        interval = time2seconds(interval)
        count = self.params['max_count']
        repeat_forever = (count == 0)

        while repeat_forever or count > 0:
            if interval:
                sleep(interval)
            self.put(time())
            if not repeat_forever:
                count -= 1


def time2seconds(value):
    SECONDS_MAP = {'s': 1, 'm': 60, 'h': 60*60, 'd': 24 * 60 * 60}
    number = ''
    unit = 's'
    if isinstance(value, int):
        return value
    for char in value:
        if char.isdigit():
            number += char
        else:
            unit = char
            break
    multiplier = SECONDS_MAP[unit]
    return int(number) * multiplier
