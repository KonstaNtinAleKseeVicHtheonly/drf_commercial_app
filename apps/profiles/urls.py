
from django.urls import path, include
from apps.profiles.views import ProfileView, DeliveryAddressView, DeliveryAddressViewID, OrderItemView, OrdersView
app_name = 'all_profiles'

urlpatterns = [

    path('', ProfileView.as_view()),
    path('delivery_addresses/', DeliveryAddressView.as_view()),
    path('delivery_addresses/detail/<uuid:id>/', DeliveryAddressViewID.as_view()),
    path('orders/',OrdersView.as_view()),
    path('order/<str:tx_ref>/', OrderItemView.as_view())
]

