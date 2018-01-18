from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, Group, Subsession, JobContract
import time
from random import randint
from channels import Group as ChannelGroup
from otree.models_concrete import CompletedGroupWaitPage


class EmployerPage(Page):
    def is_displayed(self):
        return self.player.role() == 'employer' and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


class WorkerPage(Page):
    def is_displayed(self):
        return self.player.role() == 'worker' and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


class ActiveWorkerPage(Page):
    def is_displayed(self):
        return self.player.role() == 'worker' and self.player.active_worker and self.extra_is_displayed()

    def extra_is_displayed(self):
        return True


class WP(WaitPage):
    def after_all_players_arrive(self):
        now = time.time()
        self.group.auctionenddate = now + Constants.starting_time


class Auction(EmployerPage):
    def extra_is_displayed(self):
        closed_contract = self.player.contract.filter(accepted=True).exists()
        return not any([self.group.day_over, closed_contract])

    def vars_for_template(self):
        active_contracts = JobContract.objects.filter(accepted=False, employer__group=self.group)
        return {'time_left': self.group.time_left(),
                'active_contracts': active_contracts,
                }

    def before_next_page(self):
        closed_contract = self.player.contract.filter(accepted=True)
        if closed_contract.exists():
            self.player.wage_offer = closed_contract.first().amount


class Accept(WorkerPage):
    def extra_is_displayed(self):
        closed_contract = self.player.work_to_do.filter(accepted=True).exists()
        return not any([self.group.day_over, closed_contract])

    def vars_for_template(self):
        active_contracts = JobContract.objects.filter(accepted=False, employer__group=self.group).values('pk', 'amount')
        return {'time_left': self.group.time_left(),
                'active_contracts': active_contracts}

    def before_next_page(self):
        closed_contract = self.player.work_to_do.filter(accepted=True).exists()
        self.player.active_worker = closed_contract


class AfterAuctionDecision(EmployerPage):
    form_model = models.Player
    form_fields = ["wage_adjusted"]

    def extra_is_displayed(self):
        closed_contract = self.player.contract.filter(accepted=True).exists()
        return closed_contract

    def before_next_page(self):
        closed_contract = self.player.contract.get(accepted=True)
        closed_contract.amount_updated = self.player.wage_adjusted
        closed_contract.save()
        closed_contract.worker.job_to_do_updated = True


class AuctionResultsEmployer(EmployerPage):
    ...


class ActiveWorkerWPBeforeStart(WaitPage):
    def is_displayed(self):
        self.subsession.wp_to_delete_completion = self._index_in_pages
        if self.player.role() == 'employer':
            closed_contract = self.player.contract.filter(accepted=True)
            if closed_contract.exists():
                worker_pk = self.player.contract.get().worker.participant.pk
                self.send_completion_message(set([worker_pk]))

        return (not self.player.job_to_do_updated) and self.player.active_worker


class AuctionResultsWorker(ActiveWorkerPage):
    def vars_for_template(self):
        completion = CompletedGroupWaitPage.objects.filter(
            page_index=self.subsession.wp_to_delete_completion,
            id_in_subsession=self.group.id_in_subsession,
            session=self.session,
        )
        if completion.exists():
            completion.delete()
        closed_contract = self.player.work_to_do.get()
        worker_wage_offer = closed_contract.amount
        worker_wage_adjusted = closed_contract.amount_updated
        return {'worker_wage_offer': worker_wage_offer,
                'worker_wage_adjusted': worker_wage_adjusted, }


class Start(ActiveWorkerPage):
    ...


class WorkPage(ActiveWorkerPage):
    timer_text = 'Time left to complete this section:'

    timeout_seconds = 30000

    def before_next_page(self):
        ...


class WaitP(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    ...


page_sequence = [
    WP,
    Auction, Accept,
    AfterAuctionDecision,
    AuctionResultsEmployer,
    ActiveWorkerWPBeforeStart,
    AuctionResultsWorker,
    Start,
    WorkPage,
    WaitP,
    Results
]
