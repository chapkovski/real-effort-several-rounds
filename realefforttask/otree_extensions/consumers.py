from channels import Group
from channels.generic.websockets import WebsocketConsumer
from realefforttask.models import Player, Constants
import json
from random import randint


def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_random_list():
    max_len = 100
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


def get_task():
    string_len = 10
    listx = get_random_list()
    listy = get_random_list()
    answer = max(listx) + max(listy)
    listx = slicelist(listx, string_len)
    listy = slicelist(listy, string_len)

    return {
        "mat1": listx,
        "mat2": listy,
        "correct_answer": answer,
    }


class TaskTracker(WebsocketConsumer):
    url_pattern = (
        r'^/tasktracker' +
        '/participant/(?P<participant_code>[a-zA-Z0-9_-]+)' +
        '/player/(?P<player>[0-9]+)' +
        '$')

    def clean_kwargs(self, kwargs):
        self.player = self.kwargs['player']
        self.participant = self.kwargs['participant_code']

    def receive(self, text=None, bytes=None, **kwargs):
        self.clean_kwargs(kwargs)

        jsonmessage = json.loads(text)
        answer = jsonmessage.get('answer')
        player = Player.objects.get(participant__code__exact=self.participant, pk=self.player)
        player.tasks_attempted += 1
        if int(answer) == int(player.last_correct_answer):
            player.tasks_correct += 1
        new_task = get_task()
        new_task['tasks_correct'] = player.tasks_correct
        new_task['tasks_attempted'] = player.tasks_attempted
        player.last_correct_answer = new_task['correct_answer']
        player.save()
        self.send(new_task)

    def connect(self, message, **kwargs):
        self.clean_kwargs(kwargs)

        new_task = get_task()
        player = Player.objects.get(participant__code__exact=self.participant, pk=self.player)
        player.last_correct_answer = new_task['correct_answer']
        player.save()
        self.send(new_task)

    def send(self, content):
        self.message.reply_channel.send({'text': json.dumps(content)})
