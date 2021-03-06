from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.article import AddForm, UpdateForm, SelectForm, UpdateClassifyForm, GiveALike,\
PopulaSelectForm, DecideIfYourArticle, select_form, add_article, RecordLengthForm
from django.db.models import Q, F
from publicFunc.base64_encryption import b64decode, b64encode
from publicFunc.article_oper import give_like
from publicFunc.get_content_article import get_article
from publicFunc.article_oper import add_article_public
from tianyan_celery.tasks import customer_view_articles_send_msg
from publicFunc.public import randomly_query_three_articles, get_hot_commodity
import requests, datetime, random, json, redis, re

# token验证 文章展示模块
@account.is_token(models.Userprofile)
def article(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    team_list = request.GET.get('team_list')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            redis_key = 'tianyan_article_fixed_{}'.format(user_id)
            rc = redis.StrictRedis(host='redis_host', port=6379, db=7, decode_responses=True)

            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            field_dict = {
                'id': '',
                'title': '__contains',
                'classify': '',
                'create_user_id': '__in',
                'create_datetime': '',
                'source_link': '',
            }
            q = conditionCom(request, field_dict)
            user_obj = models.Userprofile.objects.get(id=user_id)

            """
            用户查看文章页面时 点击别的操作 会刷新页面  需求： 点击别的操作不刷新页面 数据还是原来的 只有点击刷新 才变页面数据
            解决方法：{
                每个人一个ID 如：article_fixed_{user_id}，
                每次查询 未传 fixed_content 参数情况下 推荐查询 记录本次数据 返回查询码，
                传递 fixed_content 参数 查询上次数据，
                传递 fixed_content 参数 且 传递add_fixed_content参数 单做查询 插入原有固定数据 证明翻页 
                redis-hash数据  name:tianyan_article_fixed_content  key:tianyan_article_fixed_{user_id}
            }            
            """

            fixed_content = request.GET.get('fixed_content')  # 固定内容键  查询上次查询过的数据
            add_fixed_content = request.GET.get('add_fixed_content')  # 下拉固定内容 添加固定内容

            if fixed_content and not add_fixed_content: # 查询上次内容  且未下拉
                data = rc.hget('tianyan_article_fixed_content', redis_key)
                ret_data = eval(data)
                count = len(ret_data)
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    ret_data = ret_data[start_line: stop_line]

            else:
                classify_type = forms_obj.cleaned_data.get('classify_type')  # 分类类型，1 => 推荐, 2 => 品牌
                classify_id_list = []
                if classify_type:
                    classify_objs = None
                    if classify_type == 1:  # 推荐分类
                        classify_objs = user_obj.recommend_classify.all()
                        classify_id_list = [obj.id for obj in classify_objs]
                        if len(classify_id_list) > 0:
                            q.add(Q(**{'classify__in': classify_id_list}), Q.AND)

                    elif classify_type == 2:  # 品牌分类
                        classify_objs = user_obj.brand_classify.all()
                        classify_id_list = [obj.id for obj in classify_objs]
                        q.add(Q(**{'classify__in': classify_id_list}), Q.AND)

                # 团队
                if team_list and len(team_list) >= 1:
                    article_list = []
                    team_objs = models.UserprofileTeam.objects.filter(user_id=user_id)  # 查询出该用户所有团队
                    team_id_list = []
                    for i in team_objs:
                        team_id_list.append(i.team_id)

                    # 查询出该团队所有用户 去重
                    team_objs = models.UserprofileTeam.objects.filter(team_id__in=team_id_list).values(
                        'user_id').distinct()
                    team_user_list = []
                    for team_obj in team_objs:
                        team_user_list.append(team_obj['user_id'])

                    # 查询 该团队所有用户文章
                    team_user_objs = models.Article.objects.filter(
                        create_user_id__in=team_user_list,
                        ownership_team_id__in=team_id_list
                    )  # 查询该团队 所有文章
                    for i in team_user_objs:
                        article_list.append(i.id)

                    q.add(Q(**{'id__in': article_list}), Q.AND)


                is_use_redis = False # 是否进行redis操作

                if classify_type and classify_type == 2:  # 我的品牌
                    order_by = '-create_datetime'

                elif classify_type and classify_type == 1 and len(classify_id_list) <= 0:  # 推荐为空
                    q.add(Q(classify__create_user__isnull=True) & Q(classify__isnull=False),
                        Q.AND)  # 没有选择推荐的用户默认 推荐系统标签的
                    order_by = '?'
                    is_use_redis = True

                elif team_list:  # 团队
                    # q.add(Q(create_user_id=user_id), Q.OR)
                    order_by = '-like_num'

                else:
                    is_use_redis = True
                    order_by = '?'


                objs = models.Article.objects.filter(
                    q,
                ).order_by(order_by)

                print('q -->', q, order_by)

                count = objs.count()

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []

                id = request.GET.get('id')

                # 返回的数据
                for obj in objs:
                    is_like = False  # 是否点赞
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

                    summary = obj.summary
                    if obj.summary:
                        summary = b64decode(obj.summary)

                    result_data = {
                        'id': obj.id,
                        'title': obj.title,
                        'summary': summary,
                        'look_num': obj.look_num,
                        'like_num': obj.like_num,
                        'classify_id_list': classify_id_list,
                        'classify_name_list': classify_name_list,
                        'create_user_id': obj.create_user_id,
                        'cover_img': obj.cover_img,
                        'is_like': is_like,  # 是否点赞
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    if id:  # 如果查询详情 返回文章内容  查询全部不返回 否则数据过大
                        result_data['top_advertising'] = user_obj.top_advertising  # 头部广告
                        result_data['end_advertising'] = user_obj.end_advertising  # 底部广告
                        is_oneself_article = False
                        if user_id == obj.create_user_id:
                            is_oneself_article = True

                        result_data['is_oneself_article'] = is_oneself_article
                        result_data['content'] = json.loads(obj.content)
                        result_data['style'] = obj.style
                        # 个人信息
                        result_data['name'] = b64decode(user_obj.name)  # 用户名称
                        result_data['phone_number'] = user_obj.phone_number  # 用户电话
                        result_data['signature'] = user_obj.signature  # 用户签名
                        result_data['set_avator'] = user_obj.set_avator  # 用户头像
                        brand_name_list = []
                        for i in user_obj.brand_classify.all():
                            brand_name_list.append(i.name)
                        result_data['brand_name'] = brand_name_list  # 用户品牌
                        result_data['qr_code'] = user_obj.qr_code  # 用户微信二维码

                        # 用户查看文章 客户字段为空 判断今天是否看过此文章 看过不记录
                        now = datetime.datetime.today().strftime('%Y-%m-%d') + ' 00:00:00'
                        log_objs = models.SelectArticleLog.objects.filter(
                            article_id=id,
                            inviter_id=user_id,
                            create_datetime__gte=now
                        )
                        if not log_objs:
                            models.SelectArticleLog.objects.create(
                                article_id=id,
                                inviter_id=user_id
                            )
                            # 记录查看次数
                            obj.look_num = F('look_num') + 1
                            obj.save()
                        # 热卖商品 我的里面设置是否展示
                        goods_list = []
                        if user_obj.show_product:
                            good_objs = models.Goods.objects.filter(goods_classify__oper_user_id=user_id)

                            good_count = good_objs.count()
                            if good_count >= 2:
                                good_objs = good_objs[0:2]
                            elif good_count <= 0:
                                good_objs = good_objs
                            else:
                                good_objs = good_objs[0:1]

                            for good_obj in good_objs:
                                goods_list.append({
                                    'id': good_obj.id,
                                    # 'goods_describe': good_obj.goods_describe,  # 商品描述
                                    'price': good_obj.price,  # 商品价格
                                    'goods_name': good_obj.goods_name,  # 商品名称
                                    'cover_img': good_obj.cover_img,  # 封面图
                                })
                        result_data['goods_list'] = goods_list


                    if team_list and len(team_list) >= 1:  # 如果查询 团队 则返回 文章创建人头像和名称
                        result_data['create_user__name'] = obj.create_user.name
                        result_data['create_user__set_avator'] = obj.create_user.set_avator
                        team_list_name = []
                        # if obj.ownership_team:
                        team_list_name.append(obj.ownership_team.name)
                        # else:
                        #     team_list_name.append('创建')

                        result_data['team_list_name'] = team_list_name

                    #  将查询出来的数据 加入列表
                    ret_data.append(result_data)

                if is_use_redis: # 进行redis缓存
                    if not add_fixed_content: # 加入redis
                        rc.hset('tianyan_article_fixed_content', redis_key, str(ret_data))

                    else:
                        data = rc.hget('tianyan_article_fixed_content', redis_key) # 查询出所有缓存数据
                        rc_data = eval(data)
                        for i in ret_data:              # 判断缓存是否有该数据  没有插入
                            if i not in rc_data:
                                rc_data.append(i)
                        rc.hset('tianyan_article_fixed_content', redis_key, str(rc_data)) # 最终数据缓存进 redis
                        ret_data = eval(rc.hget('tianyan_article_fixed_content', redis_key)) # 查询数据

                        if length != 0:
                            start_line = (current_page - 1) * length
                            stop_line = start_line + length
                            ret_data = ret_data[start_line: stop_line]

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'rc': redis_key,    # redis_key
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
                'is_oneself_article': "是否是自己的文章",
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
            ownership_team = request.POST.get('ownership_team') # 归属团队
            classify_id = request.POST.get('classify_id')
            form_data = {
                'create_user_id': user_id,
                'article_url': article_url,
                'ownership_team': ownership_team,
                'classify_id': classify_id,
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():

                data_dict = get_article(article_url)

                print("data_dict.get('title')----------------> ", data_dict.get('title'))

                cleaned_data = forms_obj.cleaned_data
                ownership_team_id = cleaned_data.get('ownership_team')
                is_article = models.Article.objects.filter(
                    create_user_id=user_id,
                    title=data_dict.get('title'),
                    ownership_team_id=ownership_team_id
                )
                data_dict['create_user_id'] = user_id
                data_dict['ownership_team_id'] = ownership_team_id
                if not is_article:
                    classify_id = cleaned_data.get('classify_id')
                    id = add_article_public(data_dict, classify_id) # 创建文章
                else:
                    id = is_article[0].id

                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': id}
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
            user_objs = models.Userprofile.objects.filter(id=user_id)
            delete_advertising = request.POST.get('delete_advertising')  # 删除内容
            if delete_advertising:
                if delete_advertising == 'top':
                    user_objs.update(top_advertising=None)
                if delete_advertising == 'end':
                    user_objs.update(end_advertising=None)
                response.code = 200
                response.msg = '删除成功'

            else:
                top_advertising = request.POST.get('top_advertising')  # 顶部内容
                end_advertising = request.POST.get('end_advertising')  # 底部内容


                if top_advertising:
                    user_objs.update(
                        top_advertising=top_advertising,
                    )
                else:
                    user_objs.update(
                        end_advertising=end_advertising
                    )

                objs = models.Article.objects.filter(id=o_id)
                obj = objs[0]
                data = {
                    'title': obj.title,
                    'content': obj.content,
                    'cover_img': obj.cover_img,
                    'summary': obj.summary,
                    'style': obj.style,
                    'create_user_id': user_id,
                }
                print('user_id-> ', user_id)
                id = add_article_public(data)     # 添加文章

                response.msg = '修改成功'
                response.data = {
                    'id':id
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

        # 创建文章 (不是自己的文章)修改他人文章时调用
        elif oper_type == 'add_article':
            top_advertising = request.POST.get('top_advertising')
            end_advertising = request.POST.get('end_advertising')
            ownership_team = request.POST.get('ownership_team')  # 归属团队

            models.Userprofile.objects.filter(id=user_id).update(
                top_advertising=top_advertising,
                end_advertising=end_advertising
            )

            objs = models.Article.objects.filter(id=o_id)
            if objs:
                obj = objs[0]
                data = {
                    'title': obj.title,
                    'content': obj.content,
                    'cover_img': obj.cover_img,
                    'summary': obj.summary,
                    'style': obj.style,
                    'create_user_id': user_id,
                    'ownership_team_id': ownership_team,
                }
                id = add_article_public(data) # 创建文章

                response.msg = '创建成功'

                response.data = {
                    'id': id
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

        # 删除文章 （临时调用 接口）
        elif oper_type == 'delete_article':
            id = o_id
            click_article_objs = models.SelectClickArticleLog.objects.filter(article_id=id) # 客户点赞
            select_article_objs = models.SelectArticleLog.objects.filter(article_id=id) # 查询文章
            article_objs = models.Article.objects.filter(id=id)
            click_article_objs.delete()
            select_article_objs.delete()
            article_objs.delete()
            response.code = 200
            response.msg = '删除成功'

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




# 客户 操作 文章
@account.is_token(models.Customer)
def article_customer_oper(request, oper_type):
    response = Response.ResponseObj()
    inviter_user_id = request.GET.get('inviter_user_id') # 用户ID
    customer_id = request.GET.get('user_id')    # 客户ID
    if request.method == 'GET':

        # 客户查询文章详情
        if oper_type == 'article':
            id = request.GET.get('id')                          # 文章ID
            objs = models.Article.objects.filter(id=id)
            if objs:
                obj = objs[0]
                user_obj = models.Userprofile.objects.get(id=inviter_user_id)

                is_like = False  # 是否点赞
                log_obj = models.SelectClickArticleLog.objects.filter(
                    article_id=obj.id,
                    customer_id=customer_id
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
                result_data['top_advertising'] = user_obj.top_advertising
                result_data['end_advertising'] = user_obj.end_advertising
                # 个人信息
                result_data['name'] = b64decode(user_obj.name)  # 用户名称
                result_data['phone_number'] = user_obj.phone_number  # 用户电话
                result_data['signature'] = user_obj.signature  # 用户签名
                result_data['set_avator'] = user_obj.set_avator + '?imageView2/2/w/100' # 用户头像
                brand_name_list = []
                for i in user_obj.brand_classify.all():
                    brand_name_list.append(i.name)
                result_data['brand_name'] = brand_name_list  # 用户品牌
                qr_code = ''
                if user_obj.qr_code:
                    qr_code = user_obj.qr_code + '?imageView2/2/w/100'
                result_data['qr_code'] = qr_code   # 用户微信二维码
                result_data['is_like'] = is_like            # 是否点赞

                # 随机获取三篇文章
                popula_articles_list = randomly_query_three_articles(inviter_user_id, id)

                # 查询最热商品=======================
                goods_list = []
                if user_obj.show_product: # 如果客户 打开文章底部显示热卖
                    goods_list = get_hot_commodity(inviter_user_id)

                article_log_obj = models.SelectArticleLog.objects.create(
                    customer_id=customer_id,
                    article_id=id,
                    inviter_id=inviter_user_id
                )
                # 记录查看次数
                obj.look_num = F('look_num') + 1
                obj.save()

                # 给用户发送消息
                customer_view_articles_send_msg.delay({
                    'check_type': '文章',
                    'user_id': inviter_user_id,
                    'title': obj.title,
                    'customer_id': customer_id,
                })

                is_own_article = False
                # 判断是否是自己的文章
                customer_openid = article_log_obj.customer.openid
                user_objs = models.Userprofile.objects.filter(openid=customer_openid)
                if user_objs:
                    if int(user_objs[0].id) == int(inviter_user_id):
                        is_own_article = True

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'goods_list': goods_list,
                    'popula_articles': popula_articles_list,
                    'result_data': result_data,
                    'is_own_article': is_own_article,
                }
                response.note = {
                    'popula_articles热门文章': {
                        'title': '标题',
                        'cover_img': '封面',
                        'url': '链接'
                    },
                    'result_data_文章内容': {
                        'id': '文章ID',
                        'title': '文章标题',
                        'summary': '文章摘要',
                        'look_num': '文章查看人数',
                        'like_num': '文章点赞人数',
                        'create_user_id': '文章创建人ID',
                        'cover_img': '文章封面',
                        'create_datetime': '文章创建时间',
                        'content': '文章内容',
                        'style': '文章样式',
                        'top_advertising': '顶部内容',
                        'end_advertising': '底部内容',
                        'name': '用户名称',
                        'phone_number': '用户电话',
                        'signature': '用户签名',
                        'set_avator': '用户头像',
                        'brand_name': '用户品牌',
                        'qr_code': '用户微信二维码',
                        'is_like': '是否点赞',
                    },
                    'goods_list_热门商品':{
                        # 'goods_describe': '商品描述',
                        'price': '商品价格',
                        'goods_name': '商品名称',
                        'cover_img': '封面图',
                        'url': '跳转链接'
                    },
                    'is_own_article': '是否为自己的文章',
                }

            else:
                response.code = 400
                response.msg = '页面丢失'

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


                # 查询详情记录
                id = request.GET.get('id')
                if id:
                    goods_obj = models.Goods.objects.get(id=id)
                    models.customer_look_goods_log.objects.create(
                        goods_id=id,
                        customer_id=customer_id,
                        user_id=inviter_user_id
                    )

                    # 给用户发送消息
                    customer_view_articles_send_msg.delay({
                        'check_type': '商品',
                        'user_id': inviter_user_id,
                        'title': goods_obj.goods_name,
                        'customer_id': customer_id,
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

        # 客户记录 文章查看时长/商城查看时长
        elif oper_type == 'record_length':
            status = request.GET.get('status')
            public_id = request.GET.get('public_id')
            # close_date = request.GET.get('close_date')
            """
            inviter_user_id  为分享人ID
            status == 1 为记录文章日志 
            status == 2 为记录微店日志
            user_id 为客户ID
            close_date 最后一次时间 每几秒请求一次 以最后一次请求为关闭时间
            """
            form_data = {
                'status': status,
                'public_id': public_id,
                'user_id': customer_id,
                'inviter_user_id': inviter_user_id,
                'close_date': datetime.datetime.now(),
            }
            form_objs = RecordLengthForm(form_data)
            if form_objs.is_valid():
                response.code = 200
                response.msg = '日志记录成功'

            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 客户查询 用户名片
        elif oper_type == 'business_card':
            obj = models.Userprofile.objects.get(id=inviter_user_id)
            name = b64decode(obj.name)
            if not obj.introduction:
                introduction = '我是{}, 欢迎来到我的名片'.format(name)
            else:
                introduction = obj.introduction

            article_list = randomly_query_three_articles(inviter_user_id)
            goods_list = get_hot_commodity(inviter_user_id)

            data_list = {
                'user_id': obj.id,
                'introduction': introduction,
                'user_name': name,
                'set_avator': obj.set_avator + '?imageView2/2/w/100',
                'article_list': article_list,
                'goods_list': goods_list,
            }
            response.code = 200
            response.msg = '查询成功'
            response.data = data_list

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

        # 客户 点击 更换成我的名片
        elif oper_type == 'change_my_business_card':
            obj = models.Customer.objects.get(id=customer_id)
            article_id = request.POST.get('article_id')
            article_objs = models.Article.objects.filter(id=article_id)
            if article_objs:
                article_obj = article_objs[0]

                if obj.subscribe:  # 已关注公众号

                    user_obj = models.Userprofile.objects.get(openid=obj.openid)

                    if_article_objs = models.Article.objects.filter(
                        create_user_id=user_obj.id,
                        title=article_obj.title
                    )

                    if not if_article_objs: # 没有创建
                        create_article_obj = models.Article.objects.create(
                            title=article_obj.title,
                            summary=article_obj.summary,
                            content=article_obj.content,
                            create_user_id=user_obj.id,
                            source_link=article_obj.source_link,
                            cover_img=article_obj.cover_img,
                            style=article_obj.style,
                            original_link=article_obj.original_link,
                        )
                        create_article_obj.classify = [39]
                        create_article_obj.save()

                        article_id = create_article_obj.id
                    else:
                        if_article_obj = if_article_objs[0]
                        article_id = if_article_obj.id

                    msg = '跳转页面'
                    code = 200
                    response.data = {
                        'article_id': article_id,
                        'user_id': user_obj.id,
                        'token': user_obj.token,
                    }

                else:  # 未关注公众号
                    select_article_objs = models.SelectArticleLog.objects.filter(
                        customer_id=customer_id,
                        article_id=article_id
                    ).order_by('-create_datetime')
                    if select_article_objs:
                        select_article_obj = select_article_objs[0]
                        select_article_obj.click_modify = 1
                        select_article_obj.save()
                        weChat_qr_code = select_article_obj.inviter.enterprise.weChat_qr_code
                    else:
                        weChat_qr_code = article_obj.create_user.enterprise.weChat_qr_code
                    msg = '未关注公众号'
                    code = 301
                    response.data = {
                        'weChat_qr_code': weChat_qr_code
                    }

            else:
                code = 301
                msg = '该文章已被删除'

            response.code = code
            response.msg = msg

        # 获取自己 用户 的 token （以客户身份进入自己分享的文章 可直接修改 点击修改 获取自己用户token 登录天眼）
        elif oper_type == 'get_my_token':
            obj = models.Customer.objects.get(id=customer_id)
            user_objs = models.Userprofile.objects.filter(openid=obj.openid)
            if user_objs:
                user_obj = user_objs[0]
                data = {
                    'id': user_obj.id,
                    'token': user_obj.token,
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': data
                }

            else:
                response.code = 301
                response.msg = '修改失败'

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


