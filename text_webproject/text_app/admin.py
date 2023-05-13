from django.contrib import admin
# from django.contrib.auth.models import User
from text_app.models import Tag, TagList, Snippet, SnippetList


# Register your models here.
admin.site.register(Tag, TagList)
admin.site.register(Snippet, SnippetList)
