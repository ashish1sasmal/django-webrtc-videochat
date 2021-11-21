import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        msgType = text_data_json.get("type")
        to = text_data_json.get("to")
        call_from = text_data_json.get("from")
        message = text_data_json.get("message")
        if msgType == "login":
            my_username = text_data_json['to']
            print(f"[ {my_username} logged in. ]")
            self.username = my_username
            self.room_group_name = self.username

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
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
    
    async def chatroom_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type' : 'message',
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