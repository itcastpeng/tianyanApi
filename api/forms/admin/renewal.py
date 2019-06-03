from api import models
from django import forms
from publicFunc.public import length_the_days


# 添加
class AddForm(forms.Form):
    price = forms.IntegerField(
        required=True,
        error_messages={
            'required': '价格不能为空'
        }
    )

    the_length = forms.IntegerField(
        required=True,
        error_messages={
            'required': "时长不能为空"
        }
    )
    original_price = forms.IntegerField(
        required=True,
        error_messages={
            'required': "原价不能为空"
        }
    )
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )
    def clean_the_length(self):
        the_length = self.data.get('the_length')
        user_id = self.data.get('user_id')
        obj = models.renewal_management.objects.filter(
            create_user_id=user_id,
            the_length=the_length
        )
        if not obj:
            the_length, renewal_number_days = length_the_days(the_length)
            return the_length, renewal_number_days
        else:
            self.add_error('the_length', '重复添加')

    def clean_price(self):
        price = self.data.get('price')
        if '.' in price:
            self.add_error('price', '价钱必须为整数')
        else:
            return price


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    price = forms.IntegerField(
        required=True,
        error_messages={
            'required': '价格不能为空'
        }
    )

    original_price = forms.IntegerField(
        required=True,
        error_messages={
            'required': "原价不能为空"
        }
    )
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.renewal_management.objects.filter(id=o_id)
        if objs:
            return o_id, objs
        else:
            self.add_error('o_id', '修改ID不存在')


    def clean_price(self):
        price = self.data.get('price')
        if '.' in price:
            self.add_error('price', '价钱必须为整数')
        else:
            return price

# 删除
class DeleteForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "修改ID不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.renewal_management.objects.filter(id=o_id)
        if objs:
            return o_id, objs
        else:
            self.add_error('o_id', '删除ID不存在')


# 查询
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
