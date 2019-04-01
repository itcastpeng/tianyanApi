from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.article import AddForm, UpdateForm, SelectForm, UpdateClassifyForm, GiveALike, PopulaSelectForm, DecideIfYourArticle, select_form
from django.db.models import Q, F
from publicFunc.base64_encryption import b64decode, b64encode
# from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
# from publicFunc.account import get_token
# from django.shortcuts import render, redirect
from publicFunc.article_oper import give_like
from publicFunc.get_content_article import get_article
from publicFunc.forwarding_article import forwarding_article
import requests, datetime, random, json

# token验证 文章展示模块
@account.is_token(models.Userprofile)
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
                'classify': '',
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

                team_user_objs = models.Article.objects.filter(create_user_id__in=team_user_list)   # 查询该团队 所有文章
                for i in team_user_objs:
                    article_list.append(i.id)

                q.add(Q(**{'id__in':article_list}), Q.AND)
            if classify_objs:
                classify_id_list = [obj.id for obj in classify_objs]
                if len(classify_id_list) > 0:
                    q.add(Q(**{'classify__in': classify_id_list}), Q.AND)

            print('q -->', q)
            if q:
                objs = models.Article.objects.filter(
                    q,
                ).order_by(order)
            else:
                objs = models.Article.objects.filter(
                    create_datetime__isnull=False
                ).order_by('like_num')
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            id = request.GET.get('id')
            # 返回的数据
            ret_data = []
            for obj in objs:
                is_like = False # 是否点赞
                log_obj = models.SelectClickArticleLog.objects.filter(
                    article_id=obj.id,
                    user_id=user_id
                )
                if log_obj:
                    is_like = True

                classify_id_list = []
                classify_name_list = []
                if obj.classify:
                    classify_id_list = [obj.get('id') for obj in obj.classify.values('id')]
                    classify_name_list = [obj.get('name') for obj in obj.classify.values('name')]

                result_data = {
                    'id': obj.id,
                    'title': obj.title,
                    'summary': obj.summary,
                    'look_num': obj.look_num,
                    'like_num': obj.like_num,
                    'classify_id_list': classify_id_list,
                    'classify_name_list': classify_name_list,
                    'create_user_id': obj.create_user_id,
                    'cover_img': obj.cover_img,
                    'is_like': is_like,                         # 是否点赞
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                }
                if id: # 如果查询详情 返回文章内容  查询全部不返回 否则数据过大
                    result_data['content'] = json.loads(obj.content)
                    result_data['style'] = obj.style
                    result_data['top_advertising'] = obj.top_advertising
                    result_data['end_advertising'] = obj.end_advertising
                    # 个人信息
                    result_data['name'] = b64decode(user_obj.name)          # 用户名称
                    result_data['phone_number'] = user_obj.phone_number     # 用户电话
                    result_data['signature'] = user_obj.signature           # 用户签名
                    result_data['set_avator'] = user_obj.set_avator         # 用户头像
                    brand_name_list = []
                    for i in user_obj.brand_classify.all():
                        brand_name_list.append(i.name)
                    result_data['brand_name'] = brand_name_list             # 用户品牌
                    result_data['qr_code'] = user_obj.qr_code               # 用户微信二维码


                     # 用户查看文章 客户字段为空
                    models.SelectArticleLog.objects.create(
                        article_id=id,
                        inviter_id=user_id
                    )
                    # 记录查看次数
                    obj.look_num = F('look_num') + 1
                    obj.save()


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
                'classify_id_list': "所属分类id",
                'classify_name_list': "所属分类名称",
                'create_datetime': "创建时间",
                'cover_img': "封面图",
                'create_user_id': "创建人ID",
                'create_user__name': "创建人姓名",
                'create_user__set_avator': "创建人头像",
                'name': "用户名称",
                'phone_number': "用户电话",
                'signature': "用户个性签名",
                'set_avator': "用户头像",
                'brand_name': "用户品牌名称",
                'qr_code': "用户微信二维码",
            }
        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)



# token验证 用户操作文章
@account.is_token(models.Userprofile)
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加文章
        if oper_type == "add":
            article_url = request.POST.get('article_url')
            classify_id = request.POST.get('classify_id')
            form_data = {
                'create_user_id': user_id,
                'article_url': article_url,
                'classify_id': classify_id
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                data_dict = get_article(article_url)
                cleaned_data = forms_obj.cleaned_data

                cover_url = data_dict.get('cover_url') # 封面
                title = data_dict.get('title')
                summary = data_dict.get('summary')
                style = data_dict.get('style')
                data_list = json.dumps(data_dict.get('content'))
                obj = models.Article.objects.create(
                    title=title,
                    content=data_list,
                    summary=summary,
                    cover_img=cover_url,
                    style=style,
                    create_user_id=cleaned_data.get('create_user_id'),
                )

                obj.classify = cleaned_data.get('classify_id')
                obj.save()
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改文章 修改文章前 调用decide_if_your_article判断flag 是否为自己的文章 不是创建返回ID 直接跳转
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,   # 文章id
                'create_user_id': user_id,
                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
                # 'summary': request.POST.get('summary'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                title = forms_obj.cleaned_data['title']
                content = forms_obj.cleaned_data['content']
                # summary = forms_obj.cleaned_data['summary']
                objs = models.Article.objects.filter(id=o_id)
                #  如果为创建人修改 则修改文章
                objs.update(
                    title=title,
                    # summary=summary,
                    content=content,
                )
                response.msg = "修改成功"
                response.code = 200

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 插入我的内容  插入内容 判断是否为自己的文章 不是则创建直接跳转
        elif oper_type == 'insert_content':
            top_advertising = request.POST.get('top_advertising')  # 顶部内容
            end_advertising = request.POST.get('end_advertising')  # 底部内容
            objs = models.Article.objects.filter(id=o_id)
            obj = objs[0]
            if int(objs[0].create_user_id) == int(user_id):
                if top_advertising:
                    objs.update(
                        top_advertising = top_advertising,
                    )
                else:
                    objs.update(
                        end_advertising = end_advertising
                    )
                response.msg = '更新成功'
            else:
                obj = models.Article.objects.create(
                    title=obj.title,
                    content=obj.content,
                    cover_img=obj.cover_img,
                    summary=obj.summary,
                    style=obj.style,
                    create_user_id=user_id,
                    top_advertising=top_advertising,
                    end_advertising=end_advertising,
                )
                response.msg = '创建成功'
                response.data = {
                    'id':obj.id
                }
            response.code = 200

        # 修改文章所属分类
        elif oper_type == "update_classify":
            form_data = {
                'o_id': o_id,  # 文章id
                'create_user_id': user_id,
                'classify_id': request.POST.get('classify_id'),
            }

            forms_obj = UpdateClassifyForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                classify_id = forms_obj.cleaned_data['classify_id']

                #  查询更新 数据
                models.Article.objects.filter(id=o_id).update(
                    classify=classify_id
                )
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 创建文章 (不是自己的文章)
        elif oper_type == 'add_article':
            top_advertising = request.POST.get('top_advertising')
            end_advertising = request.POST.get('end_advertising')
            classify_id = json.loads(request.POST.get('classify_id'))

            objs = models.Article.objects.filter(id=o_id)
            if objs:
                obj = objs[0]

                obj = models.Article.objects.create(
                    title=obj.title,
                    content=obj.content,
                    cover_img=obj.cover_img,
                    summary=obj.summary,
                    create_user_id=user_id,
                    top_advertising=top_advertising,
                    end_advertising=end_advertising,
                )
                obj.classify = classify_id

                response.msg = '创建成功'
                response.data = {
                    'id': obj.id
                }
                response.code = 200
            else:
                response.code = 301
                response.msg = '该文章被删除'

        # 用户点赞/取消点赞
        elif oper_type == 'user_give_like':
            response = Response.ResponseObj()
            form_data = {
                'article_id': o_id,
                'user_id': request.GET.get('user_id')
            }
            form_obj = GiveALike(form_data)
            if form_obj.is_valid():
                user_id = form_obj.cleaned_data.get('user_id')
                article_id = form_obj.cleaned_data.get('article_id')
                response = give_like(user_id=user_id, article_id=article_id)  # 点赞
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())


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
                        'summary': obj.summary,
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

        # 查询是否为自己的文章  判断flag
        elif oper_type == 'decide_if_your_article':
            form_data = {
                'o_id': o_id,
                'user_id': user_id
            }
            form_obj = DecideIfYourArticle(form_data)
            if form_obj.is_valid():
                o_id = form_obj.cleaned_data.get('o_id')
                response.code = 200
                response.msg = '查询成功'
                response.data = {'flag': o_id}
                response.note = {
                    'flag': '为True则是自己创建, 为False需要选择标签classify_id'
                }
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

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











# 客户 操作
@account.is_token(models.Customer)
def article_customer_oper(request, oper_type):
    response = Response.ResponseObj()
    inviter_user_id = request.GET.get('inviter_user_id') # 用户ID
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        # 客户查询文章详情
        if oper_type == 'article':
            id = request.GET.get('id')                          # 文章ID
            obj = models.Article.objects.get(id=id)
            user_obj = models.Userprofile.objects.get(id=inviter_user_id)

            is_like = False  # 是否点赞
            log_obj = models.SelectClickArticleLog.objects.filter(
                article_id=obj.id,
                customer_id=user_id
            )
            if log_obj:
                is_like = True

            result_data = {
                'id': obj.id,
                'title': obj.title,
                'summary': obj.summary,
                'look_num': obj.look_num,
                'like_num': obj.like_num,
                'create_user_id': obj.create_user_id,
                'cover_img': obj.cover_img,
                'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            }
            result_data['content'] = json.loads(obj.content)
            result_data['style'] = obj.style
            result_data['top_advertising'] = obj.top_advertising
            result_data['end_advertising'] = obj.end_advertising
            # 个人信息
            result_data['name'] = b64decode(user_obj.name)  # 用户名称
            result_data['phone_number'] = user_obj.phone_number  # 用户电话
            result_data['signature'] = user_obj.signature  # 用户签名
            result_data['set_avator'] = user_obj.set_avator  # 用户头像
            brand_name_list = []
            for i in user_obj.brand_classify.all():
                brand_name_list.append(i.name)
            result_data['brand_name'] = brand_name_list  # 用户品牌
            result_data['qr_code'] = user_obj.qr_code   # 用户微信二维码
            result_data['is_like'] = is_like            # 是否点赞

            article_objs = models.Article.objects.filter(
                title__isnull=False
            ).exclude(
                id=id
            ).order_by('look_num')[:3]
            print('article_objs---> ', article_objs)
            popula_articles_list = []
            for article_obj in article_objs:
                pub = 'article_' + str(article_obj.id)
                url = forwarding_article(
                    pub=pub,
                    user_id=article_obj.create_user_id,
                )
                popula_articles_list.append({
                    'title': article_obj.title,
                    'cover_img':article_obj.cover_img,
                    'url':url
                })
            # 如果是客户查看记录查看次数 创建查看信息
            models.SelectArticleLog.objects.create(
                customer_id=user_id,
                article_id=id,
                inviter_id=inviter_user_id
            )
            # 记录查看次数
            obj.look_num = F('look_num') + 1
            obj.save()
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'popula_articles': popula_articles_list,
                'result_data': result_data
            }

        # 客户查询微店分类
        elif oper_type == 'goods_classify':
            objs = models.GoodsClassify.objects.filter(
                oper_user_id=inviter_user_id
            ).order_by('-create_datetime')
            data_list = []
            for obj in objs:
                is_good = False
                if obj.goods_set.all():
                    is_good = True
                data_list.append({
                    'id': obj.id,
                    'goods_classify': obj.goods_classify,
                    'oper_user_id': obj.oper_user_id,
                    'oper_user': b64decode(obj.oper_user.name),
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_good': is_good,
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': data_list,
                'count': objs.count(),
            }
            response.note = {
                'id': '分类ID',
                'goods_classify': '分类名称',
                'oper_user_id': '分类归属人ID',
                'oper_user': '分类归属人姓名',
                'create_datetime': '创建时间',
                'is_good': '该分类下是否有商品',
            }

            # 客户查询商品

        # 查询微店
        elif oper_type == 'small_shop':
            forms_obj = select_form(request.GET)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                field_dict = {
                    'id': '',
                    'goods_classify_id': '',
                    'goods_name': '__contains',
                }
                q = conditionCom(request, field_dict)

                objs = models.Goods.objects.filter(
                    q,
                    goods_classify__oper_user_id=inviter_user_id
                )
                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                ret_data = []
                for obj in objs:
                    try:
                        goods_describe = eval(obj.goods_describe)
                    except Exception:
                        goods_describe = obj.goods_describe

                        #  将查询出来的数据 加入列表
                    ret_data.append({
                        'id': obj.id,
                        'goods_classify_id': obj.goods_classify_id,  # 分类ID
                        'goods_classify': obj.goods_classify.goods_classify,  # 分类名称
                        'goods_name': obj.goods_name,  # 商品名称
                        'price': obj.price,  # 商品价格
                        'inventory': obj.inventory,  # 商品库存
                        'freight': obj.freight,  # 商品运费
                        'goods_describe': goods_describe,  # 商品描述
                        'point_origin': obj.point_origin,  # 商品发货地
                        'goods_status_id': obj.goods_status,  # 商品状态ID
                        'goods_status': obj.get_goods_status_display(),  # 商品状态
                        'cover_img': obj.cover_img,  # 商品封面图片
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count
                }
                response.note = {
                    'id': "文章id",
                    'goods_classify': '商品分类',
                    'goods_name': '分类名称',
                    'price': '商品价格',
                    'inventory': '商品库存',
                    'freight': '商品运费',
                    'goods_describe': '商品描述',
                    'point_origin': '商品发货地',
                    'goods_status': '商品状态',
                    'create_datetime': '商品创建时间',
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        # 客户点赞
        if oper_type == 'give_like':
            form_data = {
                'article_id': request.POST.get('article_id'),
                'customer_id': request.GET.get('user_id')
            }

            form_obj = GiveALike(form_data)
            if form_obj.is_valid():
                customer_id = form_obj.cleaned_data.get('customer_id')
                article_id = form_obj.cleaned_data.get('article_id')
                response = give_like(customer_id=customer_id, article_id=article_id)  # 点赞
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 客户打开 用户分享的文章 (嵌入微信url 获取用户信息 匹配openid 判断数据库是否存在 跳转文章页)
# def share_article(request, o_id):
#     code = request.GET.get('code')
#     code_objs = models.save_code.objects.filter(code=code)
#     if not code_objs:
#         models.save_code.objects.create(save_code=code)
#
#         _type = o_id.split('_')[0]  # 类型
#         oid = o_id.split('_')[1]    # ID
#
#         inviter_user_id = request.GET.get('state')  # 分享文章的用户id
#         weichat_api_obj = weixin_gongzhonghao_api.WeChatApi()
#         ret_obj = weichat_api_obj.get_openid(code)
#         openid = ret_obj.get('openid')
#
#         user_data = {
#             "sex": ret_obj.get('sex'),
#             "country": ret_obj.get('country'),
#             "province": ret_obj.get('province'),
#             "city": ret_obj.get('city'),
#         }
#         customer_objs = models.Customer.objects.filter(openid=openid)
#         if customer_objs:   # 客户已经存在
#             customer_objs.update(**user_data)
#             customer_obj = customer_objs[0]
#         # 不存在，创建用户
#         else:
#             encode_username = b64encode(
#                 ret_obj['nickname']
#             )
#
#             subscribe = ret_obj.get('subscribe')
#
#             # 如果没有关注，获取个人信息判断是否关注
#             if not subscribe:
#                 weichat_api_obj = WeChatApi()
#                 ret_obj = weichat_api_obj.get_user_info(openid=openid)
#                 subscribe = ret_obj.get('subscribe')
#
#             user_data['set_avator'] = ret_obj.get('headimgurl')
#             user_data['subscribe'] = subscribe
#             user_data['name'] = encode_username
#             user_data['openid'] = ret_obj.get('openid')
#             user_data['token'] = get_token()
#             print("user_data --->", user_data)
#             customer_obj = models.Customer.objects.create(**user_data)
#         objs = models.Customer.objects.filter(openid=openid)
#         obj = objs[0]
#
#         # 此处跳转到文章页面
#         redirect_url = '{host_url}#/share_article?user_id={user_id}&token={token}&id={article_id}&inviter_user_id={inviter_user_id}'.format(
#             host_url=host_url,
#             article_id=o_id,  # 分享文章的id
#             user_id=customer_obj.id,
#             token=obj.token,
#             inviter_user_id=inviter_user_id,
#         )
#         return redirect(redirect_url)
#
# # 点击分享出去的文章 跳转到这
# def redirect_url(request):
#     print('request.GET--------------> ', request.GET)
#     redirect_url = request.GET.get('share_url')
#     # redirect_url = unquote(share_url, 'utf-8')
#     print('=-------跳转链接--> ', redirect_url)
#     return redirect(redirect_url)


