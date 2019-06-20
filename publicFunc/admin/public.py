

from api import models
from publicFunc.public import length_the_days


def create_member_price(user_id):
    # 创建默认会员价格
    data = [
        {
            'the_length': 1,
            'price': 99,
            'original_price': 199,
        },
        {
            'the_length': 2,
            'price': 299,
            'original_price': 499,
        },
        {
            'the_length': 3,
            'price': 599,
            'original_price': 999,
        },
    ]
    for i in data:
        the_length, renewal_number_days = length_the_days(i.get('the_length'))
        models.renewal_management.objects.create(
            create_user_id=user_id,
            price=i.get('price'),
            original_price=i.get('original_price'),
            renewal_number_days=renewal_number_days,
            the_length=the_length,
        )
