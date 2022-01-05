from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ValidationError
from track.models import Track
from tag.serializers import TagSerializer
from user.serializers import UserSerializer, SimpleUserSerializer
from reaction.serializers import LikeSerializer, RepostSerializer
from reaction.models import Like, Repost
from soundcloud.utils import assign_object_perms, get_presigned_url, MediaUploadMixin
from django.contrib.contenttypes.models import ContentType

class TrackSerializer(serializers.ModelSerializer):

    artist = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    genre = TagSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'like_count',
            'repost_count',
            'comment_count',
            'description',
            'created_at',
            'count',
            'genre',
            'tags',
            'is_private',
        )
        extra_kwargs = {
            'permalink': {
                'max_length': 255,
                'min_length': 3,
            },
        }
        read_only_fields = (
            'created_at',
            'count',
        )

        # Since 'artist' is read-only field, ModelSerializer wouldn't generate UniqueTogetherValidator automatically.
        validators = [
            UniqueTogetherValidator(
                queryset=Track.objects.all(),
                fields=('artist', 'permalink'),
                message="Already existing permalink for the requested user."
            ),
        ]

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    @extend_schema_field(OpenApiTypes.INT)
    def get_like_count(self, track):
        return track.likes.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_repost_count(self, track):
        return track.reposts.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_comment_count(self, track):
        return track.comments.count()

    def validate_permalink(self, value):
        if not any(c.isalpha() for c in value):
            raise ValidationError("Permalink must contain at least one alphabetic character.")

        return value

    def validate(self, data):

        # Although it has default value, should manually include 'artist' to the data because it is read-only field.
        if self.instance is None:
            data['artist'] = self.context['request'].user

        return data


class TrackMediaUploadSerializer(MediaUploadMixin, TrackSerializer):

    audio_filename = serializers.CharField(write_only=True)
    image_filename = serializers.CharField(write_only=True, required=False)
    audio_presigned_url = serializers.SerializerMethodField()
    image_presigned_url = serializers.SerializerMethodField()

    class Meta(TrackSerializer.Meta):
        fields = TrackSerializer.Meta.fields + (
            'audio_filename',
            'image_filename',
            'audio_presigned_url',
            'image_presigned_url',
        )

    def validate(self, data):
        data = super().validate(data)
        data = self.filenames_to_urls(data)

        return data


class SimpleTrackSerializer(serializers.ModelSerializer):
    
    artist = SimpleUserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'like_count',
            'repost_count',
            'comment_count',
            'genre',
            'count',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    def get_like_count(self, track):
        return track.likes.count()

    def get_repost_count(self, track):
        return track.reposts.count()

    def get_comment_count(self, track):
        return track.comments.count()


class UserTrackSerializer(serializers.ModelSerializer):

    audio = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    repost_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'permalink',
            'audio',
            'image',
            'like_count',
            'repost_count',
            'comment_count',
            'genre',
            'count',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    def get_like_count(self, track):
        return track.likes.count()

    def get_repost_count(self, track):
        return track.reposts.count()

    def get_comment_count(self, track):
        return track.comments.count()


class CommentTrackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Track
        fields = (
            'id',
            'title',
            'permalink'
        )

class SetTrackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Track
        fields = (
            'id'
            'title',
            'artist',
            'permalink',
            'audio',
            'image',
            'count',
            'is_like',
            'repost',
        )

    def get_audio(self, track):
        return get_presigned_url(track.audio, 'get_object')

    def get_image(self, track):
        return get_presigned_url(track.image, 'get_object')

    def get_is_like(self, track):
        if self.context['request'].user.is_authenticated:
            try:                	
                contenttype_obj = ContentType.objects.get_for_model(track)
                Like.objects.get(user=self.context['request'].user, object_id=track.id, content_type=contenttype_obj)
                return True
            except Like.DoesNotExist:
                return False
        else: 
            return False 

    def get_repost(self, track):
        if self.context['request'].user.is_authenticated:
            try:                	
                contenttype_obj = ContentType.objects.get_for_model(track)
                repost = Repost.objects.get(user=self.context['request'].user, object_id=track.id, content_type=contenttype_obj)
                return RepostSerializer(repost, context=self.context).data
            except Repost.DoesNotExist:
                return None
        else: 
            return None 