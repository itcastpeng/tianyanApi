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

    classify_type = forms.IntegerField(
        required=True,
        error_messages={
            'required': "分类类型不能为空",
            'invalid': "分类类型只能为整数"
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

    def clean_classify_type(self):
        classify_type = self.data.get('classify_type')
        # print('classify_type -->', classify_type, type(classify_type))
        if classify_type not in ["1", "2"]:
            self.add_error('classify_id', '分类类型传参异常')
        else:
            return int(classify_type)

