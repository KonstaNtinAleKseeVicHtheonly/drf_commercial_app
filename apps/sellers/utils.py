def update_seller_product(obj,validated_data:dict):
    '''обновляет данные указанного объекта + перезапись старой цены при изменении текущей'''
    for k,v in validated_data.items():
        if k == 'price_current':
            if obj.price_current != v:
                obj.price_old = obj.price_current
                setattr(obj,k,v)
        else:
            setattr(obj,k,v)
    return obj
