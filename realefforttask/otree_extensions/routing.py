from channels.routing import route, route_class
from .consumers import TaskTracker
from otree.chat.otree_extensions.routing import channel_routing as chat_routing
# NOTE: otree_extensions is part of
# otree-core's private API, which may change at any time.
channel_routing = chat_routing + [
    route_class(TaskTracker, path=TaskTracker.url_pattern),

]