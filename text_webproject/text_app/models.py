from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


# Create your models here.

class UserList(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class TagList(admin.ModelAdmin):
    list_display = ('id', 'title')


class Snippet(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class SnippetList(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'created_at', 'updated_at', 'user_id', 'tag_id')
