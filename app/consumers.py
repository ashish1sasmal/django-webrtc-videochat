import json
from typing import Text
from channels.generic.websocket import AsyncWebsocketConsumer
from .service import add_remove_online_user
from asgiref.sync import sync_to_async

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, close_code):
        user_profile = await self.get_user_profile()
        online_users = add_remove_online_user("remove", self.room_group_name)
        for user in online_users:
            await self.channel_layer.group_send(
                user,
                {
                    'type' : 'online_traffic',
                    'action' : 'remove',
                    'user' : user_profile.unique_id
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
        call_from = text_data_json.get("from")
        message = text_data_json.get("message")
        
        user_profile = await self.get_user_profile()
        if msgType == "login":
            print(f"[ {user_profile.unique_id} logged in. ]")
            self.room_group_name = user_profile.unique_id

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            online_users = add_remove_online_user("add", self.room_group_name)
            print(online_users)
            for user in online_users:
                if user!=self.room_group_name:
                    await self.channel_layer.group_send(
                        user,
                        {
                            'type' : 'online_traffic',
                            'action' : 'add',
                            'user' : user_profile.unique_id
                        }
                    )

            await self.channel_layer.group_send(
                to,
                {
                    'type' : 'chatroom_message',
                    'message' : message
                }
            )
        elif msgType == "offer":
            await self.channel_layer.group_send(
                to,
                {
                    'type' : 'offer',
                    'offer' : text_data_json["offer"],
                    'from' : call_from
                }
            )
        
        elif msgType == "answer":
            await self.channel_layer.group_send(
                to,
                {
                    'type' : 'answer',
                    'answer' : text_data_json["answer"]
                }
            )
        
        elif msgType == "candidate":
            await self.channel_layer.group_send(
                to,
                {
                    'type' : 'candidate',
                    'candidate' : text_data_json["candidate"]
                }
            )
        
    async def online_traffic(self, event):
        action = event['action']
        user = event['user']
        await self.send(text_data=json.dumps({
            'type' : 'online_traffic',
            'action' : action,
            'user' : user
        })
        )
    
    async def chatroom_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type' : 'online',
            'message': message
        }))

    async def offer(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'offer',
            'offer': event['offer'],
            'from': event['from']
        }))

    async def answer(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'answer',
            'answer': event['answer']
        }))

    async def candidate(self, event):
        await self.send(text_data=json.dumps({
            'type' : 'candidate',
            'candidate': event['candidate']
        }))