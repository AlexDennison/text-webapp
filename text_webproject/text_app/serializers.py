from rest_framework import serializers

from .models import Snippet, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SnippetSerializer(serializers.ModelSerializer):
    tag_id = TagSerializer()
    snippet_detail_link = serializers.SerializerMethodField()

    class Meta:
        model = Snippet
        fields = '__all__'

    def get_snippet_detail_link(self, obj):
        request = self.context.get('request')
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        return f'{protocol}://{domain}/snippet/detail/{obj.id}'
        