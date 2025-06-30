def set_dict_attr(obj, valid_data:dict):
    '''доп метод для ProfileView принимает объект пользователя и валидные данные для обновления
    записывает обновленные валидные данные в объект пользователя 
    при PUT запроса'''
    for k,v in valid_data.items():
        setattr(obj,k,v)
    return obj