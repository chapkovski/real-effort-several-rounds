from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class WorkPage(Page):
    timer_text = 'Time left to complete this round:'
    timeout_seconds = Constants.task_time

    def before_next_page(self):
        self.player.dump_tasks()

page_sequence = [
    WorkPage,
]
