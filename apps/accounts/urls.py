
from django.urls import path, include
from apps.accounts.views import RegisterAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import  TokenRefreshView, TokenVerifyView

app_name = 'all_accounts'

urlpatterns = [
    path("", RegisterAPIView.as_view(), name="registration"),
    path("token/", MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # получение refresh и access токенов
    path("token/refresh/", TokenRefreshView.as_view(), name='token_refresh'), 
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), # проверка действительности токена   
]

