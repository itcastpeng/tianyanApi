from django import forms

from api import models
from publicFunc import account
import time


# 添加
class AddForm(forms.Form):
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )

    posters_url = forms.CharField(
        required=True,
        error_messages={
            'required': "海报链接不能为空"
        }
    )

    posters_status = forms.CharField(
        required=True,
        error_messages={
            'required': "海报类型不能为空"
        }
    )
    def clean_posters_url(self):
        posters_url = self.data.get('posters_url')
        posters_status = self.data.get('posters_status')
        objs = models.Posters.objects.filter(posters_url=posters_url, posters_status=posters_status)
        if not objs:
            return posters_url
        else:
            self.add_error('posters_url', '该海报已存在')

# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )

    posters_url = forms.CharField(
        required=True,
        error_messages={
            'required': "海报链接不能为空"
        }
    )

    posters_status = forms.CharField(
        required=True,
        error_messages={
            'required': "海报类型不能为空"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.Posters.objects.filter(id=o_id)
        if objs:
            return o_id, objs
        else:
            self.add_error('o_id', '修改ID不存在')
    def clean_posters_url(self):
        o_id = self.data.get('o_id')
        posters_url = self.data.get('posters_url')
        posters_status = self.data.get('posters_status')
        objs = models.Posters.objects.filter(posters_url=posters_url, posters_status=posters_status).exclude(id=o_id)
        if not objs:
            return posters_url
        else:
            self.add_error('posters_url', '该海报已存在')

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

