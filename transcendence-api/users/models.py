from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, userID, password=None, **extra_fields):
        if not userID:
            raise ValueError(_('The userId field must be set'))
        user = self.model(userID=userID, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_ft_user(self, oauthID, email, image, **extra_fields):
        if not oauthID:
            raise ValueError(_('The userId field must be set'))
        user = self.model(oauthID=oauthID, email = email, image = image, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(nickname, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(max_length=30, unique=True)
    userID = models.CharField(max_length=30, blank=True, null=True, unique=True)
    oauthID = models.CharField(max_length=30, blank=True, null=True)
    score = models.IntegerField(default=1000)
    image = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    is_in_game = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    match_cnt = models.IntegerField(default=0)
    win_cnt = models.IntegerField(default=0)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = []
