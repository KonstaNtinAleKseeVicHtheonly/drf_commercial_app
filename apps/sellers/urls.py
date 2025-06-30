from django.urls import path
from apps.sellers.views import SellerView,  SellerProductsView, SellerProductView, SellerOrdersView, SellerItemOrderView

app_name = 'all_sellers'

urlpatterns = [

    path('', SellerView.as_view()),
    path('products/', SellerProductsView.as_view()),
    path('product/<slug:slug>/', SellerProductView.as_view()),
    path('orders/',SellerOrdersView.as_view()), # получение всех заказов связанных с продавцом по данному юзеру
    path('order/<str:tx_ref>/', SellerItemOrderView.as_view()) # получение опред заказа, связанного с продавцом по текущему юзеру
    
]
