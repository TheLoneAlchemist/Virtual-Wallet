from django.urls import path
from .views import *
urlpatterns = [
    path('', Index, name="index"),
    path('register', Register, name="register"),
    path('login', Login, name="login"),
    path('logout', Logout, name="logout"),
    path('wallet', Wallet, name="wallet"),
    path('sendmoney', SendMoney, name="sendmoney"),
    path('requestmoney', RequestMoney, name="requestmoney"),
    path('requestlog', RequestLog, name="requestlog"),
]
