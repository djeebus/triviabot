import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def get_requirements(fn):
    reqs = [str(i.strip())
            for i in open(os.path.join(here, fn))
            if not i.startswith(('#', '-'))]
    return reqs


setup(
    name='triviabot',
    version='0.0.0.0',
    description='Triviabot for various platforms',
    url='htp://github.com/djeebus/triviabot',
    author='Joe Lombrozo',
    author_email='joe@djeebus.net',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'triviabot=triviabot.cli:cli',
        ],
    },

    install_requires=get_requirements('requirements.txt'),
)
