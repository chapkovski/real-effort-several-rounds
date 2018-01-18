from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage





class WorkPage(Page):
    timer_text = 'Time left to complete this round:'

    timeout_seconds = 60






page_sequence = [
    WorkPage,
]
