from collections import namedtuple

PollInfo = namedtuple('PollInfo', ['question', 'choices'])
POLL1 = PollInfo(
    question="How awesome is Test-Driven Development?",
    choices=[
        'Very awesome',
        'Quite awesome',
        'Moderately awesome',
    ],
)
POLL2 = PollInfo(
    question="Which workshop treat do you prefer?",
    choices=[
        'Beer',
        'Pizza',
        'The Acquisition of Knowledge',
    ],
)
