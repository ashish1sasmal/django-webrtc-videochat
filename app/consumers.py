import json
from typing import Text
from channels.generic.websocket import AsyncWebsocketConsumer
from .service import add_remove_online_user, updateLocationList
from asgiref.sync import sync_to_async

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        user_profile = await self.get_user_profile()
        location_sharing_users = updateLocationList("remove", user_profile.unique_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type' : 'chatroom_message',
                'to' : "all",
                'from' : {"id":user_profile.unique_id, "name": self.scope['user'].username},
                'event' : 'online_traffic',
                'message' : "remove"
            }
        )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    @sync_to_async
    def get_user_profile(self):
        user = self.scope['user']
        return user.user_profile

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        msgType = text_data_json.get("type")
        to = text_data_json.get("to")
        from_ = text_data_json.get("from")

        # user_profile = await self.get_user_profile()
        if msgType == "login":
            print(f"[ {from_['id']} logged in. ]")
            online_users = add_remove_online_user("add", from_["id"])
            print(online_users)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'chatroom_message',
                    'message' : "add",
                    'to' : "all",
                    'from' : from_,
                    "event" : "online_traffic",
                }
            )
        elif msgType == "offer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'offer',
                    'offer' : text_data_json["offer"],
                    'to' : to,
                    'from' : from_
                }
            )
        
        elif msgType == "answer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'answer',
                    'answer' : text_data_json["answer"],
                    'to' : to,
                    'from' : from_
                }
            )
        
        elif msgType == "candidate":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'candidate',
                    'candidate' : text_data_json["candidate"],
                    'to' : to,
                    'from' : from_
                }
            )
        
        elif msgType == "joiner":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'joiner',
                    "to" : "all",
                    "from" : from_
                }
            )
        
        elif msgType == "success_join":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'success_join',
                    "to" : to,
                    "from" : from_
                }
            )
        elif msgType == "chat_message":
             await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'chatroom_message',
                    'message' : text_data_json["message"],
                    'to' : from_,
                    'from' : from_,
                    "event" : "chat_message"
                }
            )
    
    async def chatroom_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type' : event["event"],
            'message': message,
            'to': event["to"],
            'from': event['from']
        }))

    async def offer(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'offer',
            'offer': event['offer'],
            'to': event["to"],
            'from': event['from']
        }))

    async def answer(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'answer',
            'answer': event['answer'],
            'to': event["to"],
            'from': event['from']
        }))

    async def candidate(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'candidate',
            'candidate': event['candidate'],
            'to': event["to"],
            'from': event['from']
        }))
    
    async def joiner(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'joiner',
            'to': event["to"],
            'from': event['from']
        }))

    async def success_join(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'success_join',
            'to': event["to"],
            'from': event['from']
        }))