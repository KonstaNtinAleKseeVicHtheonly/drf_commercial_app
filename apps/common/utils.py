import secrets

from apps.common.models import BaseModel

def generate_unique_code(model:BaseModel, field:str)->str:
    '''Метод для генерации уникального кода для идентификатора транзакции товара
    Принимает ЭК модели BaseModel  и имя строки для проверки наникальность'''

    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    unique_code = "".join(secrets.choice(allowed_chars) for elem in range(12))
    similar_object_exists = model.objects.filter(**{field: unique_code}).exists()
    if not similar_object_exists: # если нет совпадений, значит уникальный код сгенрирован
        return unique_code
    return generate_unique_code(model, field) # если такйо код уже есть будет рекурсия до содания уникального кода
