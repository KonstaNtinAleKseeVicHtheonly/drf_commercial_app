from django.db import models
# импорт моделей приложенйи
from apps.accounts.models import User
from apps.shop.models import Product
from apps.common.models import BaseModel

from apps.common.utils import generate_unique_code

class DeliveryAddress(BaseModel):
    '''Адрес доставки  с инфой о получателе(телефон, улица, город и т.д
    ) содрежит так же код почтовый индекс zipcode. Указывается при создании заказа'''

    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='delivery_addresses') # related_name для обрщения по обртной связи от юзера ко всем связанным с ним адресам : user.delivery_addresses
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=6)# почтовый индекс

    def __str__(self):
        return f"{self.full_name}'s delivery details"
    
DELIVERY_STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("PACKING", "PACKING"),
    ("SHIPPING", "SHIPPING"),
    ("ARRIVING", "ARRIVING"),
    ("SUCCESS", "SUCCESS"),
) # статус доставки товара

PAYMENT_STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("PROCESSING", "PROCESSING"),
    ("SUCCESSFUL", "SUCCESSFUL"),
    ("CANCELLED", "CANCELLED"),
    ("FAILED", "FAILED"),
) # статус оплаты товара

class Order(BaseModel):
    '''Модель заказа юзера с связью с этим юзером, статусами доставки, оплаты
    ,+ с расширенно инфой о получателе(на случай если после покупки адрес изменится)'''

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    tx_ref = models.CharField(max_length=100, blank=True, unique=True) # Уникальный идентификатор транзакции
    delivery_status = models.CharField(
        max_length=20, default="PENDING", choices=DELIVERY_STATUS_CHOICES
    )
    payment_status = models.CharField(
        max_length=20, default="PENDING", choices=PAYMENT_STATUS_CHOICES
    )
    date_delivered = models.DateTimeField(null=True, blank=True) # дата доставки

    # развернутая инфа о получателе
    full_name = models.CharField(max_length=1000, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=100, null=True)
    zipcode = models.CharField(max_length=6, null=True) # почтовый индекс

    @property
    def get_cart_subtotal(self):
        '''расчитывает стоимость товаров в корзине без учета доставки'''
        order_items = self.orderitems.all()
        subtotal  = sum([item.get_total for item in order_items])
        return subtotal
    
    @property
    def get_cart_total(self):
        '''расчитывает полную стоимость товаров в корзине с учетом доставки'''
        total = self.get_cart_subtotal
        return total
    
    def __str__(self):
        return f"Заказ юзера {self.full_name}. Статус оплаты {self.payment_status}. Статус доставки {self.delivery_status}"
    
    def save(self, *args, **kwargs) -> None:
        '''расширил метод для содания уникального id транзакции при создании заказа'''
        if not self.created_at:
            self.tx_ref = generate_unique_code(Order, "tx_ref") # генерация уникального кода транзакции
        super().save(*args, **kwargs)

class OrderItem(BaseModel):
    '''Модель отобрающая позицию товара в заказе, его количество и прочее.
    Если нет связи с каким либо заказаом (order), буедт использоваться как корзина, если есть связь, то как заказ'''
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True) # заказ мб создан без авторизованного пользователя.
    order = models.ForeignKey(
        Order,
        related_name="orderitems",
        null=True,
        on_delete=models.CASCADE,
        blank=True) #  Один заказ может иметь несколько позиций товаров.Если order=None заказы рассматриваются как корзина Cart
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # Один продукт может быть частью многих заказов.
    quantity = models.PositiveIntegerField(default=1)

    @property
    def get_total(self):
        '''вернет итоговую стоимтость пощиции заказа с учетом количества товара'''
        return self.product.price_current * self.quantity
    
    class Meta:
        ordering = ["-created_at"] # сортировка по дате созания (сначала новые позици)

    def __str__(self):
        return f"Строчка заказа пользователя {self.user.full_name} с товаром {self.product.name} в количестве {self.quantity}"