from django import forms
from publicFunc.public import verify_mobile_phone_number
from api import models
from publicFunc import account
import time




# 普通用户添加
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
    appid = forms.CharField(
        required=False,
        error_messages={
            'required': "appid类型错误"
        }
    )
    appsecret = forms.CharField(
        required=False,
        error_messages={
            'required': "appsecret类型错误"
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

    def clean_password(self):
        password = self.data['password']
        return account.str_encrypt(password)

    def clean_token(self):
        password = self.data['password']
        return account.get_token(password + str(int(time.time()) * 1000))

    # def clean_department_id(self):
    #     department_id = self.data.get('department_id')
    #     objs = models.department.objects.filter(id=department_id)
    #     if objs:
    #         return department_id
    #     else:
    #         self.add_error('department_id', '该部门不存在')
    def clean_signature(self):
        signature = self.data.get('signature')
        if signature:
            signature_len = len(signature)
            if signature_len > 50:
                self.add_error('signature', '个性签名长度不能超过50')
            else:
                return signature
    def clean_phone(self):
        phone = self.data.get('phone')
        if phone:
            if verify_mobile_phone_number(phone):
                return phone
            else:
                self.add_error('phone', '请输入正确手机号')

# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '修改id不能为空'
        }
    )

    username = forms.CharField(
        required=True,
        error_messages={
            'required': "用户名不能为空"
        }
    )

    role_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "角色名称不能为空"
        }
    )
    oper_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '操作人不能为空'
        }
    )
    set_avator = forms.CharField(
        required=False,
        error_messages={
            'required': "头像类型错误"
        }
    )

    phone = forms.CharField(
        required=False,
        error_messages={
            'required': "电话类型错误"
        }
    )

    def clean_signature(self):
        signature = self.data.get('signature')
        if signature:
            signature_len = len(signature)
            if signature_len > 50:
                self.add_error('signature', '个性签名长度不能超过50')
            else:
                return signature

    # 判断名称是否存在
    def clean_username(self):
        o_id = self.data['o_id']
        username = self.data['username']
        objs = models.userprofile.objects.filter(
            username=username,
        ).exclude(
            id=o_id
        )
        if objs:
            self.add_error('username', '用户名已存在')
        else:
            return username
    # def clean_department_id(self):
    #     department_id = self.data.get('department_id')
    #     objs = models.department.objects.filter(id=department_id)
    #     if objs:
    #         return department_id
    #     else:
    #         self.add_error('department_id', '该部门不存在')

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




