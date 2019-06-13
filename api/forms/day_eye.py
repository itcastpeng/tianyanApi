from django import forms

from api import models
# from publicFunc import account
import datetime
from publicFunc.emoji import baiyan

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
            'required': "页显示数量类型错误"
        }
    )

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        objs = models.Userprofile.objects.filter(id=user_id)
        if objs and objs[0].overdue_date:
            now_date = datetime.date.today()
            if objs[0].overdue_date >= now_date: # 未过期

                # 时间对象 - 年月日时分秒
                now_datetime_obj = datetime.datetime.now()

                # 时间对象 - 年月日
                now_date_obj = datetime.date(now_datetime_obj.year, now_datetime_obj.month, now_datetime_obj.day)

                # 计算剩余天数
                remaining_days = (objs[0].overdue_date - now_date_obj).days
                msg = ''


                if remaining_days <= 7:
                    if objs[0].overdue_date == now_date: # 今天到期
                        remaining_text = '今'
                    else:
                        remaining_text = '剩余{}'.format(remaining_days)
                    msg = '您的会员' + remaining_text + '天到期, 为避免正常使用, 请及时续费{}'.format(baiyan)

                return user_id, msg
            else:
                self.add_error('user_id', '您的会员已经到期, 为了避免您的正常使用, 请续费继续使用')
                objs.update(vip_type=0)
        else:
            if not objs:
                self.add_error('user_id', '非法用户')
            else:
                self.add_error('user_id', '您的会员已经到期, 为了避免您的正常使用, 请续费继续使用')

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


# 添加客户备注
class AddForm(forms.Form):
    remote = forms.CharField(
        required=True,
        error_messages={
            'required': "备注不能为空"
        }
    )
    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )



# 修改客户备注
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )

    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )

    remote = forms.CharField(
        required=True,
        error_messages={
            'required': "备注不能为空"
        }
    )

    customer_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "客户不能为空"
        }
    )
    def clean_o_id(self):
        o_id = self.data.get('o_id')
        objs = models.customer_information_the_user.objects.filter(id=o_id)
        if objs:
            return o_id
        else:
            self.add_error('o_id', '数据异常')


class Form(forms.Form):
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
