import lib8relind

class Relay:
    def __init__(self, relay_number):
        self.relay_number = relay_number

    def on(self):
        relay = self._remap_relay_number(self.relay_number)
        lib8relind.set(0, relay, 1)

    def off(self):
        relay = self._remap_relay_number(self.relay_number)
        lib8relind.set(0, relay, 0)

    def get(self):
        return lib8relind.get(0, self.relay_number)

    def _remap_relay_number(self, relay):
        if relay == 6:
            return 7
        elif relay == 7:
            return 6
        return relay


def relay_off(fret_relays, except_fret=None):
    for fret in fret_relays:
        if fret != except_fret:
            fret.off()


def detach_relays():
    lib8relind.set_all(0, 0)
