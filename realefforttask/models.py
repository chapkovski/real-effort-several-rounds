from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range,
)

from django.db import models as djmodels
from django.db.models.signals import post_save
import json
from random import randint

author = 'Philipp Chapkovski, chapkovski@gmail.com'

doc = """
    multi-round real effort task
"""


class Constants(BaseConstants):
    name_in_url = 'realefforttask'
    players_per_group = None
    num_rounds = 1
    task_time = 300
    lb = 30
    ub = 101
    step = 5
    SIZE_CHOICES = ((5, '5X5 matrix'), (10, '10X10 matrix'))


class Subsession(BaseSubsession):
    ...


class Group(BaseGroup):
    ...


class Player(BasePlayer):
    last_correct_answer = models.IntegerField()
    tasks_attempted = models.PositiveIntegerField(initial=0)
    tasks_correct = models.PositiveIntegerField(initial=0)
    easytasks_correct = models.PositiveIntegerField(initial=0)
    difftasks_correct = models.PositiveIntegerField(initial=0)

    def get_unfinished_task(self):
        unfinished_tasks = self.tasks.filter(answer__isnull=True)
        if unfinished_tasks.exists():
            return unfinished_tasks.first().get_dict()
        return False


def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_random_list(max_len):
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


class Task(djmodels.Model):
    player = djmodels.ForeignKey(to=Player, related_name='tasks')
    difficulty = models.IntegerField(doc='difficulty level', null=False)
    body = models.LongStringField(doc='to store task body just in case')
    correct_answer = models.IntegerField(doc='right answer')
    answer = models.IntegerField(doc='user\'s answer', null=True)
    get_feedback = models.BooleanField(doc='whether user chooses to get feedback', null=True)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if not created:
            return
        diff = instance.difficulty
        listx = get_random_list(diff ** 2)
        listy = get_random_list(diff ** 2)
        instance.correct_answer = max(listx) + max(listy)
        listx = slicelist(listx, diff)
        listy = slicelist(listy, diff)
        instance.body = json.dumps({'listx': listx, 'listy': listy})

    def get_dict(self):
        body = json.loads(self.body)
        return {
            "pk": self.pk,
            "mat1": body['listx'],
            "mat2": body['listy'],
            "correct_answer": self.correct_answer,
            "difficulty": self.difficulty,
            'modal_show': False,
        }


post_save.connect(Task.post_create, sender=Task)
