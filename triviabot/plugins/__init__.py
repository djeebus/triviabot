from triviabot.clients.queue_client import PubSubClient
from triviabot import ANSWER_QUEUE_NAME, MESSAGES_QUEUE_NAME


class BasePlugin(object):
    def __init__(self, config):
        self.config = config
        self.command_queue = None
        self._answer_queue = None
        self._messages_queue = None

    @property
    def answer_queue(self):
        if self._answer_queue is None:
            self._answer_queue = PubSubClient(
                queue_name=ANSWER_QUEUE_NAME, client_name='%s-answer-queue' % self.name, **self.config['redis'])

        return self._answer_queue

    @property
    def messages_queue(self):
        if self._messages_queue is None:
            self._messages_queue = PubSubClient(
                queue_name=MESSAGES_QUEUE_NAME, client_name='%s-messages-quue' % self.name, **self.config['redis'])
        return self._messages_queue

    def start(self):
        self.run()

    def run(self):
        raise NotImplementedError()

    def _send_answer(self, token_type, token_value, answer_text):
        self.answer_queue.publish({
            'text': answer_text,
            'token_type': token_type,
            'token_value': token_value,
        })
