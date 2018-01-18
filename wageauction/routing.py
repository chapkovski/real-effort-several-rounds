from channels.routing import route
from .consumers import ws_message, ws_connect, ws_disconnect, work_connect, work_disconnect, work_message
from otree.channels.routing import channel_routing
from channels.routing import include, route_class

auction_path = r'^/(?P<group_name>\w+)$'
work_path = r'^/(?P<worker_code>\w+)/(?P<player_pk>\w+)$'
wageauction_routing = [route("websocket.connect",
                             ws_connect, path=auction_path),
                       route("websocket.receive",
                             ws_message, path=auction_path),
                       route("websocket.disconnect",
                             ws_disconnect, path=auction_path), ]

workpage_routing = [route("websocket.connect",
                          work_connect, path=work_path),
                    route("websocket.receive",
                          work_message, path=work_path),
                    route("websocket.disconnect",
                          work_disconnect, path=work_path), ]

channel_routing += [
    include(wageauction_routing, path=r"^/wageauction"),
    include(workpage_routing, path=r"^/workpage"),
]
