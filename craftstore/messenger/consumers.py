from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from . import utils
from . import models
from asgiref.sync import sync_to_async
from user.utils import get_user_by_token


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Обробляє подію встановлення WebSocket з'єднання.
        - Отримує токен користувача з URL параметрів.
        - Аутентифікує користувача за допомогою функції get_user_by_token.
        - Якщо користувача не знайдено, з'єднання не приймається.
        - Якщо користувач знайдений, визначається чат (chat_slug) та група, до якої користувача додають.
        - З'єднання приймається.
        """
        # Отримання токену користувача з параметрів URL
        user_token = self.scope['url_route']['kwargs']['user_token']
        # Асинхронний виклик функції аутентифікації користувача
        user = await sync_to_async(get_user_by_token)(user_token)
        if not user:
            # Якщо користувача не знайдено, припиняємо обробку з'єднання
            return  # Повертаємо після закриття з'єднання (додатковий return не потрібен)
        self.user = user  # Збереження аутентифікованого користувача в атрибуті об'єкта
        # Отримання ідентифікатора чату (slug) з URL параметрів
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        # Формування імені групи для каналу (групування чатів)
        self.group_name = f"chat_{self.chat_slug}"
        # Додавання поточного каналу до групи (для розсилки повідомлень всім учасникам чату)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        # Прийняття WebSocket з'єднання
        await self.accept()

    async def disconnect(self, close_code):
        """
        Обробляє розрив WebSocket з'єднання.
        - При відсутності з'єднання з групою (якщо атрибут не встановлено), нічого не робиться.
        - Якщо з'єднання було додано до групи, воно видаляється.
        """
        if hasattr(self, 'group_name'):
            # Видалення поточного каналу з групи
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Обробляє отримані дані з WebSocket.
        - Дані декодуються з JSON.
        - На основі поля "type" вибирається відповідний обробник події.
        - Якщо тип повідомлення невідомий або відсутній, клієнту надсилається повідомлення про помилку.
        """
        data = json.loads(text_data)
        message_type = data.get("type")
        if not message_type:
            # Якщо тип повідомлення не заданий, відправляємо відповідь з помилкою
            await self.send(text_data=json.dumps({"status": False, "error": "Не вказано тип повідомлення"}))
            return

        # Виклик відповідного обробника залежно від типу повідомлення
        if message_type == "send_message":
            await self.handle_send_message(data)
        elif message_type == "delete_message":
            await self.handle_delete_message(data)
        elif message_type == "edit_message":
            await self.handle_edit_message(data)
        elif message_type == "typing_message":
            await self.handle_typing_message()
        else:
            # Якщо тип повідомлення не розпізнаний, повертаємо помилку
            await self.send(text_data=json.dumps({"status": False, "error": "Невідомий тип повідомлення"}))

    async def handle_send_message(self, data):
        """
        Обробник події відправлення повідомлення.
        - Перевіряє, чи повідомлення не пусте.
        - Додає повідомлення до бази даних за допомогою утиліти async_add_message.
        - Конвертує об'єкт повідомлення в словник та надсилає його всім учасникам групи.
        """
        message = data.get("message")
        images = data.get("images", [])
        if not message or not message.strip():
            # Якщо повідомлення порожнє, відправляємо відповідь з помилкою
            await self.send(text_data=json.dumps({"status": False, "error": "Повідомлення пусте"}))
            return
        # Асинхронне додавання повідомлення до бази даних
        message_obj = await utils.async_add_message(
            chat_slug=self.chat_slug, user=self.user, message=message, images=images
        )
        # Перетворення об'єкта повідомлення в словник (для передачі даних)
        message_data = await sync_to_async(message_obj.as_dict)()
        # Розсилка повідомлення всім учасникам групи через канал
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "send_message",  # викликає метод send_message у споживачів
                "message": message_data
            }
        )

    async def handle_delete_message(self, data):
        """
        Обробник події видалення повідомлення.
        - Перевіряє наявність message_id в даних.
        - Перевіряє, чи існує повідомлення з заданим id.
        - Перевіряє, чи є поточний користувач власником повідомлення.
        - Якщо всі перевірки пройдено, викликає видалення повідомлення та розсилає повідомлення про видалення.
        """
        message_id = data.get("message_id")
        if not message_id:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення"}))
            return
    
        # Отримання запиту для фільтрації повідомлення за його id
        qs = await sync_to_async(models.Message.objects.filter)(pk=message_id)
        exists = await sync_to_async(qs.exists)()
        if not exists:
            # Якщо повідомлення не знайдено, повертаємо помилку
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення"}))
            return
    
        # Отримання першого повідомлення з запиту
        message_obj = await sync_to_async(qs.first)()
        # Отримання відправника повідомлення
        sender = await sync_to_async(lambda: message_obj.sender)()
        if sender != self.user:
            # Якщо поточний користувач не є автором повідомлення, повертаємо помилку
            await self.send(text_data=json.dumps({
                "status": False,
                "error": "Ви не можете видалити це повідомлення"
            }))
            return
    
        # Виклик асинхронної функції для видалення повідомлення з бази даних
        await utils.async_delete_message(message_obj.pk)
        # Розсилка події видалення повідомлення всім учасникам групи
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "delete_message",
                "message_id": message_id
            }
        )

    async def handle_edit_message(self, data):
        """
        Обробник події редагування повідомлення.
        - Перевіряє наявність message_id та нового тексту повідомлення.
        - Перевіряє, чи існує повідомлення з заданим id.
        - Перевіряє, чи є поточний користувач автором повідомлення.
        - Якщо перевірки успішні, редагує повідомлення через утиліту edit_message,
          конвертує результат в словник і розсилає оновлене повідомлення учасникам групи.
        """
        message_id = data.get("message_id")
        new_message = data.get("message")
        if not message_id or not new_message:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення або нове повідомлення"}))
            return
        # Фільтруємо повідомлення за id
        qs = await sync_to_async(models.Message.objects.filter)(pk=message_id)
        exists = await sync_to_async(qs.exists)()
        if not exists:
            await self.send(text_data=json.dumps({"status": False, "error": "Невідоме Повідомлення"}))
            return
        # Отримання повідомлення з бази даних
        message_obj = await sync_to_async(qs.first)()
        sender = await sync_to_async(lambda: message_obj.sender)()
        if sender != self.user:
            # Якщо користувач не є автором, повертаємо помилку
            await self.send(text_data=json.dumps({"status": False, "error": "Ви не можете редагувати це повідомлення"}))
            return
        # Викликаємо утиліту для редагування повідомлення
        new_message_obj = await sync_to_async(utils.sync_edit_message)(message_obj.pk, new_message)
        # Перетворення оновленого об'єкта повідомлення в словник
        message_data = await sync_to_async(new_message_obj.as_dict)()
        # Розсилка події редагування повідомлення всім учасникам групи
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "edit_message",
                "message_id": message_id,
                "message": message_data
            }
        )
    async def handle_typing_message(self):
        await self.channel_layer.group_send(
            self.group_name,
            {
                "status": True,
                "type": "typing_message",
                "username": self.user.username,                
            }
        )
    async def typing_message(self, event):
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "typing_message",
            "username": event.get("username")
        }))

    # Обробники групових подій, які надсилають повідомлення клієнту
    async def send_message(self, event):
        """
        Отримує подію "send_message" від групи і надсилає її клієнту.
        """
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "send_message",
            "message": event.get("message")
        }))

    async def delete_message(self, event):
        """
        Отримує подію "delete_message" від групи і надсилає її клієнту.
        """
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "delete_message",
            "message_id": event.get("message_id")
        }))

    async def edit_message(self, event):
        """
        Отримує подію "edit_message" від групи і надсилає її клієнту.
        """
        await self.send(text_data=json.dumps({
            "status": event.get("status", True),
            "type": "edit_message",
            "message_id": event.get("message_id"),
            "message": event.get("message")
        }))
