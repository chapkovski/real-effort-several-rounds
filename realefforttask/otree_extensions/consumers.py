from channels.generic.websockets import JsonWebsocketConsumer
from realefforttask.models import Player, Task
import json


# TODO: delete fol lines

# from realefforttask.forms import ChooseTaskForm
# from django.template.loader import render_to_string


class TaskTracker(JsonWebsocketConsumer):
    url_pattern = (
        r'^/tasktracker' +
        '/participant/(?P<participant_code>[a-zA-Z0-9_-]+)' +
        '/player/(?P<player_id>[0-9]+)' +
        '$')

    def clean_kwargs(self, kwargs):
        self.player_id = self.kwargs['player_id']
        self.participant_code = self.kwargs['participant_code']
        self.player = self.get_player()

    def get_player(self):
        return Player.objects.get(participant__code__exact=self.participant_code, pk=self.player_id)

    def receive(self, text=None, bytes=None, **kwargs):
        self.clean_kwargs(kwargs)
        response = dict()
        answer = text.get('answer')
        if answer:
            # if the request contains task answer, we process the answer
            task = self.player.get_unfinished_task()
            if task:
                task.answer = answer
                task.save()
        response.update(self.player.get_task())
        self.send(response)

    def connect(self, message, **kwargs):
        self.clean_kwargs(kwargs)

