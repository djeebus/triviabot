import logging
import redis
import ujson

logger = logging.getLogger(__name__)


class PubSubClient(object):
    def __init__(self, host, port, db, queue_name, client_name):
        self._client = redis.Redis(host, port, db)
        self._client.client_setname(client_name)
        self._queue_name = queue_name

    def publish(self, message):
        logger.debug('publishing message to "%s": %s', self._queue_name, message)
        self._client.publish(self._queue_name, ujson.dumps(message))

    def receive(self):
        p = self._client.pubsub()
        logger.info('subscribing to "%s"' % self._queue_name)
        p.subscribe(self._queue_name)
        for message in p.listen():
            logger.debug('receiving message: %s' % message)
            if message['type'] != 'message':
                continue

            logger.debug('received message: %s', message)
            yield ujson.loads(message['data'])
        logger.warn('no more messages :(')
