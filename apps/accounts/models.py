from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from apps.common.models import IsDeletedModel
from apps.accounts.managers import CustomUserManager

# Create your models here.
ACCOUNT_TYPE_CHOICES = (
    ("SELLER", "SELLER"),
    ("BUYER", "BUYER"),
)

class User(AbstractBaseUser, IsDeletedModel):
    '''Модель юзера от абстрактного класса'''
    first_name = models.CharField(verbose_name="First name", max_length=25, null=True)
    last_name = models.CharField(verbose_name="Last name", max_length=25, null=True)
    email = models.EmailField(verbose_name="Email address", unique=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, default='avatars/default.jpg')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    account_type = models.CharField(choices=ACCOUNT_TYPE_CHOICES, default='BUYER') # роль юзера покупатель или продавец
 
    USERNAME_FIELD = "email" #указывает, что адрес электронной почты является именем пользователя для входа в систему
    REQUIRED_FIELDS = ["first_name", "last_name"] # поля, обязательные к заполнению(не влияет на создание юзеров через формы и сериализаторы)
     
    objects = CustomUserManager() #добавлять дополнительную логику для работы с пользователями

    @property
    def full_name(self):
        '''Возвращает полное имя юзера'''
        return f"{self.first_name} {self.last_name}"
    @property
    def is_superuser(self):
        '''инфа с статусе одмена'''
        return self.is_staff
    
    def __str__(self):
        return self.full_name
    
    #Django permissions
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True