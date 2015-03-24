from triviabot.plugins import BasePlugin


class WebPlugin(BasePlugin):
    name = 'web'

    @property
    def host(self):
        return self.config['host']

    @property
    def port(self):
        return self.config['port']

    def run(self):
        pass
