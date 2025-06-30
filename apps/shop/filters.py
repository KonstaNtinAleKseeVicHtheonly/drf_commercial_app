import django_filters
from rest_framework.exceptions import ValidationError

from apps.shop.models import Product


class ProductFilter(django_filters.FilterSet):
    '''кастомный фильтр для фильтрации товаров по цене'''
    max_price = django_filters.NumberFilter(field_name='price_current', lookup_expr='lte') # от max_price и ниже
    min_price = django_filters.NumberFilter(field_name='price_current', lookup_expr='gte') # от min_price и выше
    in_stock = django_filters.NumberFilter(lookup_expr='gte') # фильтрация по количеству товаров на складе(больше или равно заданному)
    created_at = django_filters.DateTimeFilter(lookup_expr='gte') # фильтрация по дате создания

    class Meta:
        model = Product
        fields = ['max_price','min_price','created_at']

    def filter_queryset(self, queryset):
        min_price = self.form.cleaned_data.get('min_price')
        max_price = self.form.cleaned_data.get('max_price')
        if min_price and max_price:
            if min_price >= max_price:
                raise ValidationError("минимальная цена должна быть больше максимальной")
        queryset = super().filter_queryset(queryset)
        return queryset