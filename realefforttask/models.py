from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range,
)

from django.db import models as djmodels
from django.db.models.signals import post_save
from django.db.models import F
import json
from random import randint
from django.core import serializers

author = 'Philipp Chapkovski, chapkovski@gmail.com'

doc = """
    multi-round real effort task
"""


class Constants(BaseConstants):
    name_in_url = 'realefforttask'
    players_per_group = None
    num_rounds = 1
    task_time = 30000
    lb = 30
    ub = 101
    step = 5
    EASY = 5
    HARD = 10
    SIZE_CHOICES = ((EASY, '5X5 matrix'), (HARD, '10X10 matrix'))


class Subsession(BaseSubsession):
    ...


class Group(BaseGroup):
    ...


class Player(BasePlayer):
    last_correct_answer = models.IntegerField()
    tasks_dump = models.LongStringField(doc='to store all tasks with answers, diff level and feedback')

    def get_unfinished_task(self):
        unfinished_tasks = self.tasks.filter(answer__isnull=True)
        if unfinished_tasks.exists():
            return unfinished_tasks.first()
        return False

    @property
    def finished_tasks(self):
        return self.tasks.filter(answer__isnull=False)

    def get_recent_finished_task(self):
        is_task = self.finished_tasks.exists()
        if is_task:
            return self.finished_tasks.latest('updated_at')

    def get_correct_tasks(self):
        return self.tasks.filter(correct_answer=F('answer'))

    @property
    def num_tasks_correct(self):
        return self.get_correct_tasks().count()

    @property
    def num_easy_tasks_correct(self):
        # not the best way to hardcode difficulty level like that so
        # in the future it's better to use somethign from constants
        return self.get_correct_tasks().filter(difficulty=Constants.EASY).count()

    @property
    def num_hard_tasks_correct(self):
        return self.get_correct_tasks().filter(difficulty=Constants.HARD).count()

    def dump_tasks(self):
        # this method will request all completed tasks and dump them to player's field
        # just for the convenience and following analysis.
        # theoretically we don't need to store 'updated_at' field because it is already sorted by this field
        # but just in case
        q = self.finished_tasks
        data = list(q.values('difficulty',
                             'correct_answer',
                             'answer',
                             'get_feedback',
                             'updated_at'))
        # the following loop we need to avoid issues with converting dateteime to string
        for d in data:
            d['updated_at'] = str(d['updated_at'])
        self.tasks_dump = json.dumps(data)


def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_random_list(max_len):
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


class Task(djmodels.Model):
    class Meta:
        ordering = ['updated_at']

    player = djmodels.ForeignKey(to=Player, related_name='tasks')
    difficulty = models.IntegerField(doc='difficulty level', initial=Constants.HARD)
    body = models.LongStringField(doc='to store task body just in case')
    correct_answer = models.IntegerField(doc='right answer')
    answer = models.IntegerField(doc='user\'s answer', null=True)
    created_at = djmodels.DateTimeField(auto_now_add=True)
    updated_at = djmodels.DateTimeField(auto_now=True)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        # this presumably is considered the safest method to update newly created items
        # so we catch the new task, we add there the body based on difficulty level,
        # and the correct answer.
        if not created:
            return
        diff = instance.difficulty
        listx = get_random_list(diff ** 2)
        listy = get_random_list(diff ** 2)
        instance.correct_answer = max(listx) + max(listy)
        listx = slicelist(listx, diff)
        listy = slicelist(listy, diff)
        instance.body = json.dumps({'listx': listx, 'listy': listy})
        instance.save()

    def get_dict(self):
        # this method is needed to push the task to the page via consumers
        body = json.loads(self.body)
        return {
            "mat1": body['listx'],
            "mat2": body['listy'],
            "correct_answer": self.correct_answer,
        }


post_save.connect(Task.post_create, sender=Task)
