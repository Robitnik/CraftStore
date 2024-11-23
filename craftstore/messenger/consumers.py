from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from modules.websocket import utils as ws_utils
from . import utils
from asgiref.sync import sync_to_async


class WSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.parsed_scope = ws_utils.parse_scope(self.scope)
        await self.accept()
        # Запуск фонового відправлення повідомлень
        asyncio.create_task(self.send_messages_periodically())

    async def disconnect(self, close_code):
        # Видалити з групи
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

    async def chat_message(self, event):
        message = event["message"]
        # Відправка клієнту
        await self.send(text_data=json.dumps({
            "message": message
        }))

    async def send_messages_periodically(self):
        while True:
            lasted_message = await sync_to_async(utils.get_lasted_massege)(self.chat_slug)
            if lasted_message:
                await self.send(json.dumps({"message": str(lasted_message)}))
            await asyncio.sleep(2)  # Асинхронний сон
