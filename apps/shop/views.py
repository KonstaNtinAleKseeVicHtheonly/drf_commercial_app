from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from apps.shop.schema_examples import PRODUCT_PARAM_EXAMPLE

#Сериализаторы
from apps.shop.serializers import CategorySerializer, ProductSerializer, CreateProductSerializer, OrderItemSerializer, ToggleCartItemSerializer, CheckoutSerializer, OrderSerializer,ProductReviewSerialzer
# импорт моделей
from apps.shop.models import Category, Product, Review
from apps.profiles.models import OrderItem, DeliveryAddress, Order
from apps.sellers.models import Seller
#permissions
from rest_framework.permissions import  AllowAny, IsAuthenticated
from apps.common.permissions import IsAdminorReadOnly, CartandOrderPermission
# для фильтрации
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from apps.shop.filters import ProductFilter
# пагинация
from rest_framework.pagination import PageNumberPagination
from apps.common.paginations import CustomPagination
# доп утилиты
from django.db.models import Avg, Q # для расчитывания реднего рейтинга по продукту



tags = ["Shop"]

class CategoryView(APIView):
    '''Контроллер для CRUD операций с категориями товара'''
    serializer_class = CategorySerializer
    permission_classes = [IsAdminorReadOnly]
    @extend_schema(
        summary="Инфа о категориях",
        description="""
            This endpoint returns all categories.
        """,
        tags=tags
    )
    def get(self,request,*args,**kwargs):
        '''Вернет все категории товаров'''
        all_categories = Category.objects.all()
        serializer = self.serializer_class(all_categories, many=True)
        return Response(data=serializer.data,status=201)
    @extend_schema(
        summary="Создание новой категории",
        description="""
            This endpoint returns all categories.
        """,
        tags=tags
    )
    def post(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_category = Category.objects.create(**serializer.validated_data)
            serializer = self.serializer_class(new_category) # передаем инфу о созданной категории
            return Response(serializer.data,status=201)
        return Response(serializer.errors, status=404)

class ProductsByCategoryView(APIView):
        '''контроллер дл показа всех товаров по заданной категории, со всего магазина'''
        serializer_class = ProductSerializer
        permission_classes = [AllowAny]
        

        @extend_schema(
        operation_id="category_products", # для избежания колизий при одинаковых API запросах
        summary="все товары по заданной категории",
        description="""
            This endpoint returns all products in a particular category.
        """,
        tags=tags
    )
        def get(self,request, *args, **kwargs):
            category = Category.objects.get_or_none(slug=kwargs['slug'])
            if not category:
                return Response(data={"message": "Category does not exist!"}, status=404)
            products_by_category = Product.objects.select_related("category", "seller", "seller__user").filter(category=category)\
        .annotate(
            avg_rating=Avg(
                'product_review__rating',
                filter=Q(product_review__is_deleted=False)
            )
        )# берем все связанный с данной категорией и юзером товары + его средний рейтинг
            serializer = self.serializer_class(products_by_category, many=True)
            response_data = []
            for product, serialized_data in zip(products_by_category,serializer.data):
                    response_data.append({
                **serialized_data,
                'avg_rating': product.avg_rating or 0  # 0 если нет отзывов
                    })
            return Response(response_data, status=200)
        
class AllStoreProductsView(APIView):
        '''выводит все товары в магазине, добавлен функционал фильтрации по цене'''
        serializer_class=ProductSerializer
        permission_class = [AllowAny]
        pagination_class = CustomPagination
        
        
        @extend_schema(
        operation_id="all_products",
        summary="Все товары из магазина",
        description="""
            This endpoint returns all products.
        """,
        tags=tags,
        parameters=PRODUCT_PARAM_EXAMPLE # список параметров фильтрации при запросе 
    )
        def get(self,request, *args, **kwargs):
            store_products  = Product.objects.select_related("category", "seller", "seller__user").all() # берем все связанные с данной категорией и юзером товары
            filterset = ProductFilter(request.query_params, queryset=store_products) # филтрация по кастомному фильтерсет (макс, мин цена, количество на складе, дата добавления товара)
            if filterset.is_valid():
                queryset = filterset.qs # применение фильтрации при валидности
                paginator = self.pagination_class() # создает ЭК пагинации
                paginated_queryset = paginator.paginate_queryset(queryset, request) # разбивка отфильтрованного запроса на страницы согласно pagination_class
                serializer = self.serializer_class(paginated_queryset,many=True)
                return paginator.get_paginated_response(serializer.data) # ответ с сериализованныи данными + мета данными пагинации (след, пред страницы, их количество)
            return Response(filterset.errors, status=400)

        
class ProductsBySellerView(APIView):
    '''выводит все товары указанного продавца по его slug'''
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="seller_products", # для избежания колизий при одинаковых API запросах
        summary="все товары указанного продавца",
        description="""
            This endpoint returns all products in a particular seller.
        """,
        tags=tags
    )
    def get(self,request, *args, **kwargs):
        current_seller = Seller.objects.get_or_none(slug=kwargs['slug'])
        if not current_seller:
            return Response(data={"message": "Seller does not exist!"}, status=404)
        seller_products = Product.objects.select_related("category", "seller", "seller__user").filter(seller=current_seller)
        serializer = self.serializer_class(seller_products, many=True)
        return Response(data=serializer.data,status=200)
    
class CertainProductView(APIView):
    '''выводит определенный товар по его slug'''
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="certain_product", # для избежания колизий при одинаковых API запросах
        summary="Определенный товар по его slug",
        description="""
            This endpoint returns the details for a product via the slug.
        """,
        tags=tags
    )
    def get(self,request, *args, **kwargs):
        '''также выводит средний рейтинг товара'''
        current_product = Product.objects.filter(slug=kwargs['slug'])\
        .annotate(
            avg_rating=Avg('product_review__rating')  # вывод среднего рейтинга по продуку
        )\
        .select_related('category', 'seller')\
        .first() #  first в конце иначе ошибка анотации
        if not current_product:
             return Response(data={'message':'данного товара не существует'}, status=404)
        serializer = self.serializer_class(current_product)
        data = serializer.data
        response_data = {
        **data,
        'avg_rating': getattr(current_product, 'avg_rating', 0) 
    }
        return Response(response_data, status=200)

class CartView(APIView):
    '''контроллер для создания и просмотра корзины текущего юзера'''
    serializer_class = OrderItemSerializer
    permission_classes = [CartandOrderPermission]

    @extend_schema(
        summary="Данные о корзине юзера",
        description="""
            This endpoint returns all items in a user cart.
        """,
        tags=tags,
    )
    def get(self,request,*args,**kwargs):
            '''Предоставление ифны о корзине юзера, отправившего запрос'''
            current_user = request.user
            orderitems = OrderItem.objects.filter(user=current_user,order=None).select_related('product','product__seller','product__seller__user') # получаем все элементы корзины данного юзера, order=None - проверка что товары в корзине, и не явля.тс заказом
            if not orderitems.exists():
                 return Response(data={'message':'Корзина пуста'})
            serializer = self.serializer_class(orderitems, many=True)
            return Response(data=serializer.data)

    @extend_schema(
        summary="Создание корзины юзера",
        description="""
            This endpoint allows a user or guest to add/update/remove an item in cart.
            If quantity is 0, the item is removed from cart
        """,
        tags=tags,
        request=ToggleCartItemSerializer,
    )
    def post(self, request, *args, **kwargs):
        '''добавление, обновление или удаление товара из корзины'''
        current_user = request.user

        serializer = ToggleCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        quantity = validated_data['quantity'] # количество товара из запроса

        current_product = Product.objects.select_related('seller','seller__user').get_or_none(slug=validated_data['slug']) # получаем продукт из БД по его slug
        if not current_product:
             return Response(data={'message':'указанного товара не существует'},status=404)
                
        orderitem, created = OrderItem.objects.update_or_create(
                            user = current_user,
                            order_id=None,
                            product=current_product,
                            defaults={'quantity':quantity}
                            ) # обновляем или создаем позицию в корзине(т.к order_id=None)
        message_info = 'Updated In' # сообщение ответа юзеру
        status_code = 200
        if created:
             status_code = 201
             message_info = 'Товар добавлен'
        if orderitem.quantity == 0 : # удаление товара из корзины при количестве =0
            message_info='Товар удален'
            orderitem.delete()
            validated_data = None
        if message_info != 'Товар удален': # если товар не был удален
            serializer = self.serializer_class(orderitem)
            validated_data = serializer.data
        return Response(data={'message':f"item{message_info} Cart", "item":validated_data},
                        status=status_code)
    
class CheckoutView(APIView):
    '''контроллер для создания заказа'''
    serializer_class = CheckoutSerializer
    permission_classes = [CartandOrderPermission]

    @extend_schema(
        summary="Создание заказа по корзине юзера",
        description="""
               This endpoint allows a user to create an order through which payment can then be made through.
               """,
        tags=tags,
        request=CheckoutSerializer,
    )
    def post(self,request, *args, **kwargs):
        ''' Метод валидирует данные, получает товары из корзины, создает заказ и связывает его с товарами,превращает товары из корзины в заказ а затем возвращает данные о созданном заказе'''
         
        current_user = request.user
        orderitems = OrderItem.objects.filter(user=current_user, order=None) # берем все данные из корзины юзера
        if not orderitems.exists():
             return Response({"message": "В корзине нет товаров"}, status=404)
        serializer = self.serializer_class(data=request.data) # валидация анных из запроса
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        delivery_id = validated_data.get('delivery_id') # получаем id доставки

        if delivery_id:
              # получаем инфу о доставке по его id, указанного юзером
            delivery = DeliveryAddress.objects.get_or_none(id=delivery_id)
            if not delivery:
                return Response({"message": "No shipping address with that ID"}, status=404)
            
            fields_to_update = [
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "zipcode",
                ] # необходимые поля для обновления заказа
            data = {}

            for field in fields_to_update:
                value = getattr(delivery, field)
                data[field] =  value
            # создание заказа по корзине юзера и указанных данных
            new_order = Order.objects.create(user=current_user, **data)
            orderitems.update(order=new_order) # из статуса корзины в статус оформленного заказа в модели OrderItem

            serializer = OrderSerializer(new_order)
            return Response(data={'message':'Заказ успешно оформлен', 'item':serializer.data}, status=200)
        
class ProductReviewView(APIView):
    '''контроллер для предоставления инфы об отзывах указанного товара'''
    serializer_class = ProductReviewSerialzer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Просмотр отзывов по указанному товару",
        description="""
               This endpoint allows a look at product reviews.
               """,
        tags=tags,
    )
    def get(self,request,*args,**kwargs):
        current_product = Product.objects.get_or_none(slug=kwargs['slug'])
        if not current_product:
             return Response(data={'message':'данного продукта не существует'},status=404)
        product_reviews = Review.objects.filter(product=current_product,is_deleted=False)
        serializer = self.serializer_class(product_reviews, many=True)
        return Response(data=serializer.data, status=201)
     
class CreateReviewView(APIView):
    '''контррллер дя создания отзыва о товаре'''
    serializer_class = ProductReviewSerialzer


    @extend_schema(
        summary="Создание отзыва по указанному товару",
        description="""
               This endpoint allows a user to create a review (one review for one product).
               """,
        tags=tags,
    )
    def post(self, request, *args,**kwargs):
        current_user = request.user
        if current_user.account_type == 'SELLER':
            return Response(data={'message':'Продавец не может оставляь отзыв на товар'})
        current_product = Product.objects.get_or_none(slug=kwargs['slug'])
        if not current_product:
             return Response(data={'message':'указанного продукта не существует'}, status=404)
        check_product_review = Review.objects.get_or_none(user=current_user,product=current_product, is_deleted=False) # проверка, что у юзера на 1 товар только 1 отзыв
        if check_product_review is not None:
             return Response(data={'message':'Вы уже оставляли отзыв на этот товар'},status=400)
        serializer = self.serializer_class(data=request.data, context={'request':request,'product':current_product})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user'] = current_user
        validated_data['product'] = current_product
        new_review = Review.objects.create(**validated_data)
        serializer = self.serializer_class(new_review)
        return Response(data =serializer.data, status=201)


class ReviewDetailAPIView(APIView):
    '''Контроллер для просмотра, изменения, удаления указанного отзыва(по id)'''
    serializer_class = ProductReviewSerialzer
    permission_classes = [IsAuthenticated]
    
    def get_object(self,user,review_id):
        current_review = Review.objects.get_or_none(user=user,id=review_id, is_deleted=False)
        return current_review
    
    @extend_schema(
        summary="Демонстрация отзыва  по его id",
        description="""
               This endpoint allows a user to  show a certain review by its id (one review for one product).
               """,
        tags=tags,
    )
    def get(self,request, *args,**kwargs):
        current_user = request.user
        current_review = self.get_object(current_user, kwargs['review_id'])
        if not current_review:
            return Response(data={'message':'указанный отзыв не найден'}, status=404)
        serializer = self.serializer_class(current_review)
        return Response(data=serializer.data,status=201)
    @extend_schema(
        summary="Изменение отзыва по его id",
        description="""
               This endpoint allows a user to  update a certain review by its id (one review for one product).
               """,
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        current_user = request.user
        current_review = self.get_object(current_user, kwargs['review_id'])
        if request.user != current_review.user:
            return Response(data={'message':'Только автор отзыва может его изменять'}, status=401)
        if not current_review:
            return Response(data={'message':'указанный отзыв не найден'}, status=404)
        serializer = self.serializer_class(
        current_review,
        data=request.data,
        partial=True,
        context={'request': request})
        serializer.is_valid(raise_exception=True)  # Автоматически вернет 400 при ошибке
        serializer.save()
        
        return Response(serializer.data, status=200)
    
    
    @extend_schema(
        summary="Удаление отзыва по его id",
        description="""
               This endpoint allows a user to  delete a certain review by its id (one review for one product).
               """,
        tags=tags,
    )
    def delete(self,request, *args, **kwargs):
        current_user = request.user
        current_review = self.get_object(current_user,kwargs['review_id'])
        if not current_review:
            return Response(data={"message":'Отзыва по указанному id не существует'}, status=404)
        if current_user != current_review.user:
            return Response(data={"mesage":"только автор отзыва может его удалять"})
        current_review.delete()
        return Response(data={'message':'Данный отзыв успешно удален'},status=201)
        