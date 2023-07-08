from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    influencers = models.ManyToManyField('User', related_name="subscribers", blank=True)


class Post(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField('User', related_name="liked_posts", blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.liked.all().count()
        }