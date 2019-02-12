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

    # 查询当前用户是否在该团队中存在且具有管理权限
    def clean_o_id(self):
        user_id = self.data['user_id']
        o_id = self.data['o_id']        # 团队id
        objs = models.UserprofileTeam.objects.filter(
            team_id=o_id,
            user_id=user_id,
            type=2
        )

        if not objs:
            self.add_error('o_id', '权限不足')
        else:
            return o_id


# 删除团队成员
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

    # 查询当前用户是否在该团队中存在且具有管理权限
    def clean_o_id(self):
        user_id = self.data['user_id']
        o_id = self.data['o_id']        # 团队id
        objs = models.UserprofileTeam.objects.filter(
            type=2,
            team_id=o_id,
            user_id=user_id
        )

        if not objs:
            self.add_error('o_id', '权限不足')
        else:
            return o_id

    # 查询被移除的成员是否在该团队中存在
    def clean_delete_user_id(self):
        delete_user_id = self.data['delete_user_id']
        o_id = self.data['o_id']  # 团队id

        objs = models.UserprofileTeam.objects.filter(
            type=1,
            team_id=o_id,
            user_id=delete_user_id
        )

        if not objs:
            self.add_error('delete_user_id', '成员不存在')
        else:
            return delete_user_id


# 设置普通成员成为管理员
class SetManagementForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '团队id不能为空'
        }
    )

    set_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "成员id不能为空"
        }
    )

    # 查询当前用户是否在该团队中存在且具有管理权限
    def clean_o_id(self):
        user_id = self.data['user_id']
        o_id = self.data['o_id']        # 团队id
        objs = models.UserprofileTeam.objects.filter(
            type=2,
            team_id=o_id,
            user_id=user_id
        )

        if not objs:
            self.add_error('o_id', '权限不足')
        else:
            return o_id

    # 查询被移除的成员是否在该团队中存在
    def clean_set_user_id(self):
        set_user_id = self.data['set_user_id']
        o_id = self.data['o_id']  # 团队id

        objs = models.UserprofileTeam.objects.filter(
            type=1,
            team_id=o_id,
            user_id=set_user_id
        )

        if not objs:
            self.add_error('set_user_id', '成员不存在')
        else:
            return set_user_id


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
class SelectUserListForm(forms.Form):
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
