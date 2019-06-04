from django import forms
from publicFunc.public import verify_mobile_phone_number
from api import models
from publicFunc import account
import time


# 添加用户
class AddForm(forms.Form):
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    password = forms.CharField(
        required=True,
        error_messages={
            'required': "密码不能为空"
        }
    )

    role = forms.IntegerField(
        required=True,
        error_messages={
            'required': "角色名称不能为空"
        }
    )

    token = forms.IntegerField(
        required=False
    )

    phone = forms.CharField(
        required=True,
        error_messages={
            'required': "电话号码不能为空"
        }
    )

    # 查询名称是否存在
    def clean_name(self):
        name = self.data.get('name')
        objs = models.Enterprise.objects.filter(
            name=name,
        )
        if objs:
            self.add_error('name', '用户名已存在')
        else:
            return name

    def clean_token(self):
        password = self.data.get('password')
        return account.get_token(password + str(int(time.time()) * 1000))

    def clean_phone(self):
        phone = self.data.get('phone')
        if phone:
            if verify_mobile_phone_number(phone):
                return phone
            else:
                self.add_error('phone', '请输入正确手机号')

    def clean_password(self):
        password = self.data.get('password')
        return account.str_encrypt(password)


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '修改id不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    phone = forms.CharField(
        required=False,
        error_messages={
            'required': "电话类型错误"
        }
    )

    # 判断名称是否存在
    def clean_name(self):
        o_id = self.data['o_id']
        name = self.data.get('name')
        objs = models.Enterprise.objects.filter(
            name=name,
        ).exclude(
            id=o_id
        )
        if objs:
            self.add_error('name', '用户名已存在')
        else:
            return name


    def clean_phone(self):
        phone = self.data.get('phone')
        if phone:
            if verify_mobile_phone_number(phone):
                return phone
            else:
                self.add_error('phone', '请输入正确手机号')




# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
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

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        obj = models.Enterprise.objects.get(id=user_id)

        return user_id, obj.role



