from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, Group, Subsession
# from datetime import datetime
import time
import datetime
from random import randint


class WP(WaitPage):

    def after_all_players_arrive(self):
        now = time.time()
        self.group.auctionenddate = now + Constants.starting_time


class TaxOutcome(Page):
    timeout_seconds = 10


class Auction(Page):
    def is_displayed(self):
        return self.player.role() == 'employer'

    def vars_for_template(self):
        return {'time_left': self.group.time_left()}

    form_model = models.Player
    form_fields = ['wage_offer', 'partner_id']


class Accept(Page):
    def is_displayed(self):
        return self.player.role() == 'worker'

    def vars_for_template(self):
        return {'time_left': self.group.time_left()}

    form_model = models.Player
    form_fields = ['wage_offer', 'partner_id']


class WPage(WaitPage):

    title_text = "Results of the auction"
    body_text = "Your decision has been recorded... we are waiting for the other participants."

    def after_all_players_arrive(self):
        dicta = []
        new_matrix = []
        for p in self.subsession.get_players():
            dicta.append([p.partner_id, p])
        for q in self.subsession.get_players():
            if q.partner_id == 0:
                new_matrix.append(q)
        newer_matrix = [new_matrix]
        for p in self.subsession.get_players():
            for i in range(1, Constants.num_employers + 1):
                if p.partner_id == i:
                    newer_matrix.append([p, dicta[i-1][1]])
        self.subsession.set_group_matrix(newer_matrix)


class AuctionResultsEmployer(Page):
    def is_displayed(self):
        if self.player.partner_id > 0 and self.player.role() == 'employer':
            return True


class AuctionResultsWorker(Page):
    def is_displayed(self):
        if self.player.partner_id > 0 and self.player.role() == 'worker':
            return True


class Start(Page):
    def is_displayed(self):
        if self.player.partner_id > 0 and self.player.role() == 'worker':
            return True


class WaitWorkers(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        for worker in self.session.get_participants():
            worker.vars['expiry_timestamp'] = time.time() + models.Constants.task_time


class WorkPage(Page):
    timer_text = 'Time left to complete this section:'

    timeout_submission = {'tasks_attempted': True,
                          'tasks_correct': True}

    def get_timeout_seconds(self):
        return self.participant.vars['expiry_timestamp'] - time.time()

    def is_displayed(self):
        if self.player.partner_id > 0 and self.player.role() == 'worker':
            if self.participant.vars['expiry_timestamp'] - time.time() > 3:
                return True
            else:
                return False
        else:
            return False

    form_model = models.Player
    form_fields = ["tasks_attempted", "tasks_correct"]

    def vars_for_template(self):
        x = randint(50, 100)
        y = randint(50, 100)
        listx = [randint(10, x)]
        listy = [randint(10, y)]
        for i in range(0, 99):
            listx.append(randint(10, x))
            listy.append(randint(10, y))
        answer = max(listx) + max(listy)

        return {
            "mat1": listx,
            "mat2": listy,
            "correct_answer": answer,
        }

    def before_next_page(self):
        # this is silly but worth trying out
        if self.timeout_happened:
            post_dict = self.request.POST.dict()
            my_value_attempted = post_dict.get('tasks_attempted')
            my_value_correct = post_dict.get('tasks_correct')
            self.player.tasks_attempted = int(my_value_attempted)
            self.player.tasks_correct = int(my_value_correct)
        # WOW THIS WORKS! :) - ONLY THE PAGE ERRORS ALL THE TIME.


class Work1(WorkPage):
    pass


class Work2(WorkPage):
    pass


class Work3(WorkPage):
    pass


class Work4(WorkPage):
    pass


class Work5(WorkPage):
    pass


class Work6(WorkPage):
    pass


class Work7(WorkPage):
    pass


class Work8(WorkPage):
    pass


class Work9(WorkPage):
    pass


class Work10(WorkPage):
    pass


class WaitP(WaitPage):
    def after_all_players_arrive(self):
        for p in self.subsession.get_players():
            if p.role() == 'employer':
                for partner in p.get_others_in_group():
                    if p.partner_id > 0:
                        p.tasks_correct = partner.tasks_correct
                        p.tasks_attempted = partner.tasks_attempted

        self.group.set_payoffs()

        for p in self.subsession.get_players():
            if p.partner_id > 0:
                for partner in p.get_others_in_group():
                    p.partner_payoff = partner.payoff


class Results(Page):
    pass


page_sequence = [
    WP, TaxOutcome,
    Auction, Accept,
    WPage,
    AuctionResultsEmployer, AuctionResultsWorker,
    Start, WaitWorkers,
    Work1, Work2, Work3, Work4, Work5, Work6, Work7, Work8, Work9, Work10,
    WaitP,
    Results
]
