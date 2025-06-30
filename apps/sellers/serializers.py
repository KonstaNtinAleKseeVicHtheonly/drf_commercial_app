from rest_framework import serializers


class SellerSeriazer(serializers.Serializer):
    business_name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(read_only=True) 
    inn_identification_number = serializers.CharField(max_length=50) #Инн продавца, slug будет обновляться при каждом изменении поля  business_name
    website_url = serializers.URLField(required=False, allow_null=True) #  URL-адрес сайта продавца
    phone_number =serializers.CharField(max_length=20)
    business_description = serializers.CharField()

    # Address Information
    business_address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20) # почтовый индекс

    # Bank Information
    bank_name =serializers.CharField(max_length=255)
    bank_bic_number = serializers.CharField(max_length=9)
    bank_account_number =serializers.CharField(max_length=50)
    bank_routing_number =serializers.CharField(max_length=50)

    is_approved = serializers.BooleanField(read_only=True)


