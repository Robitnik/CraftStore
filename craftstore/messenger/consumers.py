from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from modules.websocket import utils as ws_utils
from . import utils
from . import models
from asgiref.sync import sync_to_async
from user.utils import get_user_by_token



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_token = self.scope['url_route']['kwargs']['user_token']
        user = await sync_to_async(get_user_by_token)(user_token)
        if not user:
            await self.close(code=3000, reason="Unknown user")
            return  # Повертаємо після закриття з'єднання
        self.user = user
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.group_name = f"chat_{self.chat_slug}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")
        if not message_type:
            await self.send(text_data=json.dumps({"status": False, "error": "Не вказано тип повідомлення"}))
            return

        if message_type == "send_message":
            await self.handle_send_message(data)
        elif message_type == "delete_message":
            await self.handle_delete_message(data)
        elif message_type == "edit_message":
            await self.handle_edit_message(data)
        else:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідомий тип повідомлення"}))

    async def handle_send_message(self, data):
        message = data.get("message")
        images = data.get("images", [])
        if not message or not message.strip():
            await self.send(text_data=json.dumps({"status": False, "error": "Повідомлення пусте"}))
            return
        message_obj = await utils.async_add_message(
            chat_slug=self.chat_slug, user=self.user, message=message, images=images
        )
        message_data = await sync_to_async(message_obj.as_dict)()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "send_message",  # викликає метод send_message
                "message": message_data
            }
        )

    async def handle_delete_message(self, data):
        message_id = data.get("message_id")
        if not message_id:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення"}))
            return
    
        qs = await sync_to_async(models.Message.objects.filter)(pk=message_id)
        exists = await sync_to_async(qs.exists)()
        if not exists:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення"}))
            return
    
        message_obj = await sync_to_async(qs.first)()
        # Отримуємо атрибут sender через sync_to_async
        sender = await sync_to_async(lambda: message_obj.sender)()
        if sender != self.user:
            await self.send(text_data=json.dumps({
                "status": False,
                "error": "Ви не можете видалити це повідомлення"
            }))
            return
    
        await utils.async_delete_message(message_obj.pk)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "delete_message",
                "message_id": message_id
            }
        )

    async def handle_edit_message(self, data):
        message_id = data.get("message_id")
        new_message = data.get("message")
        if not message_id or not new_message:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення або нове повідомлення"}))
            return
        qs = await sync_to_async(models.Message.objects.filter)(pk=message_id)
        exists = await sync_to_async(qs.exists)()
        if not exists:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення"}))
            return
        message_obj = await sync_to_async(qs.first)()
        if message_obj.sender != self.user:
            await self.send(text_data=json.dumps({"status": False, "error": "Ви не можете редагувати це повідомлення"}))
            return
        new_message_obj = await utils.edit_message(message_obj.pk, new_message)
        message_data = await sync_to_async(new_message_obj.as_dict)()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "edit_message",
                "message_id": message_id,
                "message": message_data
            }
        )

    # Обробники групових подій
    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "send_message",
            "message": event.get("message")
        }))

    async def delete_message(self, event):
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "delete_message",
            "message_id": event.get("message_id")
        }))

    async def edit_message(self, event):
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "edit_message",
            "message_id": event.get("message_id"),
            "message": event.get("message")
        }))
