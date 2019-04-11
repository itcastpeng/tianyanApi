from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode, b64encode
import requests, datetime, random, json
from django.db.models import Q
from publicFunc.get_content_article import get_article
from publicFunc.article_oper import add_article_public

# token验证 用户操作文章
def article_oper(request, oper_type):
    response = Response.ResponseObj()

    # 获取分类
    if oper_type == 'get_classify':
        now = datetime.datetime.today()
        q = Q()
        q.add(Q(last_update_time__isnull=True) | Q(last_update_time__lt=now), Q.AND)
        objs = models.Classify.objects.filter(
            q,
            create_user__isnull=True
        )
        ret_data = {}
        if objs:
            obj = objs[0]
            ret_data['id'] = obj.id
            ret_data['name'] = obj.name

            obj.last_update_time=now
            obj.save()

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
        content = json.dumps(data.get('content'))  # 标题
        objs = models.Article.objects.filter(title=title)
        if not objs:
            if len(content) > 0 and title and len(content) >= 2:
                add_article_public(data, classify_id)

    return JsonResponse(response.__dict__)




