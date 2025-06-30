from django.db import models
from autoslug import AutoSlugField # автоматическая генерация уникального slug объекта
# Create your models here.

from apps.common.models import BaseModel
from apps.accounts.models import User



class Seller(BaseModel):
    '''модель Бизнес продавцов(поставщиков)связанного с пользователем с указаниме базовой инфы о бизнесе, банковских рекизитах'''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller') # обратная связь ьюзеа с продавцом через user.seller 

    # Business Information
    business_name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="business_name", always_update=True, null=True) 
    inn_identification_number = models.CharField(max_length=50) #Инн продавца, slug будет обновляться при каждом изменении поля  business_name
    website_url = models.URLField(null=True) #  URL-адрес сайта продавца
    phone_number = models.CharField(max_length=20)
    business_description = models.TextField()

    # Address Information
    business_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20) # почтовый индекс

    # Bank Information
    bank_name = models.CharField(max_length=255)
    bank_bic_number = models.CharField(max_length=9)
    bank_account_number = models.CharField(max_length=50)
    bank_routing_number = models.CharField(max_length=50)
   
    # Status fields
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        if self.is_approved:
            return f"Продавец из {self.business_name}.Подтвержден"
        return f"Продавец из {self.business_name}.Непоодтвержден"
