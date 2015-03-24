import logging
import random

from datetime import datetime
from threading import Timer, Thread
from time import time, sleep

from triviabot import MESSAGES_QUEUE_NAME, ANSWER_QUEUE_NAME
from triviabot.clients.queue_client import PubSubClient
from triviabot.questions import get_questions

logger = logging.getLogger(__name__)


class Daemon(object):
    name = 'daemon'

    def __init__(self, config):
        self._seconds = config['time_to_answer']
        self._points = config['max_points']

        self._timer = None
        self._waiting_for_answer = False

        kwargs = config['redis']
        self._answer_queue = PubSubClient(queue_name=ANSWER_QUEUE_NAME, client_name='daemon-answer-queue', **kwargs)
        self._output_queue = PubSubClient(queue_name=MESSAGES_QUEUE_NAME, client_name='daemon-output-queue', **kwargs)

        self._current_question = None
        self._correct_answer = None
        self._questions = get_questions()

        self._answer_thread = Thread(target=self._watch_answers)
        self._answer_thread.daemon = True
        self._answer_thread.name = 'daemon: answers'
        self._answer_thread.start()

    def run(self):
        while True:
            self._ask_question()

    def _get_random_question(self):
        return random.choice(self._questions)

    def _send_question(self, question_info):
        text = question_info.format_question()
        logger.info('sending question: %s' % text)
        self._output_queue.publish(text)

    def _announce_correct_answer(self, answer_info):
        logger.info('announcing a correct answer')
        self._output_queue.publish(
            '{user} got the right answer in {time} '
            'seconds for {points} points, and now has {score} points!'.format(
                user=answer_info['user']['name'],
                time=int(answer_info['duration']),
                points=answer_info['points'],
                score=answer_info['user']['score'],
            )
        )

    def _announce_no_correct_answer(self, trivia_item):
        """
        :type trivia_item: triviabot.questions.TriviaItem
        """
        logger.info('announcing no correct answer')
        self._output_queue.publish(
            'The correct answer was "{answer}"'.format(
                answer=trivia_item.answer,
            )
        )

    def _get_user_info(self, token_type, token_value):
        return {
            'user_id': 123,
            'score': 100,
            'name': 'test_user',
            'last_activity': datetime.now().isoformat(),
            'tokens': {
                token_type: token_value
            }
        }

    def _start_timer(self):
        self._correct_answer = None
        self._waiting_for_answer = True
        self._duration = time()

        self._timer = Timer(self._seconds, self._times_up)
        self._timer.daemon = True
        self._timer.start()

    def _times_up(self):
        self._waiting_for_answer = False

    def _cancel_timer(self):
        self._waiting_for_answer = False
        self._duration = time() - self._duration
        self._timer.cancel()

    def _watch_answers(self):
        for message in self._answer_queue.receive():
            self._process_answer(message)

    def _process_answer(self, answer_info):
        logger.info('processing answer attempt')
        if not self._waiting_for_answer or self._correct_answer is not None:
            return

        if answer_info['text'].lower() != self._current_question['Answer'].lower():
            return

        user_info = self._get_user_info(answer_info['token_type'], answer_info['token_value'])
        if not user_info:
            return

        answer_info['user'] = user_info
        self._correct_answer = answer_info
        self._cancel_timer()

    def _ask_question(self):
        question_info = self._get_random_question()
        self._send_question(question_info)
        self._current_question = question_info

        self._start_timer()
        while self._waiting_for_answer:
            sleep(1)

        if not self._correct_answer:
            self._announce_no_correct_answer(question_info)
            return

        answer_info = self._correct_answer
        answer_info['duration'] = int(self._duration)
        answer_info['points'] = int((1 - (self._duration / self._seconds)) * self._points)
        self._announce_correct_answer(answer_info)

        # clean up
        self._correct_answer = None
        self._current_question = None
