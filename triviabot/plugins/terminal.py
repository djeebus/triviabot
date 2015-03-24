from triviabot.plugins import BasePlugin


class TerminalPlugin(BasePlugin):
    name = 'terminal'

    def __init__(self, config):
        self._config = config
        super(TerminalPlugin, self).__init__()

    def run(self):
        pass
