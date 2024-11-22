from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio



class WSConsumer(AsyncWebsocketConsumer):
    messages = ["first"]
    last_message = None
    async def connect(self):
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.chat_group_slug = f"chat_{self.chat_slug}"

        await self.accept()

        # Запуск фонового відправлення повідомлень
        asyncio.create_task(self.send_messages_periodically())

    async def disconnect(self, close_code):
        # Видалити з групи
        await self.channel_layer.group_discard(
            self.chat_group_slug,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        self.messages.append(message)


    async def chat_message(self, event):
        # Отримання повідомлення з групи
        message = event["message"]

        # Відправка клієнту
        await self.send(text_data=json.dumps({
            "message": message
        }))

    async def send_messages_periodically(self):
        # Періодична відправка повідомлень
        while True:
            if self.messages:
                if self.last_message != self.messages[-1]:
                    await self.send(json.dumps({"message": self.messages[-1]}))
                    self.last_message = self.messages[-1]
            await asyncio.sleep(2)  # Асинхронний сон
