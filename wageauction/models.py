from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
from django import forms
import time
import datetime

from django.db import models as djmodels

author = 'Essi Kujansuu, EUI, essi.kujansuu@eui.eu, adapting work of Philipp Chapkovski, UZH, chapkovski@gmail.com'

doc = """
Adaptation of Fehr et al. 1993 auction.
"""


class Constants(BaseConstants):
    name_in_url = 'wageauction'
    players_per_group = 5
    num_rounds = 2
    starting_time = 15000
    num_employers = 2
    num_workers = players_per_group - num_employers
    assert num_workers > num_employers, 'NUMBER OF EMPLOYERS SHOULD EXCEED THE NUMBER OF WORKERS IN THE MARKET'
    task_time = 300
    lb = 30
    ub = 101
    step = 5
    offers = list(range(lb, ub, step))


class Subsession(BaseSubsession):
    wp_to_delete_completion=models.IntegerField()
    def creating_session(self):
        tax_outcome = random.randint(1, 3)
        for p in self.get_players():
            p.tax_outcome = tax_outcome


class Group(BaseGroup):
    auctionenddate = models.FloatField()
    day_over = models.BooleanField()

    def time_left(self):
        now = time.time()
        time_left = self.auctionenddate - now
        time_left = round(time_left) if time_left > 0 else 0
        return time_left

    def set_payoffs(self):
        # TO DO: the payoff function should be re-written completely based on new JobCOntract model info - Philipp
        for person in self.get_players():
            if person.role() == 'employer':
                if person.partner_id == 0:
                    person.payoff = 0
                else:
                    if person.tax_outcome == 2:
                        person.payoff = 40 - (
                            person.wage_offer + person.wage_adjustment) + 0.8 * 20 * person.tasks_correct
                    else:
                        person.payoff = 40 - (person.wage_offer + person.wage_adjustment) + 20 * person.tasks_correct
            if person.role() == 'worker':
                if person.partner_id == 0:
                    person.payoff = 20
                else:
                    if person.tax_outcome == 3:
                        person.payoff = 0.8 * (person.wage_offer + person.wage_adjustment)
                    else:
                        person.payoff = (person.wage_offer + person.wage_adjustment)


class Player(BasePlayer):
    wage_offer = models.IntegerField()
    tax_outcome = models.PositiveIntegerField()
    wage_adjustment = models.IntegerField()
    wage_adjusted=models.IntegerField()
    last_correct_answer=models.IntegerField()
    tasks_attempted = models.PositiveIntegerField(initial=0)
    tasks_correct = models.PositiveIntegerField(initial=0)
    partner_payoff = models.CurrencyField()
    active_worker=models.BooleanField()
    job_to_do_updated=models.BooleanField(initial=False)

    def role(self):
        if self.id_in_group <= Constants.num_employers:
            return 'employer'
        if self.id_in_group > Constants.num_employers:
            return 'worker'


class Request(djmodels.Model):
    employer = djmodels.ForeignKey(Player, related_name='requests')
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobContract(djmodels.Model):
    employer = djmodels.ForeignKey(Player, related_name='contract', unique=True)
    worker = djmodels.ForeignKey(Player, blank=True, null=True, related_name='work_to_do')
    amount = models.IntegerField()
    accepted = models.BooleanField()
    amount_updated = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
