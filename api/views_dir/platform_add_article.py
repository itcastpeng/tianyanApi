from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode, b64encode
import requests, datetime, random, json
from django.db.models import Q
from publicFunc.get_content_article import get_article


# token验证 用户操作文章
def article_oper(request, oper_type):
    response = Response.ResponseObj()

    # 获取分类
    if oper_type == 'get_classify':
        now = datetime.datetime.today()
        q = Q()
        q.add(Q(last_update_time__isnull=True) | Q(last_update_time__lt=now), Q.AND)
        objs = models.Classify.objects.filter(
            create_user__isnull=True
        )
        ret_data = {}
        if objs:
            objs.update(last_update_time=now)
            obj = objs[0]
            ret_data['id'] = obj.id
            ret_data['name'] = obj.name
        response.code = 200
        response.data = ret_data

    # 判断库里是否有该文章
    elif oper_type == 'is_there_article':
        title = request.GET.get('title')
        q = Q()
        q.add(Q(title=title) & Q(create_user__isnull=True), Q.AND)
        objs = models.Article.objects.filter(q)
        print('objs-----> ', objs, title)
        flag = True
        if objs:
            flag = False
        response.data = flag

    # 获取链接 加入文章
    elif oper_type == 'get_url_add_article':
        url = request.GET.get('url')
        classify_id = request.GET.get('classify_id')

        data = get_article(url)
        title = data.get('title')  # 标题
        summary = data.get('summary') # 摘要
        cover_url = data.get('cover_url') # 封面
        style = data.get('style') # style
        content = json.dumps(data.get('content')) # 内容

        objs = models.Article.objects.filter(title=title)
        if not objs:
            obj = models.Article.objects.create(
                title=title,
                content=content,
                summary=summary,
                cover_img=cover_url,
                style=style,
            )
            obj.classify = classify_id
            obj.save()

    return JsonResponse(response.__dict__)




