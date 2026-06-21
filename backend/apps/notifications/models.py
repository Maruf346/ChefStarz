from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('follow', 'New Follower'),
        ('post_like', 'Post Liked'),
        ('post_comment', 'New Comment on Post'),
        ('recipe_like', 'Recipe Liked'),
        ('recipe_comment', 'New Comment on Recipe'),
        ('parent_approval', 'Parental Approval Received'),
        ('admin', 'Admin Announcement'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='triggered_notifications',
        null=True, 
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.TextField()
    
    # Generic link to the object (could be post_id or recipe_id)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'Notifications Table'

    def __str__(self):
        return f'{self.notification_type} for {self.recipient.email}'