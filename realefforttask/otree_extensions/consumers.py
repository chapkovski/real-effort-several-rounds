from channels.generic.websockets import WebsocketConsumer
from realefforttask.models import Player, Task
import json
from random import randint
from realefforttask.forms import ChooseTaskForm
from django.template.loader import render_to_string


class TaskTracker(WebsocketConsumer):
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
        task = player.tasks.create(difficulty=self.task_choice)
        return task.get_dict()

    def get_task(self):
        # here we check if a Player has an unanswered=unfinished task. If yes we return it as a dictionary,
        # if not - we create a new one and pass it
        player = self.get_player()
        unfinished_task = player.get_unfinished_task()
        task = unfinished_task.get_dict() if unfinished_task else self.create_task(player)
        task.update({
            'tasks_attempted':player.finished_tasks.count(),
            'tasks_correct':player.num_tasks_correct,
        })
        return task

    def receive(self, text=None, bytes=None, **kwargs):
        self.clean_kwargs(kwargs)
        jsonmessage = json.loads(text)
        response = dict()
        player = self.get_player()

        # if the request contains form, then we clean it
        raw_form_data = jsonmessage.get('form_data')
        if raw_form_data:
            json_data = json.loads(raw_form_data)
            form_data = dict()
            for i in json_data:
                form_data[i['name']] = i['value']
            form = ChooseTaskForm(form_data)
            if form.is_valid():
                # if it is clean, return a new task based on info in the form
                self.task_choice = form.cleaned_data['task_choice']
                response.update(self.get_task())
            else:
                # if it is not clean, return form with an error
                # we also need to take into account if the last time a person requested feedback
                # and provide it if needed

                rendered = render_to_string('includes/choosing_task_form.html', {'form': form})
                response['form'] = rendered
            self.send(response)
            return
        if jsonmessage.get('answer'):
            # if the request contains task answer, we process the answer
            answer = jsonmessage.get('answer')
            task = player.get_unfinished_task()
            if task:
                task.answer = answer
                if jsonmessage.get('feedback_request'):
                    task.get_feedback = True
                task.save()
                response = self.get_form()
        self.send(response)

    def get_form(self, data=None):
        feedback_dict = None
        form = ChooseTaskForm(data)
        dict_to_render = {'form': form}
        player = self.get_player()
        task = player.get_recent_finished_task()
        if task:
            if task.get_feedback == True:
                feedback_dict = {
                    'feedback': task.correct_answer,
                    'user_answer': task.answer,
                    'correct': task.correct_answer == task.answer,
                }

        if feedback_dict:
            dict_to_render.update(feedback_dict)
        rendered = render_to_string('includes/choosing_task_form.html', dict_to_render)
        return {'form': rendered,
                'modal_show': True}

    def connect(self, message, **kwargs):

        self.clean_kwargs(kwargs)
        player = self.get_player()
        # if there is no unfinished tasks to do, then we send them a form to fill so we can
        # form a new task based on their choice
        unfinished_task = player.get_unfinished_task()
        if unfinished_task:
            self.send(unfinished_task.get_dict())
        else:
            self.send(self.get_form())

    def send(self, content):
        self.message.reply_channel.send({'text': json.dumps(content)})
