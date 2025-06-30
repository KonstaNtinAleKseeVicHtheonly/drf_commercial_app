from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    '''Разрешение на изменени только владельцу объетка или одмэну'''
    def has_permission(self, request, view):
        '''имеет ли юзер права доступа в целом(только авторизированный)'''
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        '''явялется ли пользователь владельцем указанного объекта'''
        return request.user == obj.user or request.user.is_staff

class IsSeller(permissions.BasePermission):
    '''РАзрешение продавцов на просмотр и изменение только их товаров'''

    def has_permission(self, request, view):
        if (request.user.type == 'SELLER' and request.user.seller.is_approved and request.user.is_authenticated) or request.user.is_staff:
            return True

    def has_object_permission(self, request, view, obj):
        return request.user.seller == obj.seller or request.user.is_staff
    
class IsAdminorReadOnly(permissions.BasePermission):
    '''класс разрешает чтение всем юзерам а изменение только админу'''
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (request.user and request.user.is_staff) # request.user нужен что бы не возникла ошибка при попытке изменения анонимным юзером

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user and request.user.is_staff)
    
class CartandOrderPermission(permissions.BasePermission):
    '''разрешение создавать корзины и заказы только авторизированным юзерам'''
    def has_permission(self, request, view):
        return request.user and (request.user.is_authenticated or request.user.is_staff)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user and (request.user == obj.user or request.user.is_staff)
        return request.user == obj.user

