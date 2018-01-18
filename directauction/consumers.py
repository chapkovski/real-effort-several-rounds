from channels import Group
from channels.sessions import channel_session
import random
from .models import Player, Group as OtreeGroup, Constants
import json
import time
import django


def ws_connect(message, group_name):
    Group(group_name).add(message.reply_channel)

# again, not an elegant solution, but once a employer has gotten their offer accepted, this number will be set to 0.
# there are a maximum of 5 employers

# Connected to websocket.receive
def ws_message(message, group_name):
    group_id = group_name[5:]
    print('GROUP ID', group_id)
    print('PLAYER::::', message['text'])
    #the above lines have basically no importance
    jsonmessage = json.loads(message.content['text'])
    #this loads the dictionary probably...
    mygroup = OtreeGroup.objects.get(id=group_id)

    if (jsonmessage['role'] == "employer"):
        # handle the data this way
        print('employer')
        curemployer_id = jsonmessage['id_employer']
        curemployer_id_id_in_group = jsonmessage['id_employer_in_group']
        wage_offer = jsonmessage['wage_offer']
        employers_left_in = jsonmessage['employers_left']
        offer_times = jsonmessage['offer_time']
        offer_times += 1
        now = time.time()
        time_left = round(mygroup.auctionenddate - now)

        if curemployer_id_id_in_group == 1:
            mygroup.standing1 = wage_offer
        if curemployer_id_id_in_group == 2:
            mygroup.standing2 = wage_offer
        if curemployer_id_id_in_group == 3:
            mygroup.standing3 = wage_offer
        if curemployer_id_id_in_group == 4:
            mygroup.standing4 = wage_offer
        if curemployer_id_id_in_group == 5:
            mygroup.standing5 = wage_offer

        mygroup.save()

        textforgroup = json.dumps({
            "from": "employer",
            "employer_id": curemployer_id,
            "employer_id_in_group": curemployer_id_id_in_group,
            "wage_offered": wage_offer,
            "offer_time": offer_times,
            "time_left": time_left,
            "employers_left":employers_left_in

        })
        # Note that this corresponds exactly to the fields defined extra under the groups (in models.py)
        Group(group_name).send({
            "text": textforgroup,
        })

    if (jsonmessage['role'] == "worker"):
    # handle the message this way
        print('worker')
        curworker_id = jsonmessage['id_worker']
        curworker_id_id_in_group = jsonmessage['id_worker_in_group']
        curemployer_id_id_in_group = jsonmessage['id_employer_in_group']
        wage_accepted = jsonmessage['wage_accepted']
        offer_times = jsonmessage['offer_time']
        now = time.time()
        employers_left_in = jsonmessage['num_employers_left']
        employers_left_in -= 1

        # mygroup.auctionenddate = now + Constants.extra_time
        are_you_matched = 0
        time_left = round(mygroup.auctionenddate - now)

        # Are you matched directly?
        if curemployer_id_id_in_group == 1:
            mygroup.matched1 += 1
            if mygroup.matched1 == 1:
                are_you_matched = 1  # yes!
        if curemployer_id_id_in_group == 2:
            mygroup.matched2 += 1
            if mygroup.matched2 == 1:
                are_you_matched = 1  # yes
        if curemployer_id_id_in_group == 3:
            mygroup.matched3 += 1
            if mygroup.matched3 == 1:
                are_you_matched = 1  # yes
        if curemployer_id_id_in_group == 4:
            mygroup.matched4 += 1
            if mygroup.matched4 == 1:
                are_you_matched = 1  # yes
        if curemployer_id_id_in_group == 5:
            mygroup.matched5 += 1
            if mygroup.matched5 == 1:
                are_you_matched = 1  # yes:

        # If you are not matched directly, are there other standing offers identical to the one you have just accepted?
        if are_you_matched == 0:
            if wage_accepted == mygroup.standing1:
                if mygroup.matched1 != 1:
                    curemployer_id_id_in_group = 1 # match them!
                    mygroup.matched1 = 1
                    are_you_matched = 2
            else:
                if wage_accepted == mygroup.standing2:
                    if mygroup.matched2 != 1:
                        curemployer_id_id_in_group = 2 # match them!
                        mygroup.matched2 = 1
                        are_you_matched = 2
                else:
                    if wage_accepted == mygroup.standing3:
                        if mygroup.matched3 != 1:
                            curemployer_id_id_in_group = 3 # match them!
                            mygroup.matched3 = 1
                            are_you_matched = 2
                    else:
                        if wage_accepted == mygroup.standing4:
                            if mygroup.matched4 != 1:
                                curemployer_id_id_in_group = 4 # match them!
                                mygroup.matched4 = 1
                                are_you_matched = 2
                        else:
                            if wage_accepted == standing5:
                                if mygroup.matched5 != 1:
                                    curemployer_id_id_in_group = 5 # match them!
                                    mygroup.matched5 = 1
                                    are_you_matched = 2

        if are_you_matched == 0:
            employers_left_in += 1

        if are_you_matched == 2:
            employers_left_in -= 1

        mygroup.save()

        # do something with those that are not first in the receiving end.
        textforgroup = json.dumps({
            "from": "worker",
            "employer_id_in_group": curemployer_id_id_in_group,
            "worker_id_in_group": curworker_id_id_in_group,
            "wage_accepted": wage_accepted,
            "offer_time": offer_times,
            "time_left": time_left,
            "employers_left": employers_left_in,
            "first": are_you_matched
        })
        Group(group_name).send({
            "text": textforgroup,
        })
    print("SERVER::::", textforgroup)



# Connected to websocket.disconnect
def ws_disconnect(message, group_name):
    Group(group_name).discard(message.reply_channel)
