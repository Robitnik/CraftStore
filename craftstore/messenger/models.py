from django.db import models
from modules.generators.strings import generate_random_string

class Chat(models.Model):
    members = models.ManyToManyField("user.User", related_name="chats", blank=True)
    masseges = models.ManyToManyField("Massage", related_name="chat", blank=True)
    slug = models.SlugField(default=generate_random_string(50, 100), unique=True)
    date = models.DateTimeField(auto_now=True)
    
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class Massage(models.Model):
    massege = models.TextField()
    sender = models.ForeignKey("user.User", related_name="chat_masseges", on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    send_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)