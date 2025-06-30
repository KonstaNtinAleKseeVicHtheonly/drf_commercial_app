from rest_framework import serializers
from apps.profiles.serializers import DeliveryAddressSerializer
from drf_spectacular.utils import extend_schema_field
# импорт моделей
from apps.shop.models import Review


class CategorySerializer(serializers.Serializer):
    '''сериализатор для каткгорий товаров магазина'''
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)# автоищменение слага при изменении имени категории
    image = serializers.ImageField()


class SellerShopSerializer(serializers.Serializer):
    '''Сериализтор данных о продавце'''
    name = serializers.CharField(source='business_name') # получаем инфу их поля business_name продавца (модель Seller)
    slug = serializers.SlugField()
    avatar = serializers.CharField(source='user.avatar')# обращаемся к полю user модели Seller(user-ForeignKey) к модели User
    
class ProductSerializer(serializers.Serializer):
    '''серилизатор для сериалзиации уже созданных продуктов(продавцов) с вложенными сериализаторами'''
    seller = SellerShopSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField() 
    desc = serializers.CharField()
    price_old =serializers.DecimalField(max_digits=10, decimal_places=2)
    price_current =serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer()
    in_stock = serializers.IntegerField() # количество товара на складе
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)

class CreateProductSerializer(serializers.Serializer):
    '''серилизатор для создания новых  продуктов без вложенных сериализаторов'''
    name = serializers.CharField()
    category_slug = serializers.SlugField()# передача категории товара через slug
    desc = serializers.CharField()
    price_current =serializers.DecimalField(max_digits=10, decimal_places=2)
    in_stock = serializers.IntegerField() # количество товара на складе
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)


    
class OrderItemProductSerializer(serializers.Serializer):
    '''Сериализатор для предоставления данных о продукте, 
    в составе заказа юзера(как товар в корзине).Сериализует выборочные поля из модели Product'''
    
    seller = SellerShopSerializer()
    name =serializers.CharField(max_length=100)
    slug = serializers.SlugField() # db_index=True создает индекс для поля в базе данных для ускорения поиска по slug.
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price_current')

class OrderItemSerializer(serializers.Serializer):
    '''Сериализатор для предоставления данныъ элемента корзины'''
    product = ProductSerializer()
    quantity = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, source='get_total')

class ToggleCartItemSerializer(serializers.Serializer):
    '''Серилизатор для валидации данных юзера при добавлении,удалении
    товаров в его корзину(данные о юзере из модели OrderItem)'''
    slug = serializers.SlugField() # slug продукта в качестве его идентификатора
    quantity = serializers.IntegerField(min_value=0)


class CheckoutSerializer(serializers.Serializer):
    '''Сериализатор для валидации данных, связанных с этапом оформления заказа до создания самого заказа'''
    delivery_id = serializers.UUIDField()


class OrderSerializer(serializers.Serializer):
    '''Сериализатор для предоставления данных о заказе после его создания.(модель Order из приложения profile)
    Включает инфу  о доставке(delivery_address), указанной юзерм'''
    tx_ref = serializers.CharField() # уникаоьный id траназкции (для запроса оплаты заказа)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    delivery_status = serializers.CharField()
    payment_status = serializers.CharField()
    date_delivered = serializers.DateTimeField()
    delivery_details = serializers.SerializerMethodField() # данные для этого поля будут получены из метода get_delivery_details.
    subtotal = serializers.DecimalField(
        max_digits=100, decimal_places=2, source="get_cart_subtotal"
    ) # стоимость товара без учета доставки(ссылается наа метод моедли Order)
    total = serializers.DecimalField(
        max_digits=100, decimal_places=2, source="get_cart_total"
    ) # общая стоимость товара с учетом доставки

    @extend_schema_field(DeliveryAddressSerializer)
    def get_delivery_details(self, obj):
        '''получение данных о доставке'''
        return DeliveryAddressSerializer(obj).data # вернем сериализированные данные
    
class CheckItemOrderSerializer(serializers.Serializer):
    '''сериализатор для валидации данных о заказе юзера'''
    product = ProductSerializer() # вложенный сериализтор, предоставляющий данные о заказе
    quantity = serializers.IntegerField() # количесвто товара
    total = serializers.FloatField(source='get_total') # общая стоимсоть товара


class ProductReviewSerialzer(serializers.ModelSerializer):
    '''Сериализатор для CRUD операци с отзывами на товар'''
    class Meta:
        model = Review
        fields = ['id', 'user', 'product','rating', 'text']
        read_only_fields = ['user','product']
    def validate(self,data):
        # проверка на существования только 1 отзыва юзера на данный товар
        if self.instance is None: # только при создании
            user = self.context['request'].user
            product = data.get('product')
            if Review.objects.filter(user=user, product=product, is_deleted=False).exists():
                raise serializers.ValidationError({"error":'Вы уже оставляли отзыв на этот товар'})
        return data
