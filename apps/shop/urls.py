from django.urls import path, include
from apps.shop.views import CategoryView, ProductsByCategoryView, AllStoreProductsView, ProductsBySellerView, CertainProductView, CartView, CheckoutView, CreateReviewView, ProductReviewView, ReviewDetailAPIView


app_name = 'shop_info'
urlpatterns = [
    path('categories/',CategoryView.as_view()), #категории товаров
    path('categories/<slug:slug>/', ProductsByCategoryView.as_view()),# все товары по указанной категории
    path('all_products/', AllStoreProductsView.as_view()), # все товары из магазина
    path('seller/<slug:slug>/', ProductsBySellerView.as_view()), # все товары указанного продавца
    path('product/<slug:slug>/', CertainProductView.as_view()), # инфа об определенном товаре
    path('cart/', CartView.as_view()), # взаимодействие с корзиной юзера
    path('create_order/', CheckoutView.as_view()), # созадния заказа юзера из его корзины
    path('create_review/<slug:slug>/', CreateReviewView.as_view()), # создание отзыва о товаре по его slug
    path('product_reviews/<slug:slug>/', ProductReviewView.as_view()), # покажет отзывы по указанному товару
    path('detail_review/<str:review_id>/', ReviewDetailAPIView.as_view()) # показ, изменение, удаление отзыва по его id 

]