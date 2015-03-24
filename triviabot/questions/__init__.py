import logging
import pkg_resources
import re

logger = logging.getLogger(__name__)


def get_questions():
    resource_names = pkg_resources.resource_listdir(
        'triviabot', 'questions/')

    questions = []
    for resource_name in resource_names:
        if not resource_name.endswith('.en'):
            continue

        some_questions = _parse_resource('questions/' + resource_name)
        logger.info('found %s questions in %s', len(some_questions), resource_name)
        questions += some_questions
    return questions


def _parse_resource(resource_name):
    resource = pkg_resources.resource_string('triviabot', resource_name)

    questions = []
    temp_question = {}
    for line in resource.split('\n'):
        line = line.strip()
        if not line:
            if temp_question:
                q = TriviaItem(temp_question)
                questions.append(q)
                temp_question = {}
            continue

        if line.startswith('#'):
            continue

        parts = line.split(':', 1)
        if len(parts) != 2:
            logger.warn('Missing key and value: %s' % line)
            continue

        key, value = parts
        key = key.strip()
        value = value.strip()

        if key in temp_question:
            logger.warn('"%s" defined more than once' % key)
            continue

        temp_question[key] = value
    return questions


class TriviaItem(object):
    def __init__(self, question_info):
        self.question = question_info['Question']
        self.answer = question_info['Answer'].lower()
        self.category = question_info.get('Category')
        self.regexp = question_info.get('Regexp')
        self.level = question_info.get('Level')

    def check_answer(self, attempted_answer):
        if self.regexp:
            if re.match(self.regexp, attempted_answer):
                return True

        if attempted_answer.lower() == self.answer:
            return True

        return False

    def format_question(self):
        text = ''
        if self.category:
            text = '%s: ' % self.category

        text += self.question
        if self.level:
            text = ' [%s]' % self.level
        return text
