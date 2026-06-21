from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Notification
from apps.posts.models import LikeModel, CommentModel
from apps.recipes.models import RecipeLikeModel, RecipeCommentModel
from apps.users.models import CustomUserModel


def get_display_name(user):
    """Return the best available display name for a user."""
    if user.username:
        return user.username
    # Fallback: use email prefix before @
    return user.email.split('@')[0] if user.email else 'Someone'

# 1. User Followed (M2M Change)
@receiver(m2m_changed, sender=CustomUserModel.followers.through)
def user_followed_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            follower = CustomUserModel.objects.get(pk=pk)
            # Notify the person who just got a new follower
            Notification.objects.create(
                recipient=instance,
                sender=follower,
                notification_type='follow',
                text=f"{get_display_name(follower)} started following you!",
                target_id=follower.id
            )

# 2. Post Liked
@receiver(post_save, sender=LikeModel)
def post_liked_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.user:
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='post_like',
            text=f"{get_display_name(instance.user)} liked your post: {instance.post.title}",
            target_id=instance.post.id
        )

# 3. Post Commented
@receiver(post_save, sender=CommentModel)
def post_commented_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.user:
        Notification.objects.create(
            recipient=instance.post.user,
            sender=instance.user,
            notification_type='post_comment',
            text=f"{get_display_name(instance.user)} commented on your post: {instance.post.title}",
            target_id=instance.post.id
        )

# 4. Recipe Liked
@receiver(post_save, sender=RecipeLikeModel)
def recipe_liked_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.recipe.user:
        Notification.objects.create(
            recipient=instance.recipe.user,
            sender=instance.user,
            notification_type='recipe_like',
            text=f"{get_display_name(instance.user)} liked your recipe: {instance.recipe.title}",
            target_id=instance.recipe.id
        )

# 5. Recipe Commented
@receiver(post_save, sender=RecipeCommentModel)
def recipe_commented_notification(sender, instance, created, **kwargs):
    if created and instance.user != instance.recipe.user:
        Notification.objects.create(
            recipient=instance.recipe.user,
            sender=instance.user,
            notification_type='recipe_comment',
            text=f"{get_display_name(instance.user)} commented on your recipe: {instance.recipe.title}",
            target_id=instance.recipe.id
        )
