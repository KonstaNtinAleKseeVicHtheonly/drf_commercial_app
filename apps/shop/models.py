from django.db import models
from apps.sellers.models import Seller
from autoslug import AutoSlugField
# from django.core.validators import MinValueValidator, MaxValueValidator

from apps.common.models import BaseModel, IsDeletedModel
from apps.accounts.models import User

# Create your models here.
class Category(BaseModel):
    '''Модель катгеории товара с базовой инфой о категории + фото'''
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)# автоищменение слага при изменении имени категории
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return f"Категория товаров : {self.name}"
    class Meta:
        verbose_name = 'Категрия'
        verbose_name_plural = 'Категории'

class Product(IsDeletedModel):
    '''модель продукта, связанного с продавцом и категорией, содержит базовую инфу о товаре, цена, описание, фото и т.д'''

    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, related_name="products", null=True)
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", unique=True, db_index=True) # db_index=True создает индекс для поля в базе данных для ускорения поиска по slug.
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_current = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    in_stock = models.IntegerField(default=5) # количество товара на складе
    # фото товара
    image1 = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/', blank=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True)


    def __str__(self):
        return f"Продукт {self.name}"

RATING_CHOICES = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
class Review(IsDeletedModel):
    '''модель отзывов на товар. У каждого юзера по 1 отзыву на товар'''
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_review', null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='product_review', null=True)
    rating = models.IntegerField(default=1, choices=RATING_CHOICES) # оценка товара
    text = models.TextField()# отзыв о товаре

