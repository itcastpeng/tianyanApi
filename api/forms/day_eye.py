from django import forms

from api import models
from publicFunc import account
import time, datetime



# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "页显示数量类型错误"
        }
    )
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        objs = models.Userprofile.objects.filter(id=user_id)
        if objs and objs[0].overdue_date:
            now_date = datetime.date.today()
            if objs[0].overdue_date >= now_date:
                return user_id
            else:
                self.add_error('user_id','您的会员已经到期, 为了避免您的正常使用, 请续费')
        else:
            if not objs:
                self.add_error('user_id', '非法用户')
            else:
                self.add_error('user_id', '您的会员已经到期, 为了避免您的正常使用, 请续费')

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length
