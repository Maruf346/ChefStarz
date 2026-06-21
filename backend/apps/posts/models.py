from django.db import models
from django.conf import settings

# Create your models here.
class PostModel(models.Model):
    class Meta:
        app_label = 'posts'
        db_table = 'Posts Table'

    POST_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    # default fields
    title = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    media = models.FileField(upload_to='posts/media/', blank=True, null=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='image')
    
    # Simple counters (can be updated by signals or property)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.media:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(self.media.name)
            if mime_type:
                if mime_type.startswith('video'):
                    self.post_type = 'video'
                elif mime_type.startswith('image'):
                    self.post_type = 'image'
        super().save(*args, **kwargs)


class LikeModel(models.Model):
    class Meta:
        app_label = 'posts'
        db_table = 'Likes Table'
        unique_together = ('post', 'user')

    # default fields
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.post.title} - {self.user.email}'


class CommentModel(models.Model):
    class Meta:
        app_label = 'posts'
        db_table = 'Comments Table'

    # default fields
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.post.title} - {self.user.email}'


class ShareModel(models.Model):
    class Meta:
        app_label = 'posts'
        db_table = 'Shares Table'

    # default fields
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shares')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.post.title} - {self.user.email}'

class PinModel(models.Model):
    class Meta:
        app_label = 'posts'
        db_table = 'Pinned Posts Table'
        unique_together = ('post', 'user')

    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='pins')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pins')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pinned: {self.post.title} by {self.user.email}'

class SaveModel(models.Model):
    class Meta:
        app_label = 'posts'
        db_table = 'Saved Posts Table'
        unique_together = ('post', 'user')

    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_posts')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Saved: {self.post.title} by {self.user.email}'