from django.db import models
from django.utils import timezone

# Create your models here.
import uuid


from apps.common.managers import GetOrNoneManager, IsDeletedManager

class BaseModel(models.Model):
    '''Базовый Абстрактный класс, содержащий общие поля и методы для всех реальных моделей
    (id, created_at, updated_at)
    '''
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False) # генерация уникального перичного ключа модели с улучшенным поиском по id
    created_at = models.DateTimeField(auto_now_add=True) # автоматически обновляет дату и время создани объекта
    updated_at = models.DateTimeField(auto_now=True)# автоматически обновляет дату и время последнего изменения объекта

    objects = GetOrNoneManager() # привязка кастомного менеджера моделей к базовому классу

    class Meta:
        abstract = True # это абстрактный класс, таблица этого класса не будет создаваться в БД

class IsDeletedModel(BaseModel):
    '''Расширение абстрактного Базового класса'''
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = IsDeletedManager()# привзка кастомного енеджера с логикой мягкого и жесткого удаления объектов

    class Meta:
        ordering = ['-id'] # отсортировка по убыванию данных queryset, что бы не было ошибок пагинации
        abstract = True

    def delete(self, *args, **kwargs):
        '''мягкое удаление is_deleted=True'''
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted','deleted_at'])

    def hard_delete(self, *args, **kwargs):
        '''полное, жесткое удаление всей инфы о записи'''
        super().deleter(*args, **kwargs)
