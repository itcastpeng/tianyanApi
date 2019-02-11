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

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "团队名称不能为空"
        }
    )


# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '团队id不能为空'
        }
    )

    name = forms.CharField(
        required=True,
        error_messages={
            'required': "团队名称不能为空"
        }
    )

    # 查询文章标题是否存在
    def clean_o_id(self):
        user_id = self.data['user_id']
        o_id = self.data['o_id']        # 团队id
        team_obj = models.Team.objects.get(id=o_id)
        user_objs = team_obj.userprofile_team.filter(id=user_id)

        if not user_objs:
            self.add_error('o_id', '团队不存在')
        else:
            return o_id


class UpdateClassifyForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    classify_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "分类id不能为空"
        }
    )

    # 查询文章标题是否存在
    def clean_o_id(self):
        create_user_id = self.data['create_user_id']
        o_id = self.data['o_id']

        objs = models.Article.objects.filter(
            create_user_id=create_user_id,
            id=o_id,
        )
        if not objs:
            self.add_error('o_id', '文章不存在')
        else:
            return o_id

    # 查询分类Id是否存在
    def clean_classify_id(self):
        classify_id = self.data['classify_id']

        objs = models.Classify.objects.filter(
            id=classify_id,
        )
        if not objs:
            self.add_error('classify_id', '分类Id不存在')
        else:
            return classify_id


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

    id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "查询ID类型错误",
        }
    )
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户",
        }
    )
    timestamp = forms.CharField(
        required=True,
        error_messages={
            'required': "非法用户",
        }
    )
    rand_str = forms.CharField(
        required=True,
        error_messages={
            'required': "非法用户",
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

    def clean_id(self): # 判断是否为客户查看
        id = self.data.get('id')
        user_id = self.data.get('user_id')
        data = {
            'user_id':user_id,
            'rand_str':self.data.get('rand_str'),
            'timestamp':self.data.get('timestamp')
        }
        flag = account.customer_is_token(models.Customer, data)
        if flag:
            print('=-==============')