from django.db import models

from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.contrib.auth.models import AbstractUser, Group, Permission
class User(AbstractUser):
    is_premium = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2,default=0.01)
    
    REQUIRED_FIELDS = []
    
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, help_text='The groups this user belongs to.', related_name='wallet_users')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_name='wallet_users')
    
    objects = UserManager()

    def save1(self, *args, **kwargs):
        print(self,self.wallet_balance)
        if self.is_premium:
            self.wallet_balance = 2500.0
        else:
            self.wallet_balance = 1000.0
        super().save(*args, **kwargs)


    def save(self, update_balance=False,*args, **kwargs):
            print("overload: ",self,self.wallet_balance)
            if update_balance == True:
                print("overload")
                super().save(*args, **kwargs)
            elif not User.objects.filter(username=self.username).exists():
                self.save1()
            else:
                super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('send', 'Send'),
        ('receive', 'Receive'),
        ('CR','DR')
    )

    sender = models.ForeignKey(User, related_name='sender_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender_remain_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    reciever_remain_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    sender_transaction_charge = models.DecimalField(max_digits=10, decimal_places=2)
    reciever_transaction_charge = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.CharField(max_length=50)

    def __str__(self):
        return self.sender.first_name
    



class TransactionRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transaction_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_transaction_requests', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} requested:( {self.amount}) amount from {self.receiver}'


