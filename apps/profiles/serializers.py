from rest_framework import serializers
from apps.profiles.models import DeliveryAddress


class ProfileSerializer(serializers.Serializer):
    """сериализатор для обработки данных профиля юзера(получения и обновления)"""
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)
    email = serializers.EmailField(read_only=True)
    avatar = serializers.ImageField(required=False)
    account_type = serializers.CharField(read_only=True) # тип аккаунта юзера Byer или seller


class DeliveryAddressSerializer(serializers.Serializer):
    '''Сериализатор для модели адреса доставки товара'''
    id = serializers.UUIDField(read_only=True) # что бы находить опред адрес доставки по id
    full_name = serializers.CharField(max_length=500)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=12)
    address = serializers.CharField(max_length=1000)
    city = serializers.CharField(max_length=100)
    country = serializers.CharField()
    
    zipcode = serializers.CharField()

# вариант N2 для DeliveryAddressSerializer
class DeliveryAddressSerializer2(serializers.ModelSerializer):
    '''альтеранитвыйн сериализатор на основе ModelSerializer'''
    class Meta:
        model=DeliveryAddress
        fields=[
            'id',
            'full_name',
            'email',
            'phone',
            'address',
            'city',
            'country',
            'zipcode',
        ]
        read_only_fields=('id',)
        extra_kwargs={
            'address': {'required': True},
            'country': {'required': True},
            'zipcode': {'required': True},
            'phone': {'required': True}
        }
    def create(self, validated_data):
        user = self.context['request'].user
        return DeliveryAddress.objects.create(user=user, **validated_data)
