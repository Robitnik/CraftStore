from django.db import models
from modules.generators.strings import generate_random_string
from django.db.models import Max
from modules.serializers import get_serializer_for_model


class Chat(models.Model):
    members = models.ManyToManyField("user.User", related_name="chats", blank=True)
    slug = models.SlugField(default=generate_random_string, unique=True, max_length=200)
    date = models.DateTimeField(auto_now=True)

    def get_last_message_date(self):
        return self.messages.aggregate(last_date=Max('send_date'))['last_date']

    def get_last_message(self):
        return self.messages.last().as_dict() if self.messages.exists() else None

    def get_last_messages_as_dict(self) -> list[dict]:
        unread_messages = self.messages.filter(read=False)
        if unread_messages.exists():
            return [m.as_dict() for m in unread_messages]
        return None

    def get_unread_message_count(self):
        return self.messages.filter(read=False).count()


    def mark_as_read(self):
        self.messages.filter(read=False).update(read=True)    

    def as_dict(self, fields=None):
        fields = fields or ['slug', 'id', 'date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data.data['members'] = [member.as_mini_dict() for member in self.members.all()]
        data.data['last_message'] = self.get_last_message()
        data.data['unread_message_count'] = self.messages.filter(read=False).count()
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['slug', 'id', 'date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def get_chat_user(self, user):
        """
        Повертає іншого користувача в чаті, який не є переданим як аргумент.
        Якщо чат містить більше ніж двох учасників, повертається перший знайдений.
        Якщо інший користувач не знайдено, повертається None.
        """
        other = self.members.exclude(id=user.id).first()
        return other

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.pk}" + generate_random_string()
        super().save(*args, **kwargs)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    images = models.ManyToManyField("cdn.Image", related_name="messages", blank=True)
    sender = models.ForeignKey("user.User", related_name="chat_messages", on_delete=models.SET_NULL, blank=True, null=True)
    read = models.BooleanField(default=False, db_index=True)
    send_date = models.DateTimeField(auto_now_add=True, db_index=True)
    edit_date = models.DateTimeField(auto_now=True)

    def is_edit(self) -> bool:
        return self.send_date != self.edit_date

    def as_dict(self, fields=None):
        fields = fields or ['message', 'read', 'send_date', 'edit_date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = dict(data.data)
        data['sender'] = self.sender.as_mini_dict() if self.sender else None
        data['date'] = {"send": str(self.send_date), "edit": str(self.edit_date)}
        return data

    def as_mini_dict(self, fields=None):
        fields = fields or ['message', 'read', 'send_date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data = dict(data.data)
        return data