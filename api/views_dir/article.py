from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.article import AddForm, UpdateForm, SelectForm, UpdateClassifyForm, GiveALike, PopulaSelectForm
from django.db.models import Q
from publicFunc.weixin import weixin_gongzhonghao_api
from publicFunc import base64_encryption
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.account import get_token
from django.shortcuts import render, redirect
from publicFunc.host import host_url
from publicFunc.get_content_article import get_content_article
import requests, datetime, random, json


# token验证 用户展示模块
@account.is_token(models.Userprofile)  # 用户登录 直接跳转文章 页面 （判断是否为新用户）
def article(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    team_list = request.GET.get('team_list')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'title': '__contains',
                'classify_id': '__in',
                'create_user_id': '__in',
                'create_datetime': '',
                'source_link': '',
            }
            q = conditionCom(request, field_dict)
            classify_type = forms_obj.cleaned_data.get('classify_type')    # 分类类型，1 => 推荐, 2 => 品牌
            user_obj = models.Userprofile.objects.get(id=user_id)

            classify_objs = None
            if classify_type == 1:  # 推荐分类
                classify_objs = user_obj.recommend_classify.all()
            elif classify_type == 2:    # 品牌分类
                classify_objs = user_obj.brand_classify.all()

            article_list = []
            # 团队
            if team_list and len(team_list) >= 1:
                team_objs = models.UserprofileTeam.objects.filter(team_id__in=json.loads(team_list)).values('user_id').distinct()
                team_user_list = []
                for team_obj in team_objs:
                    team_user_list.append(team_obj['user_id'])
                print('team_user_list--------------> ', team_user_list )
                team_user_objs = models.users_forward_articles.objects.filter(user_id__in=team_user_list)
                for i in team_user_objs:
                    article_list.append(i.share_article_id)
                print('article_list----------------> ', article_list)
                q.add(Q(**{'id__in':article_list}), Q.AND)

            print('classify_objs------------> ', classify_objs)
            if classify_objs:
                classify_id_list = [obj.id for obj in classify_objs]
                print("classify_id_list -->", classify_id_list)
                if len(classify_id_list) > 0:
                    q.add(Q(**{'classify_id__in': classify_id_list}), Q.AND)


            print('q -->', q)
            if q:
                objs = models.Article.objects.select_related('classify').filter(q).order_by(order)
            else:
                objs = models.Article.objects.select_related('classify').filter(
                    create_datetime__isnull=False
                ).order_by('like_num')
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            id = request.GET.get('id')
            # 返回的数据s
            ret_data = []
            for obj in objs:

                result_data = {
                    'id': obj.id,
                    'title': obj.title,
                    'look_num': obj.look_num,
                    'like_num': obj.like_num,
                    'classify_id': obj.classify_id,
                    'classify_name': obj.classify.name,
                    'create_user_id': obj.create_user_id,
                    'cover_img': obj.cover_img,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                }
                if id: # 如果查询详情 返回文章内容 否则数据过大
                    result_data['content'] = eval(json.loads(obj.content))

                if team_list and len(team_list) >= 1: # 如果查询 团队 则返回 文章创建人头像和名称
                    result_data['create_user__name'] = obj.create_user.name
                    result_data['create_user__set_avator'] = obj.create_user.set_avator

                #  将查询出来的数据 加入列表
                ret_data.append(result_data)

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }

            response.note = {
                'id': "文章id",
                'title': "文章标题",
                'content': "文章内容",
                'look_num': "查看次数",
                'like_num': "点赞(喜欢)次数",
                'classify_id': "所属分类id",
                'classify_name': "所属分类名称",
                'create_datetime': "创建时间",
                'cover_img': "封面图",
                'create_user_id': "创建人ID",
                'create_user__name': "创建人姓名",
                'create_user__set_avator': "创建人头像",
            }
        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加文章
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
                'classify_id': request.POST.get('classify_id'),
                'top_advertising': request.POST.get('top_advertising'),
                'end_advertising': request.POST.get('end_advertising'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                #  添加数据库
                print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)

                obj = models.Article.objects.create(**forms_obj.cleaned_data)

                cover_img_list = [
                    'http://tianyan.zhangcong.top/statics/img/f4578f133cd9fc4b88449b1e373c5d4cnews4.png',
                    'http://tianyan.zhangcong.top/statics/img/ca47a146ff6b6b7f45742742326075cdnews3.png',
                    'http://tianyan.zhangcong.top/statics/img/651397a20f5f8fe15b1c12cf150ff3d3news2.png',
                    'http://tianyan.zhangcong.top/statics/img/a105a02aff72958b5cfb0fca97e4363anews1.png',
                    'http://tianyan.zhangcong.top/statics/img/1f75da72013edbb7fcaae9660ca55cbenews5.png'
                                  ]
                cover_img = random.sample(cover_img_list, 1)

                obj.cover_img = cover_img[0]
                obj.save()
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())


        # 修改文章
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,   # 文章id
                'create_user_id': user_id,
                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                title = forms_obj.cleaned_data['title']
                content = forms_obj.cleaned_data['content']

                #  查询更新 数据
                models.Article.objects.filter(id=o_id).update(
                    title=title,
                    content=content,
                )

                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改文章所属分类
        elif oper_type == "update_classify":
            form_data = {
                'o_id': o_id,  # 文章id
                'create_user_id': user_id,
                'classify_id': request.POST.get('classify_id'),
            }

            forms_obj = UpdateClassifyForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                classify_id = forms_obj.cleaned_data['classify_id']

                #  查询更新 数据
                models.Article.objects.filter(id=o_id).update(
                    classify_id=classify_id,
                )
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())


    else:
        # 热门文章查询
        if oper_type == 'popula_articles':
            form_obj = PopulaSelectForm(request.GET)
            if form_obj.is_valid():
                current_page = form_obj.cleaned_data['current_page']
                length = form_obj.cleaned_data['length']
                objs = models.Article.objects.filter(title__isnull=False).order_by('look_num')
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]


                count = objs.count()
                #  将查询出来的数据 加入列表
                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'id': obj.id,
                        'title': obj.title,
                        # 'content': obj.content,
                        # 'look_num': obj.look_num,
                        # 'like_num': obj.like_num,
                        # 'classify_id': obj.classify_id,
                        # 'classify_name': obj.classify.name,
                        'cover_img': obj.cover_img,
                        # 'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data':ret_data,
                    'count':count
                }
                response.note = {
                    'title': '文章标题',
                    'cover_img': '文章封面'
                }
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())


        # 放入文章链接 获取所有内容(添加文章之前调用)
        elif oper_type == 'get_content_article':
            article_url = request.GET.get('article_url')
            data_dict = get_content_article(article_url)

            response.code = 200
            response.msg = '获取内容成功'
            response.data = {'data_dict': data_dict}

        # 临时转换文章内容为数组(开发期间更改需求 临时转换)
        # elif oper_type == 'linshi':
        #     objs = models.Article.objects.all()
        #     for obj in objs:
        #         soup = BeautifulSoup(obj.content, 'lxml')
        #         p_tag = soup.find_all('p')
        #         content = []
        #         for i in p_tag:
        #             content.append(str(i))
        #         print(content)
        #         content = json.dumps(str(content))
        #         obj.content = content
        #         obj.save()
        #     response.code = 200

        # 放入 文章链接 返回文章 所有内容

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)

# 点赞/取消点赞
def give_a_like(request):
    response = Response.ResponseObj()
    form_data = {
        'article_id': request.GET.get('article_id'),
        'customer_id': request.GET.get('customer_id')
    }

    form_obj = GiveALike(form_data)
    if form_obj.is_valid():
        customer_id = form_obj.cleaned_data.get('customer_id')
        article_id = form_obj.cleaned_data.get('article_id')

        objs = models.SelectClickArticleLog.objects.filter(customer_id=customer_id, article_id=article_id)

        response.code = 200
        response.msg = '点赞成功'
        if objs:
            if objs[0].is_click:
                is_click = False
                response.msg = '取消点赞'
            else:
                is_click = True
            objs.update(is_click=is_click)
        else:
            models.SelectClickArticleLog.objects.create(**{
                'customer_id':customer_id,
                'article_id':article_id
            })

    return JsonResponse(response.__dict__)


# 客户打开 用户分享的文章 (嵌入微信url 获取用户信息 匹配openid 判断数据库是否存在 跳转文章页)
def share_article(request, o_id):
    code = request.GET.get('code')
    print('code---------code----------code---> ', code)
    inviter_user_id = request.GET.get('state')  # 分享文章的用户id
    article_id = o_id                           # 分享文章的id
    weichat_api_obj = weixin_gongzhonghao_api.WeChatApi()
    ret_obj = weichat_api_obj.get_openid(code)
    openid = ret_obj.get('openid')

    user_data = {
        "sex": ret_obj.get('sex'),
        "country": ret_obj.get('country'),
        "province": ret_obj.get('province'),
        "city": ret_obj.get('city'),
    }
    customer_objs = models.Customer.objects.filter(openid=openid)
    if customer_objs:   # 客户已经存在
        customer_objs.update(**user_data)
        customer_obj = customer_objs[0]
    # 不存在，创建用户
    else:
        encode_username = base64_encryption.b64encode(
            ret_obj['nickname']
        )

        subscribe = ret_obj.get('subscribe')

        # 如果没有关注，获取个人信息判断是否关注
        if not subscribe:
            weichat_api_obj = WeChatApi()
            ret_obj = weichat_api_obj.get_user_info(openid=openid)
            subscribe = ret_obj.get('subscribe')

        user_data['set_avator'] = ret_obj.get('headimgurl')
        user_data['subscribe'] = subscribe
        user_data['name'] = encode_username
        user_data['openid'] = ret_obj.get('openid')
        user_data['token'] = get_token()
        print("user_data --->", user_data)
        customer_obj = models.Customer.objects.create(**user_data)

    # 创建浏览文章记录
    models.SelectArticleLog.objects.create(
        customer=customer_obj,
        article_id=article_id,
        inviter_id=inviter_user_id
    )

    objs = models.Customer.objects.filter(openid=openid)
    obj = objs[0]

    # 此处跳转到文章页面
    redirect_url = '{host_url}/article?user_id={user_id}&token={token}&id={article_id}'.format(
        host_url=host_url,
        article_id=article_id,
        user_id=inviter_user_id,
        token=obj.token,
    )
    return redirect(redirect_url)








