from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_user = serializers.SerializerMethodField()
    notification_type_display = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_user',
            'notification_type', 'notification_type_display',
            'text', 'message', 'target_id',
            'is_read', 'created_at'
        ]
        read_only_fields = [
            'id', 'recipient', 'sender', 'sender_user',
            'notification_type', 'notification_type_display',
            'text', 'message', 'target_id', 'created_at'
        ]

    def get_sender_user(self, obj):
        if obj.sender:
            # Safely get profile picture URL to avoid S3 access errors
            try:
                profile_pic_url = obj.sender.profile_picture.url if obj.sender.profile_picture else None
            except Exception:
                profile_pic_url = None

            return {
                "id": obj.sender.id,
                "email": obj.sender.email,
                "username": obj.sender.username or obj.sender.email,
                "profile_picture": profile_pic_url,
            }
        return None

    def get_notification_type_display(self, obj):
        """Return a human-readable label for the notification type."""
        type_labels = {
            'follow': 'New Follower',
            'post_like': 'Post Liked',
            'post_comment': 'New Comment',
            'recipe_like': 'Recipe Liked',
            'recipe_comment': 'New Comment',
            'parent_approval': 'Parental Approval',
            'admin': 'Announcement',
        }
        return type_labels.get(obj.notification_type, obj.notification_type)

    def get_message(self, obj):
        """Return the notification text. If empty, generate a fallback from type + sender."""
        if obj.text:
            return obj.text

        # Fallback for old notifications that may have empty text
        sender_name = None
        if obj.sender:
            sender_name = obj.sender.username or obj.sender.email

        fallbacks = {
            'follow': f"{sender_name} started following you!" if sender_name else "You have a new follower.",
            'post_like': f"{sender_name} liked your post." if sender_name else "Someone liked your post.",
            'post_comment': f"{sender_name} commented on your post." if sender_name else "Someone commented on your post.",
            'recipe_like': f"{sender_name} liked your recipe." if sender_name else "Someone liked your recipe.",
            'recipe_comment': f"{sender_name} commented on your recipe." if sender_name else "Someone commented on your recipe.",
            'parent_approval': "Your account has been approved by a parent.",
            'admin': "You have a new announcement.",
        }
        return fallbacks.get(obj.notification_type, "You have a new notification.")