from django.contrib import admin
from .models import User,Transaction,TransactionRequest
# Register your models here.
@admin.register(User)

class UserAdmin(admin.ModelAdmin):
    list_display = ['username','is_premium','wallet_balance']
    

admin.site.register(Transaction)
admin.site.register(TransactionRequest)