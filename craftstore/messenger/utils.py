from . import models
from django.db.models import Count
from asgiref.sync import sync_to_async



def get_chat_between_users(user1, user2):
    """
    Повертає чат, який містить лише двох користувачів: user1 та user2.
    Якщо такий чат існує, повертає його, інакше повертає None.
    """
    chat = models.Chat.objects.filter(members=user1).filter(members=user2).first()
    return chat


@sync_to_async
def sync_add_message(chat_slug, user, message) -> models.Message:
    chat = models.Chat.objects.get(slug=chat_slug)
    message_obj = models.Message(message=message, sender=user, chat=chat)
    message_obj.save()
    return message_obj


async def async_add_message(chat_slug, user, message) -> models.Message:
    return await sync_add_message(chat_slug, user, message)
