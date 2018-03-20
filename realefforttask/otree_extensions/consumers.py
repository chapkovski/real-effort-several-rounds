from channels import Group
from channels.generic.websockets import WebsocketConsumer
from realefforttask.models import Player, Constants
import json
from random import randint
from realefforttask.forms import ChooseTaskForm
from django.template.loader import render_to_string


def slicelist(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def get_random_list(max_len):
    low_upper_bound = 50
    high_upper_bound = 99
    return [randint(10, randint(low_upper_bound, high_upper_bound)) for i in range(max_len)]


def get_task():
    ...


class TaskTracker(WebsocketConsumer):
    url_pattern = (
        r'^/tasktracker' +
        '/participant/(?P<participant_code>[a-zA-Z0-9_-]+)' +
        '/player/(?P<player>[0-9]+)' +
        '$')

    def clean_kwargs(self, kwargs):
        self.player = self.kwargs['player']
        self.participant = self.kwargs['participant_code']

    def get_task(self):
        string_len = self.task_choice
        listx = get_random_list(self.task_choice ** 2)
        listy = get_random_list(self.task_choice ** 2)
        answer = max(listx) + max(listy)
        listx = slicelist(listx, string_len)
        listy = slicelist(listy, string_len)

        return {
            "mat1": listx,
            "mat2": listy,
            "correct_answer": answer,
            "difficulty": self.task_choice,
        }

    def receive(self, text=None, bytes=None, **kwargs):
        self.clean_kwargs(kwargs)
        jsonmessage = json.loads(text)
        response = dict()
        player = Player.objects.get(participant__code__exact=self.participant, pk=self.player)
        response['tasks_correct'] = player.tasks_correct
        response['tasks_attempted'] = player.tasks_attempted
        # if the request contains form, then we clean it
        if jsonmessage.get('contains_form'):
            raw_data = json.loads(jsonmessage.get('form_data'))
            form_data = dict()
            for i in raw_data:
                form_data[i['name']] = i['value']
            form = ChooseTaskForm(form_data)
            if form.is_valid():
                # if it is clean, return a new task based on info in the form
                self.task_choice = form.cleaned_data['task_choice']
                new_task = self.get_task()
                player.last_correct_answer = new_task['correct_answer']
                player.save()
                response.update(new_task)
                response['modal_show'] = False
            else:
                # if it is not clean, return form with an error
                response['modal_show'] = True
                rendered = render_to_string('includes/choosing_task_form.html', {'form': form})
                response['form'] = rendered
            self.send(response)
            return
        if jsonmessage.get('contains_answer'):
            # if the request contains task answer, we process the answer
            answer = jsonmessage.get('answer')
            self.task_choice = jsonmessage.get('difficulty')
            player.tasks_attempted += 1
            if int(answer) == int(player.last_correct_answer):
                player.tasks_correct += 1
                if self.task_choice == 5:
                    player.easytasks_correct += 1
                else:
                    player.difftasks_correct += 1
            player.save()

        # if the request contains a form request, we add to the answer a new form
        if jsonmessage.get('form_request'):
            response.update(self.get_form())
        self.send(response)

    def get_form(self, data=None):
        form = ChooseTaskForm(data)
        rendered = render_to_string('includes/choosing_task_form.html', {'form': form})
        return {'form': rendered,
                'modal_show': True}

    def connect(self, message, **kwargs):
        self.clean_kwargs(kwargs)
        self.send(self.get_form())

    def send(self, content):
        self.message.reply_channel.send({'text': json.dumps(content)})
