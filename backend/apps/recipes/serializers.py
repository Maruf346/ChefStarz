from rest_framework import serializers
from .models import RecipeModel, StepByStepRecipeModel, RecipeLikeModel, RecipeCommentModel, RecipeShareModel, RecipePinModel, RecipeSaveModel
from apps.users.serializers import CustomUserModelSerializer

class RecipeLikeModelSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = RecipeLikeModel
        fields = ['id', 'user', 'created_at']

class RecipeCommentModelSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = RecipeCommentModel
        fields = ['id', 'user', 'comment', 'created_at']

class RecipePinModelSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = RecipePinModel
        fields = ['id', 'user', 'created_at']

class RecipeSaveModelSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = RecipeSaveModel
        fields = ['id', 'user', 'created_at']

class RecipeShareModelSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = RecipeShareModel
        fields = ['id', 'user', 'created_at']

class StepByStepRecipeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepByStepRecipeModel
        fields = ['id', 'step', 'title', 'description', 'image']

class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    # Use JSONField for input to avoid Swagger/MultiPart issues with nested lists
    steps = serializers.JSONField(write_only=True, required=False, help_text="List of step objects: [{'step': 1, 'title': '...', 'description': '...'}]")
    
    class Meta:
        model = RecipeModel
        fields = [
            'id', 'user', 'title', 'description', 'media', 'servings', 
            'preparation_time', 'category', 'difficulty',
            'ingredients', 'frosting', 'steps'
        ]
        read_only_fields = ['user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Use StepByStepRecipeModelSerializer to ensure image URLs are correct in response
        representation['steps'] = StepByStepRecipeModelSerializer(
            instance.step_by_step_recipes.all(), 
            many=True,
            context=self.context
        ).data
        return representation

    def create(self, validated_data):
        request = self.context.get('request')
        steps_data = validated_data.pop('steps', [])
        
        # In multipart/form-data, steps might be a string that needs parsing
        if isinstance(steps_data, str):
            import json
            try:
                steps_data = json.loads(steps_data)
            except json.JSONDecodeError:
                steps_data = []

        recipe = RecipeModel.objects.create(**validated_data)
        
        for i, step_data in enumerate(steps_data):
            # Extract image from request.FILES if it exists (e.g., steps[0][image])
            if request and request.FILES:
                image = request.FILES.get(f'steps[{i}][image]')
                if image:
                    step_data['image'] = image
            
            StepByStepRecipeModel.objects.create(recipe=recipe, **step_data)
        return recipe

    def update(self, instance, validated_data):
        request = self.context.get('request')
        steps_data = validated_data.pop('steps', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if steps_data is not None:
            # In multipart/form-data, steps might be a string that needs parsing
            if isinstance(steps_data, str):
                import json
                try:
                    steps_data = json.loads(steps_data)
                except json.JSONDecodeError:
                    steps_data = []

            instance.step_by_step_recipes.all().delete()
            for i, step_data in enumerate(steps_data):
                # Extract image from request.FILES if it exists
                if request and request.FILES:
                    image = request.FILES.get(f'steps[{i}][image]')
                    if image:
                        step_data['image'] = image
                
                # If image is a string (e.g., existing URL), remove it to avoid model errors
                # during recreation, unless we want to try and preserve it.
                if 'image' in step_data and isinstance(step_data['image'], str):
                    if step_data['image'].startswith('http'):
                        del step_data['image']

                StepByStepRecipeModel.objects.create(recipe=instance, **step_data)
        return instance

class RecipeModelSerializer(serializers.ModelSerializer):
    steps = StepByStepRecipeModelSerializer(many=True, 
                                            source='step_by_step_recipes', 
                                            required=False)

    likes_list = RecipeLikeModelSerializer(many=True, source='likes', read_only=True)
    comments_list = serializers.SerializerMethodField()
    shares_list = RecipeShareModelSerializer(many=True, source='shares', read_only=True)
    pins_list = RecipePinModelSerializer(many=True, source='pins', read_only=True)
    saves_list = RecipeSaveModelSerializer(many=True, source='saved_by', read_only=True)

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_details = CustomUserModelSerializer(source='user', read_only=True)

    total_likes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    total_shares = serializers.SerializerMethodField()
    total_pins = serializers.SerializerMethodField()
    total_saves = serializers.SerializerMethodField()

    class Meta:
        model = RecipeModel
        fields = [
            'id', 'title', 'description', 'media', 'servings', 
            'preparation_time', 'category', 'difficulty',
            'ingredients', 'frosting', 
            'user', 'user_details', 'steps', 'created_at', 'updated_at',
            'total_likes', 'total_comments', 'total_shares', 'total_pins', 'total_saves',
            'likes_list', 'comments_list', 'shares_list', 'pins_list', 'saves_list',
        ]
        read_only_fields = ['user', 'user_details', 'total_likes', 'total_comments', 'total_shares', 'total_pins', 'total_saves', 'created_at', 'updated_at']


    def get_total_likes(self, obj):
        return obj.likes.count()

    def get_total_comments(self, obj):
        return obj.comments.count()

    def get_total_shares(self, obj):
        return obj.shares.count()

    def get_total_pins(self, obj):
        return obj.pins.count()

    def get_total_saves(self, obj):
        return obj.saved_by.count()

    def get_comments_list(self, obj):
        request = self.context.get('request')
        comments = obj.comments.all()
        if request and request.user.is_authenticated:
            blocked_user_ids = request.user.blocked_users_relationship.values_list('blocked_id', flat=True)
            blocked_by_ids = request.user.blocked_by_relationship.values_list('blocker_id', flat=True)
            comments = comments.exclude(user_id__in=blocked_user_ids).exclude(user_id__in=blocked_by_ids)
        return RecipeCommentModelSerializer(comments, many=True, context=self.context).data


