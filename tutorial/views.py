from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class Welcome(Page):
    pass


class GeneralInstructions(Page):
    pass


class InstructionsPartI(Page):
    pass


class InstructionsAuction(Page):
    pass


class InstructionsInformation(Page):
    pass


class InstructionsWork(Page):
    pass


class InstructionsPayoff(Page):
    pass


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    Welcome,
    GeneralInstructions,
    InstructionsPartI,
    InstructionsAuction,
    InstructionsInformation,
    InstructionsWork,
    InstructionsPayoff,
    ResultsWaitPage,
    Results
]
