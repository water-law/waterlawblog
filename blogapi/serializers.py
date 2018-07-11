from django.contrib.auth.models import Group
from rest_framework import serializers
from blog.models import User, Post
from comment.models import Comment


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number', )


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PostSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data['author'] = request.user
        return super(PostSerializer, self).create(validated_data)

    class Meta:
        model = Post
        fields = '__all__'


class PublishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'tags')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('name', 'content', 'post')






