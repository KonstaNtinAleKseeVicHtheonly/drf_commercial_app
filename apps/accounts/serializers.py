from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User

class CreateUserSerializer(serializers.ModelSerializer):
    '''Сериализатор для контроллеп RegisterAPIVIew (регистрация юзера)'''
    class Meta:
        model = User
        fields = ('email','password')
    def validate_password(self, value: str) -> str:
        '''переорпеделяет пароль в хэшированный вид для хранения в БД'''
        return make_password(value)
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''кастомный сериализатр для генерации токенов(refresh access)
    для юзеров расширенный для передачи доп данных в нагрузку при создании токенов'''
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        #добавляем пользовательские данные в payload в jwt токене
        if user.is_staff:
            token['group'] = 'admin'
        else:
            token['group'] = 'user'
            token['role'] = user.account_type #  роль пользователя ("SELLER" или "BUYER").
        return token