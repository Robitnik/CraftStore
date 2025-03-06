from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from modules.websocket import utils as ws_utils
from . import utils
from asgiref.sync import sync_to_async
from user.utils import get_user_by_token


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_token = self.scope['url_route']['kwargs']['user_token']
        user = await sync_to_async(get_user_by_token)(user_token)
        if not user:
            await self.close(code=3000, reason="Unknown user")
            return  # додано повернення після закриття з'єднання
        self.user = user
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.group_name = f"chat_{self.chat_slug}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Обробка повідомлень користувача
        data = json.loads(text_data)
        message = data.get("message")
        if not message or not message.strip():
            await self.send(text_data=json.dumps({"status": False, "error": "Повідомлення пусте"}))
            return
        message_obj = await utils.async_add_message(chat_slug=self.chat_slug, user=self.user, message=message)
        message_data = await sync_to_async(message_obj.as_dict)()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "chat_message",
                "message": message_data
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
