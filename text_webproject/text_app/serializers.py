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
        url = f'{protocol}://{domain}/snippet/detail/{obj.id}'
        return url

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        print("---------", validated_data.get('tag_id'))
        print("00000000000000", instance.tag_id)
        instance.tag_id = validated_data.get('tag_id', instance.tag_id)
        instance.save()
        return instance


class SnippetListSerializer(serializers.ModelSerializer):
    tag_id = TagSerializer()
    snippet_detail_link = serializers.SerializerMethodField()

    class Meta:
        model = Snippet
        fields = '__all__'

    def get_snippet_detail_link(self, obj):
        request = self.context.get('request')
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        url = f'{protocol}://{domain}/snippet/detail/{obj.id}'
        return url
