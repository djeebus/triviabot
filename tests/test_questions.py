def test_get_questions_sample():
    from triviabot.questions import _parse_resource

    questions = _parse_resource('questions/questions.test')

    assert len(questions) == 2

    question_1 = questions[0]
    assert question_1.category == 'General'
    assert question_1.question == 'What is the literal translation of the Latin word \'video\'?'
    assert question_1.answer == 'i see'

    question_2 = questions[1]
    assert question_2.category == 'General'
    assert question_2.question == 'Who is the supreme head of the Church Of England?'
    assert question_2.answer == 'queen elizabeth ii'


def test_answer_regexp_matches():
    from triviabot.questions import TriviaItem
    item = TriviaItem({
        'Question': 'this is a question',
        'Regexp': '(6(th)? (of )?June,? 1944|June 6(th)?,? 1944)',
        'Answer': 'june',
    })

    assert item.check_answer('6th of June, 1944') is True


def test_answer_regexp_does_not_match_but_answer_does():
    from triviabot.questions import TriviaItem
    item = TriviaItem({
        'Question': 'this is a question',
        'Regexp': '(6(th)? (of )?June,? 1944|June 6(th)?,? 1944)',
        'Answer': 'june',
    })

    assert item.check_answer('June') is True
