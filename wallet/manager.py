from time import sleep
from django.contrib.auth.models import BaseUserManager
from . import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
       
        user = self.model(username = username, **extra_fields)
        user.set_password(password)
        print("iii",user.wallet_balance)
        user.save(using=self._db)
        return user
    


    def create_superuser(self, username, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given username and password.
        """
        extra_fields.setdefault('first_name','admin')
        extra_fields.setdefault('last_name','admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('wallet_balance', 2500)
        extra_fields.setdefault('is_premium', True)
        return self.create_user(username, password, **extra_fields)

