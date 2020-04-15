from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ModelForm

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=400)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
        )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True, null=True
        )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(
        Post, null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="comments"
        )
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE
        )
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
        )
