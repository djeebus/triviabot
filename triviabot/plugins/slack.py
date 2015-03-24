import logging

from time import sleep
from triviabot.clients.slack_client import SlackClient
from triviabot.plugins import BasePlugin
from threading import Thread

logger = logging.getLogger(__name__)


class SlackPlugin(BasePlugin):
    name = 'slack'

    def __init__(self, config):
        super(SlackPlugin, self).__init__(config)

        self._name = config['name']
        self._token = config['api_token']
        self._channel = config['channel']

        sqs_config = config['sqs']
        self._slack_client = SlackClient(
            self._token, **sqs_config)

    def run(self):
        threads = [
            ('slack: trivia-messages', self._listen_for_trivia_bot),
            ('slack: slack-chats', self._listen_for_slack),
        ]
        for name, func in threads:
            t = Thread(target=func)
            t.daemon = True
            t.name = name
            t.start()

        while True:
            sleep(.1)

    def _listen_for_slack(self):
        logger.info('listening for slack messages ... ')
        for message in self._slack_client.get_sqs_messages():
            logger.info('got a slack message! %s', message)
            if message['channel_name'] != self._channel[1:]:
                continue

            self._send_answer('slack',
                              message['user_id'],
                              message['text'])

    def _listen_for_trivia_bot(self):
        logger.info('listening for trivia bot messages ... ')
        for message in self.messages_queue.receive():
            logger.info('received a trivia bot message! %s', message)
            if not message:
                continue

            self._slack_client.send_message(
                self._channel,
                self._name,
                message,
            )
