from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# импорт моделей
from apps.profiles.models import DeliveryAddress, Order, OrderItem
# сериалзиторы
from apps.profiles.serializers import ProfileSerializer, DeliveryAddressSerializer
from apps.shop.serializers import OrderSerializer, CheckItemOrderSerializer
# permissions
from apps.common.permissions import IsOwner # доступ на чтение, изменения только владельцу объетка и админу
# доп утилиты 
from apps.profiles.utils import set_dict_attr # для сохранения обновленной инфы в объетке при PUT запросе
# Create your views here.
from drf_spectacular.utils import extend_schema
tags = ["Profiles"] # для расширения функиионала документации OpenAPI для View


class ProfileView(APIView):
    '''контроллер CRUD операция для профиля юзера'''
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]

    @extend_schema(
            summary="Get info about Profile",
            description="""
                Отображение инфы о профиле
                """,
                tags = tags,)
    def get(self,request):
        '''метод получает данные от юзера(который этот запрос отправил) и передает этому же пользователю'''
        current_user = request.user
        serializer = self.serializer_class(current_user)
        return Response(serializer.data, status=200)
    @extend_schema(
            summary="Update Profile",
            description="""
                Обновление инфы в профиле
                """,
                tags = tags,
                request={"multipart/form-data":serializer_class}
                )
    def put(self, request):
        current_user = request.user  # получаем данные о юзере, отправившем запрос
        serializer = self.serializer_class(data=request.data) # сериализуем данные полученные из запроса
        serializer.is_valid(raise_exception=True) # проверка на валидность
        current_user = set_dict_attr(current_user,serializer.validated_data)
        current_user.save() # сохраняем измененные данные в БД
        serializer = self.serializer_class(current_user) # сериализуем данные уже обновленного пользователя
        return Response(data=serializer.data)
    
    @extend_schema(
            summary="Deactivate Profile",
            description="""
                Деактивация профиля юзера
                """,
                tags = tags,)
    def delete(self, request):
        '''деактивация пользователя'''
        user = request.user
        user.is_active = False
        user.save()
        return Response(data={"message":"User has been deactivated"})
    
class DeliveryAddressView(APIView):
    '''контроллер для оображения инфы о адресе доставки товара'''
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsOwner]
    
    @extend_schema(
            summary="Get info about DeliveryAddress",
            description="""
                Отображение инфы об адресе доставки
                """,
                tags = tags,)
    def get(self, request, *args, **kwargs):
        '''отображени инфы о заказе пользователю'''
        current_user = request.user
        delivery_addresses = DeliveryAddress.objects.filter(user=current_user) # поулчение всех адресов доставки юзера
        serializer = self.serializer_class(delivery_addresses, many=True)
        return Response(data=serializer.data, status=200)
    @extend_schema(
            summary="Create deliveryaddress    ",
            description="""
                Создание адреса доставки или возвращение старого адреса
                """,
                tags = tags,
                )
    def post(self,request,*args, **kwargs):
        '''передача инфы об адресе доставки,если юзер взял старый адрес доставки, не изменяя его, мы
        берем его из бд, а не создаем заново'''
        user = request.user
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        validate_data = serializer.validated_data # данные для сохранения в бд
        delivery_address, _ = DeliveryAddress.objects.get_or_create(user=user, **validate_data) # получает или создает адрес доставки для текущего юзера(_ нужно для игнорирования параметра bool)
        serializer = self.serializer_class(delivery_address)
        return Response(data=serializer.data, status=201)

class DeliveryAddressViewID(APIView):
    '''корнтроллер для CRUD операции адресов доставки'''
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsOwner]

    def get_object(self, user, delivery_id):
        '''chec_object_permissions вызвывает permission_classes даного View для определения прав доступа текущего юзера '''
        delivery_address = DeliveryAddress.objects.get_or_none(user=user,id=delivery_id)
        if delivery_address is not None:
            self.check_object_permissions(self.request,delivery_address) # ручная проверка на жоступ из-за переопределения метода get_obect
        return delivery_address

    @extend_schema(
            summary="инфа об адресе доставки по id",
            description="""
                Отображение инфы о доставке данного юзера
                """,
                tags = tags,)
    def get(self,request, *args,**kwargs):
        user = request.user
        delivery_addresses = self.get_object(user,kwargs['id'])# получение опред адреса доставки по
        if not delivery_addresses:
            return Response(data={"message":"Данный объект не найден"},status=404)
        serializer = self.serializer_class(delivery_addresses)
        return Response(serializer.data)
    
    @extend_schema(
            summary="Обновление инфы об адресе доставки",
            description="""
                Отображение инфы об адресе доставки
                """,
                tags = tags,)
    def put(self,request,*args,**kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        delivery_address = set_dict_attr(user,data)
        delivery_address.save()
        serializer = self.serializer_class(delivery_address)
        return Response(data=serializer.data,status=200)
    @extend_schema(
            summary="Удаление адреса доставки данного юзера",
            description="""
                Деактивация адреса доставки
                """,
                tags = tags,)
    def delete(self, request, *args, **kwargs):
        user = request.user
        delivery_address = self.get_object(user,kwargs['id'])
        if not delivery_address:
            return Response(data={"message":"Данный объект не найден"},status=404)
        delivery_address.delete()
        return Response(data={'message':'Адрес успешно удален'}, status=200)
        



class OrdersView(APIView):
    '''Контроллер предоставляющий инфу о заказах юзера'''
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        operation_id="orders_view",
        summary="Инфа о всех заказах текущего юзера",
        description="""
            This endpoint returns all orders for a particular user.
        """,
        tags=tags
    )
    def get(self,request):
        current_user = request.user
        user_orders = (Order.objects.filter(user=current_user)
                .prefetch_related("orderitems", "orderitems__product") # вытаскиваем обратные внешний ключ у модели OrderItem
                .order_by("-created_at"))
        if not user_orders.exists():
            return Response(data={'message':'У этого юзера нет заказов'},status=201)
        serializer = self.serializer_class(user_orders, many=True)
        return Response(data=serializer.data, status=200)
    
class OrderItemView(APIView):
    '''предоставляет детальную инфу о позициях(товарх) в  определенном заказе по его tx_ref(уинкальный id транзакции)'''
    serializer_class = CheckItemOrderSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        operation_id="order_item_view",
        summary="Инфа о определенном заказе по его транакционному id",
        description="""
            This endpoint returns all orders for a particular user.
        """,
        tags=tags
    )
    def get(self,request,**kwargs):
        order = Order.objects.get_or_none(tx_ref=kwargs['tx_ref']) # определяем текущий заказ по его id транзакции tx_ref
        if not order:
            return Response(data={'message':'Заказа по данном id транзакции не существует'},status=404)
        if order.user != request.user:
            return Response(data={'message':'Юзер не соответсвтует запрашиваемому'},status=400)#
        order_items = OrderItem.objects.filter(order=order) # возвращаем все позиции(товары) с текущего заказа
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status= 200)