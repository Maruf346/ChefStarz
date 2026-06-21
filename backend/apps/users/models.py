from django.db import models
from  django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "User"           # Singular name
        verbose_name_plural = "Users Account"   # Plural name
        app_label = 'users'
        db_table = 'Users Table'

    AGE_GROUP_CHOICES = [
        ('05-10 yrs', ('05-10 yrs')),
        ('11-15 yrs', ('11-15 yrs')),
        ('16-20 yrs', ('16-20 yrs'))
    ]

    # defauld fields
    email = models.EmailField(unique=True)
    username = models.TextField(max_length=15, unique=True, blank=True, null=True)


    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # custom fields
    age_group = models.CharField(choices=AGE_GROUP_CHOICES, max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.TextField(max_length=100, blank=True, null=True)
    followers = models.ManyToManyField('self', related_name='following', symmetrical=False, blank=True)
    
    parent_email = models.EmailField(blank=True, null=True)

    # Verification Trackers
    is_email_verified = models.BooleanField(default=False) # For the Kid
    is_parent_approved = models.BooleanField(default=False) # For the Parent

    # We will reuse this field for OTPs, or create two separate ones
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    # The account is only usable if BOTH are True
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserBlockModel(models.Model):
    class Meta:
        verbose_name = "User Block"
        verbose_name_plural = "User Blocks"
        app_label = 'users'
        db_table = 'User Blocks Table'
        unique_together = ('blocker', 'blocked')

    blocker = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='blocked_users_relationship')
    blocked = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='blocked_by_relationship')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked.email}"

    