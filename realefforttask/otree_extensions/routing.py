from channels.routing import route, route_class
from .consumers import TaskTracker

# NOTE: otree_extensions is part of
# otree-core's private API, which may change at any time.
channel_routing = [
    route_class(TaskTracker, path=TaskTracker.url_pattern),

]