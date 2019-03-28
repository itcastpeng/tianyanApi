from django import forms
from bs4 import BeautifulSoup
from api import models
import json
from publicFunc.get_content_article import get_article


# 添加文章
class AddForm(forms.Form):
    create_user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '创建人不能为空'
        }
    )

    article_url = forms.CharField(
        required=True,
        error_messages={
            'required': '文章链接不能为空'
        }
    )

    classify_id = forms.CharField(
            required=True,
            error_messages={
                'required': "分类id不能为空"
            }
        )

    # 查询分类Id是否存在
    def clean_classify_id(self):
        classify_id = self.data['classify_id']
        classify_id = json.loads(classify_id)

        objs = models.Classify.objects.filter(
            id__in=classify_id,
        )
        if not objs:
            self.add_error('classify_id', '分类Id不存在')
        else:
            len_classify_id = len(classify_id)
            if len_classify_id <= 5:
                return classify_id
            else:
                self.add_error('classify_id', '标签最多不超过五个')

# 更新
class UpdateForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    title = forms.CharField(
        required=True,
        error_messages={
            'required': "标题不能为空"
        }
    )
    content = forms.CharField(
        required=True,
        error_messages={
            'required': "内容不能为空"
        }
    )
    # summary = forms.CharField(
    #     required=True,
    #     error_messages={
    #         'required': "简介不能为空"
    #     }
    # )

    # 查询文章标题是否存在
    def clean_o_id(self):
        create_user_id = self.data['create_user_id']
        o_id = self.data['o_id']        # 文章id
        print('o_id---------> ', o_id)
        objs = models.Article.objects.filter(
            create_user_id=create_user_id,
            id=o_id,
        )
        if not objs:
            self.add_error('o_id', '文章不存在')
        else:
            return o_id

    # # 查询文章标题是否存在
    # def clean_title(self):
    #     create_user_id = self.data['create_user_id']
    #     title = self.data['title']
    #     o_id = self.data['o_id']        # 文章id
    #     print('o_id -->', o_id)
    #     objs = models.Article.objects.filter(
    #         create_user_id=create_user_id,
    #         title=title,
    #     ).exclude(id=o_id)
    #     if objs:
    #         self.add_error('title', '标题已存在')
    #     else:
    #         return title

# 修改文章标签
class UpdateClassifyForm(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '文章id不能为空'
        }
    )

    classify_id = forms.CharField(
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
            # create_user_id=create_user_id,
            id=o_id,
        )
        if not objs:
            self.add_error('o_id', '文章不存在')
        else:
            return o_id

    # 查询分类Id是否存在
    def clean_classify_id(self):
        classify_id = self.data['classify_id']
        classify_id = json.loads(classify_id)
        len_classify_id = len(classify_id)
        if len_classify_id <= 5:
            return classify_id
        else:
            self.add_error('classify_id', '标签最多不超过五个')

# 查询
class SelectForm(forms.Form):
    id = forms.IntegerField(
        required=False,
        error_messages={
            'invalid': "文章ID类型错误"
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

    classify_type = forms.IntegerField(
        required=False,
        error_messages={
            'required': "分类类型不能为空",
            'invalid': "分类类型只能为整数"
        }
    )
    team_list = forms.CharField(
        required=False,
        error_messages={
            'invalid': "团队分类"
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
        id = self.data.get('id')
        classify_type = self.data.get('classify_type')
        team_list = self.data.get('team_list')
        if id:
            return id
        else:
            if team_list or classify_type:
                if team_list:
                    team_list = json.loads(team_list)
                    if len(team_list) >= 1:
                        print('=======================')
                        if models.UserprofileTeam.objects.filter(team__in=team_list):
                            return team_list
                        else:
                            self.add_error('team_list', '团队不存在')
                    else:
                        self.add_error('team_list', '团队ID不能为空')
                else:
                    if classify_type not in ["1", "2"]:
                        self.add_error('classify_id', '分类类型传参异常')
                    else:
                        return int(classify_type)
            else:
                self.add_error('classify_type', '请选择一项分类')

# 点赞
class GiveALike(forms.Form):
    article_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "该文章已被删除",
        }
    )
    customer_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "登录异常"
        }
    )
    user_id = forms.IntegerField(
        required=False,
        error_messages={
            'required': "登录异常"
        }
    )

    def clean_article_id(self):
        article_id = self.data.get('article_id')
        if models.Article.objects.filter(id=article_id):
            return article_id
        else:
            self.add_error('article_id', '文章不存在')

    def clean_customer_id(self):
        customer_id = self.data.get('customer_id')
        if customer_id:
            if models.Customer.objects.filter(id=customer_id):
                return customer_id
            else:
                self.add_error('customer_id', '请重新登录')

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        if user_id:
            objs = models.Userprofile.objects.filter(id=user_id)
            if objs:
                return user_id
            else:
                self.add_error('user_id', '非法用户')


# 热门查询
class PopulaSelectForm(forms.Form):
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

# 插入文章
class InsertContentForm(forms.Form):
    article_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "文章ID不能为空"
        }
    )
    def clean_article_id(self):
        article_id = self.data.get('article_id')
        objs = models.Article.objects.filter(id=article_id)
        if objs:
            return article_id
        else:
            self.add_error('article_id', '无此ID')

# 判断是否为自己的文章 (修改文章前 调用)
class DecideIfYourArticle(forms.Form):
    o_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "文章ID不能为空"
        }
    )
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'invalid': "登录异常"
        }
    )

    def clean_o_id(self):
        o_id = self.data.get('o_id')
        user_id = self.data.get('user_id')
        objs = models.Article.objects.filter(id=o_id)
        if not objs:
            self.add_error('o_id', '该文章已删除')
        else:
            obj = objs[0]
            flag = False
            if int(obj.create_user_id) == int(user_id):
                flag = True
            return flag
















