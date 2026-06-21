from django.db import models
from django.conf import settings
# Create your models here.

class RecipeModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Recipes Table'

    PREPARATION_TIME_CHOICES = [
        ('under 10', 'under 10 minutes'),
        ('10-20', '10-20 minutes'),
        ('20-30', '20-30 minutes'),
        ('30+', '30+ minutes'),
    ]

    CATEGORY_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('difficult', 'Difficult'),
    ]

    # default fields
    title = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    media = models.FileField(upload_to='recipes/media/', blank=True, null=True)
    servings = models.IntegerField(default=1)
    preparation_time = models.CharField(choices=PREPARATION_TIME_CHOICES, max_length=10, blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20, default='breakfast')
    difficulty = models.CharField(choices=DIFFICULTY_CHOICES, max_length=10, default='easy')
    
    ingredients = models.JSONField(blank=False, null=False)
    frosting = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Simple counters
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)

    # custom fields
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    
    def __str__(self):
        return self.title


class StepByStepRecipeModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Step By Step Recipes Table'

    # default fields
    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='step_by_step_recipes')
    step = models.IntegerField(default=1)
    title = models.TextField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='recipes/step_by_step_images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.recipe.title} - Step {self.step}'

class RecipeLikeModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Recipe Likes Table'
        unique_together = ('recipe', 'user')

    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_likes')
    created_at = models.DateTimeField(auto_now_add=True)

class RecipeCommentModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Recipe Comments Table'

    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_comments')
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

class RecipeShareModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Recipe Shares Table'

    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_shares')
    created_at = models.DateTimeField(auto_now_add=True)

class RecipePinModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Recipe Pins Table'
        unique_together = ('recipe', 'user')

    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='pins')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_pins')
    created_at = models.DateTimeField(auto_now_add=True)

class RecipeSaveModel(models.Model):
    class Meta:
        app_label = 'recipes'
        db_table = 'Recipe Saves Table'
        unique_together = ('recipe', 'user')

    recipe = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name='saved_by')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_recipes')
    created_at = models.DateTimeField(auto_now_add=True)