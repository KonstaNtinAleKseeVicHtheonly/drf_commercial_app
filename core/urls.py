"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
# для работы swager OpenAPI
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"), # сырое json отображение OpenAPI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"), # графический интерфейс отображения OpenAPI для просмотра и тестирования
    path('auth/', include('apps.accounts.urls',namespace='all_accounts')),
    path('profiles/', include('apps.profiles.urls', namespace='all_profiles')),
    path('sellers/', include('apps.sellers.urls', namespace='all_sellers')),
    path('shop/', include('apps.shop.urls', namespace='shop_info'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # путь до папки с меди файлами проекта
