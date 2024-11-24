from . import models
from asgiref.sync import sync_to_async


def get_lasted_massege(chat_slug) -> dict:
    chat = models.Chat.objects.get(slug=chat_slug)
    last_massege = chat.masseges.filter(read=False).last()
    return last_massege.as_dict()

def get_lasted_masseges(chat_slug) -> list[dict]:
    chat = models.Chat.objects.get(slug=chat_slug)
    if chat.masseges.filter(read=False).exists():
        last_masseges = chat.masseges.filter(read=False)
        return [m.as_dict() for m in last_masseges]
    return None


@sync_to_async
def sync_add_message(chat_slug, user, message) -> models.Massage:
    message_obj = models.Massage(massege=message, sender=user)
    message_obj.save()    
    chat = models.Chat.objects.get(slug=chat_slug)
    chat.masseges.add(message_obj)
    return message_obj


async def async_add_message(chat_slug, user, message) -> models.Massage:
    return await sync_add_message(chat_slug, user, message)
