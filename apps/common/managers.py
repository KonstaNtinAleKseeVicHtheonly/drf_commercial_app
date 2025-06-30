'''Файл менеджер для объектов проекта'''
from django.db import models
from django.utils import timezone

class GetOrNoneQuerySet(models.QuerySet):
    '''Расширяет функционал моделей, добавляя метод get_or_none.
    Класс срабатывает при вызове MOdel.objects.method() + get_or_none()
    и позволяет вызывать метод после применения доп фильтров'''

    def get_or_none(self, **kwargs):
        '''проверка существования модели при запросе в QuerySet, теперь при 
        несуществующей модели вернется None а не ошибка DoesNotExist'''
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
        
class GetOrNoneManager(models.Manager):
    '''Собственный менеджер для управления нашим кастомным QuerySet(при вызове Model.objects.all() сохранится расширенный функционал).
    Класс срабатывает при вызове Model.objects + method()
    срабатывает чисто на Model.objects без фильтров'''

    def get_queryset(self):
        '''перепоределил метод, что бы все запросы проходили через наш кастомный QuerySet
        (подклюение QuerySet к моделям)'''
        return GetOrNoneQuerySet(self.model)
    
    def get_or_none(self, **kwargs):
        '''Свяазали метод с нашим кастомным QuerySet, что бы этот метод  срабатывал как Model.objects.get_or_none()'''
        return self.get_queryset().get_or_none(**kwargs)
    
class IsDeletedQuerySet(GetOrNoneQuerySet):
    '''Queryset для расширения логики удаления объектов.
    Реалиовано мягкое удаление(сокрытие полей модели без их полного удаления из БД)'''

    def delete(self, hard_delete=False):
        '''реализация мягкого и жесткого удаления ЕДИИЧНОГО объекта'''
        if hard_delete:
            return super.delete() # полное удаление из БД
        else:
            return self.update(is_deleted=True, deleted_at=timezone.now()) # мягкое удаление с сохранением полей из БД
        
        
class IsDeletedManager(GetOrNoneManager):
    def get_queryset(self):
        return IsDeletedQuerySet(self.model).filter(is_deleted=False)  # сокрытие удаленных объектов из поиска
    
    def unfiltered(self):
        '''Возомжнность получнеия всех запесей, даже удаленных(мягко) '''
        return IsDeletedQuerySet(self.model)
    
    def hard_delete(self):
        '''физическое удаление всех записей, даже мягко удаленных'''
        return self.unfiltered().delete(hard_delete=True)