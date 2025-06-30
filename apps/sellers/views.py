from django.shortcuts import render
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from rest_framework.views import APIView
# сериализаторы
from apps.sellers.serializers import SellerSeriazer
from apps.shop.serializers import ProductSerializer, CreateProductSerializer, OrderSerializer, CheckItemOrderSerializer
# импорт моделей
from apps.sellers.models import  Seller
from apps.shop.models import Product, Category
from apps.profiles.models import Order, OrderItem
#permissions
from apps.common.permissions import IsSeller
#доп утилиты
from apps.sellers.utils import update_seller_product

tags = ['Sellers'] # для отображения в API документации
# Create your views here.

class SellerView(APIView):
    '''контроллер для создания продавца'''
    serializer_class = SellerSeriazer

    def get(self,request):
        user = request.user
        current_seller = Seller.objects.get_or_none(user=user)
        if not current_seller:
            return Response(data={"message":'данного юзера не существует'}, status=404)
        serializer = self.serializer_class(current_seller)
        return Response(data=serializer.data, status=201)
    
    @extend_schema(
            summary="добавить и обновить инфу о продавце",
            description="""
                Изменение и добавление инфы о продавце
                """,
                tags = tags,)
    def post(self,request):
        '''Добваление продавцами инфы о себе'''
        user = request.user

        serializer = self.serializer_class(data=request.data,partial=False) # все поля в сериализаторе обязательны для заполнения
        if serializer.is_valid():
            data = serializer.validated_data
            seller,_ = Seller.objects.update_or_create(user=user, defaults=data) # находит запись в таблице Seller и либо создает либо обновляет(данные из default)
            user.account_type = "SELLER" # меняем статус юзера с покупателя на продавца
            user.save()
            serializer = self.serializer_class(seller)
            return Response(data=serializer.data,status=201)
        return Response(data=serializer.errors, status=400)
    
class SellerProductsView(APIView):
    '''контроллер для CRUD операция товара текущим продавцом'''
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]


    @extend_schema(
        summary="Получение инфы о продукте текущего продавца",
        description="""
            This endpoint returns all products from a seller.
            Products can be filtered by name, sizes or colors.
        """,
        tags=tags,
    )
    def get(self,request, *args, **kwargs):
        current_seller = Seller.objects.get_or_none(user=request.user, is_approved=True)
        if not current_seller:
            return Response(data={'message':'Данного продавца не существует или он не подтвержден'},status=404)
        all_products = Product.objects.select_related('category','seller','seller__user').filter(seller=current_seller) # получаем все товары связанные с данным продавцвом
        serializer = self.serializer_class(all_products, many=True)
        return Response(data=serializer.data, status=200)
    
    @extend_schema(
        summary="Создание нового продукта",
        description="""
            This endpoint returns all products from a seller.
        """,
        tags=tags,
        responses=CreateProductSerializer,
        request= CreateProductSerializer
    )
    def post(self,request,*args,**kwargs):
        current_seller = Seller.objects.get_or_none(user=request.user, is_approved=True)
        if not current_seller:
            return Response(data={'message':'Данного продавца не существует или он не подтвержден'},status=404)
        serializer = CreateProductSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            category_slug = data.pop('category_slug', None) # слаг категории для определния категории
            current_category = Category.objects.get_or_none(slug=category_slug)
            if not current_category:
                 return Response(data={'message':'Категории не существует'},status=404)
            data['category'] = current_category
            data['seller'] = current_seller
            new_product = Product.objects.create(**data)
            serializer = self.serializer_class(new_product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    
class SellerProductView(APIView):
    '''контроллер для добавления и удаления товара по его slug текущим продавцом'''
    serializer_class = CreateProductSerializer
    permission_classes = [IsSeller]


    def get_object(self,slug):
        """Получение продукта или None"""
        product = Product.objects.get_or_none(slug=slug)
        if not product is not None:
            self.check_object_permissions(self.request, product)
        return product
        
    @extend_schema(
        summary="Обновление инфы о товаре",
        description="""
            обновляет поля товара, при необходимости перезаписывет актуальную и старую цены.
        """,
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        '''обновляет данные о товаре текущего продавца + проверка на принадлежность товара этом продавцу,проверка наличия товара'''
        
        current_product = self.get_object(kwargs['slug'])
        if not current_product:
            return Response(data={'message':'данного товара не существует'}, status=404)
        if current_product.seller != request.user.seller:
            return Response(data={'message':'Продавец не подтвержден'},status=403)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        category_slug = validated_data.pop('category_slug', None)
        category = Category.objects.get_or_none(slug=category_slug)
        if not category:
            return Response(data={'message':'Категория не существует'}, status=404)
        validated_data['category'] = category
        updated_product = update_seller_product(current_product,validated_data)
        updated_product.save()
        serializer = ProductSerializer(updated_product)
        return Response(data=serializer.data, status=200)
    @extend_schema(
        summary="Удаление продукта по слагу",
        description="""
                This endpoint allows a seller to delete a product.
            """,
        tags=tags
    )
    def delete(self,request,*args,**kwargs):
        product_slug = kwargs['slug']
        current_product = self.get_object(product_slug)
        if not current_product:
            return Response(data={'message':'данного товара не существует'}, status=404)
        if current_product.seller != request.user:
            return Response(data={'message':'Данного продавца не существует или он не подтвержден'},status=403)
        current_product.delete()
        return Response(data={'message':'товар успешно удален'}, status=201)


class SellerOrdersView(APIView):
    '''контроллер для отображения заказов, сделанных о текущего продавца'''
    serializer_class = OrderSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        operation_id="seller_orders_view",
        summary="Инфа о всех заказах по текущему продавцу",
        description="""
            This endpoint returns all orders for a current seller.
        """,
        tags=tags
    )
    def get(self,request):
        current_seller = request.user.seller # получаем продавца по текущему авторизированнму юзеру
        orders = Order.objects.filter(orderitems__product__seller=current_seller).order_by('-created_at') # получение всех заказаов где хотя бы 1 проукт от данного продавца
        if not orders.exists():
            return Response(data={'message':'По текущему продавце нет заказов'})
        serializer = self.serializer_class(orders, many=True)
        return Response(data=serializer.data,status=201)
    
class SellerItemOrderView(APIView):
    '''контроллер для показа конкретного заказа по текущему продавцу(по транзакционному id)'''
    serializer_class = CheckItemOrderSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        operation_id="seller_order_item_view",
        summary="Инфа об определенном заказе по текущему продавцу",
        description="""
            This endpoint returns all orders for a current seller.
        """,
        tags=tags
    )
    def get(self, request,**kwargs):
        current_seller = request.user.seller # получаем продавца по текущему авторизированнму юзеру
        current_order = Order.objects.get_or_none(tx_ref=kwargs['tx_ref']) # получение заказа по переданному в url id транзакции
        if not current_order:
            return Response(data={'message':'заказа по укаазанному транзакционному id не существует'})
        order_items = OrderItem.objects.filter(order=current_order, product__seller=current_seller) # получение элементов заказа принадлежащеих именно этому продавце
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)
