from channels.generic.websockets import  JsonWebsocketConsumer
from realefforttask.models import Player, Task
import json
# TODO: delete fol lines

# from realefforttask.forms import ChooseTaskForm
# from django.template.loader import render_to_string


class TaskTracker(JsonWebsocketConsumer):
    url_pattern = (
        r'^/tasktracker' +
        '/participant/(?P<participant_code>[a-zA-Z0-9_-]+)' +
        '/player/(?P<player>[0-9]+)' +
        '$')

    def clean_kwargs(self, kwargs):
        self.player = self.kwargs['player']
        self.participant = self.kwargs['participant_code']

    def get_player(self):
        return Player.objects.get(participant__code__exact=self.participant, pk=self.player)

    def create_task(self, player):
        task = player.tasks.create()
        return task.get_dict()

    def get_task(self):
        # here we check if a Player has an unanswered=unfinished task. If yes we return it as a dictionary,
        # if not - we create a new one and pass it
        player = self.get_player()
        unfinished_task = player.get_unfinished_task()
        task = unfinished_task.get_dict() if unfinished_task else self.create_task(player)
        task.update({
            'tasks_attempted': player.finished_tasks.count(),
            'tasks_correct': player.num_tasks_correct,
        })
        return task

    def receive(self, text=None, bytes=None, **kwargs):
        self.clean_kwargs(kwargs)
        # todo: check if we need that later

        response = dict()
        player = self.get_player()
        answer = text.get('answer')
        if answer:
            # if the request contains task answer, we process the answer
            task = player.get_unfinished_task()
            if task:
                task.answer = answer
                task.save()
        response.update(self.get_task())
        self.send(response)

    def connect(self, message, **kwargs):
        self.clean_kwargs(kwargs)
        self.send(self.get_task())


