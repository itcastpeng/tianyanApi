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

    # 查询当前用户是否在该团队中存在
    def clean_o_id(self):
        user_id = self.data['user_id']
        o_id = self.data['o_id']        # 团队id
        team_obj = models.Team.objects.get(id=o_id)
        user_objs = team_obj.userprofile_team.filter(id=user_id)

        if not user_objs:
            self.add_error('o_id', '团队不存在')
        else:
            return o_id


# 更新
class DeleteMemberForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '团队id不能为空'
        }
    )

    delete_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "成员id不能为空"
        }
    )

    # 查询当前用户是否在该团队中存在
    def clean_o_id(self):
        user_id = self.data['user_id']
        o_id = self.data['o_id']        # 团队id
        team_obj = models.Team.objects.get(id=o_id)
        user_objs = team_obj.userprofile_team.filter(id=user_id)

        if not user_objs:
            self.add_error('o_id', '团队不存在')
        else:
            return o_id

    # 查询被移除的成员是否在该团队中存在
    def clean_delete_user_id(self):
        delete_user_id = self.data['delete_user_id']
        o_id = self.data['o_id']  # 团队id
        team_obj = models.Team.objects.get(id=o_id)
        user_objs = team_obj.userprofile_team.filter(id=delete_user_id)

        if not user_objs:
            self.add_error('o_id', '删除成员不在该团队中')
        else:
            return o_id


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


# 查看团队人员列表
class SelectUserList(forms.Form):
    team_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "页码数据类型错误",
            'required': "团队id不能为空"
        }
    )

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
