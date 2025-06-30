from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from core import settings




PRODUCT_PARAM_EXAMPLE =[

    OpenApiParameter(
            name='max_price',
            description='Фильтрация по максимальной цене',
            required=False,
            type=OpenApiTypes.INT),
    OpenApiParameter(
            name='min_price',
            description='Фильтрация по минимальной цене',
            required=False,
            type=OpenApiTypes.INT),
    OpenApiParameter(
            name='in_stock',
            description='Фильтрация по количеству товара на складе',
            required=False,
            type=OpenApiTypes.INT),
    OpenApiParameter(
            name='created_at',
            description='Фильтрация по дате добавления товара',
            required=False,
            type=OpenApiTypes.DATE),
    OpenApiParameter(
        name="page",
        description="Возвращает определенную страницу (по умолчанию 1)",
        required=False,
        type=OpenApiTypes.INT,
    ), # возможность перехода по страницам
    OpenApiParameter(
        name="page_size",
        description=f"Количество товаров на странице для отображения. Defaults to {settings.REST_FRAMEWORK['PAGE_SIZE']}",
        required=False,
        type=OpenApiTypes.INT,
    )
]