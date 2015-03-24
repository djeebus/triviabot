import boto
import boto.sqs.message
import logging
import triviabot.clients
import ujson

from time import sleep

logger = logging.getLogger(__name__)


class SlackClient(triviabot.clients.BaseClient):
    djeebus_user_id = 'U02B0RXUC'

    ROOT_API_URL = 'https://slack.com/api/'

    def __init__(self, slack_api_token,
                 aws_access_key_id, aws_secret_access_key,
                 sqs_queue_name):
        super(SlackClient, self).__init__()
        self._common_params = {
            'token': slack_api_token,
        }

        sqs_client = boto.connect_sqs(
            aws_access_key_id,
            aws_secret_access_key,
        )
        self._sqs = sqs_client.get_queue(
            sqs_queue_name)
        self._sqs.message_class = boto.sqs.message.RawMessage

    def validate_response(self, response):
        json_body = response.json()
        if json_body['ok'] not in (1, True):
            raise Exception("not ok! %s" % json_body)

        return json_body

    def send_message(self, channel, username, message):
        payload = {
            'channel': channel,
            'username': username,
            'text': message,
        }

        self._make_request('GET', 'chat.postMessage', params=payload)

    def get_sqs_messages(self):
        while True:
            logger.debug('listening for sqs messages ... ')
            message = self._sqs.read(wait_time_seconds=10)
            if not message:
                sleep(.01)
                continue

            logger.debug('got an sqs message!')

            payload = ujson.loads(message.get_body())
            if payload['user_id'] == 'USLACKBOT':
                continue

            if payload['user_name'] == 'slackbot':
                continue

            try:
                yield payload
            finally:
                self._sqs.delete_message(message)
