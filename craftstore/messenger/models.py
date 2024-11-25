from django.db import models
from modules.generators.strings import generate_random_string
from django.db.models import Max
from modules.serializers import get_serializer_for_model


class Chat(models.Model):
    members = models.ManyToManyField("user.User", related_name="chats", blank=True)
    masseges = models.ManyToManyField("Massage", related_name="chat", blank=True)
    slug = models.SlugField(default=generate_random_string(50, 100), unique=True, max_length=200)
    date = models.DateTimeField(auto_now=True)

    def get_last_message_date(self):
        return self.masseges.aggregate(last_date=Max('send_date'))['last_date']

    def get_last_message(self):
        return self.masseges.last().as_dict() if self.masseges.exists() else None

    def as_dict(self, fields=None):
        fields = fields or ['slug', 'id', 'date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data['members'] = [member.as_mini_dict() for member in self.members.all()]
        data['last_message'] = self.get_last_message()
        data['unread_message_count'] = self.masseges.filter(read=False).count()
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['slug', 'id', 'date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Massage(models.Model):
    massege = models.TextField()
    sender = models.ForeignKey("user.User", related_name="chat_masseges", on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    send_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)

    def is_edit(self) -> bool:
        return self.edit_date if self.send_date != self.edit_date else False

    def as_dict(self, fields=None):
        fields = fields or ['massege', 'read', 'send_date', 'edit_date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        data['sender'] = self.sender.as_mini_dict()
        data['date'] = {"send": str(self.send_date), "edit": str(self.edit_date)}
        return data.data

    def as_mini_dict(self, fields=None):
        fields = fields or ['massege', 'read', 'send_date']
        data = get_serializer_for_model(queryset=self, model=type(self), fields=fields, many=False)
        return data.data
