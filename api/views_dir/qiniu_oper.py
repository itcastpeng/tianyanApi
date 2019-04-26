
from publicFunc import Response
import qiniu
from django.http import JsonResponse
from api import models
import json, requests, os

# 前端请求
def qiniu_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'get_token':

        SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
        AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
        q = qiniu.Auth(AccessKey, SecretKey)
        bucket_name = 'bjhzkq_tianyan'
        token = q.upload_token(bucket_name)  # 可以指定key 图片名称

        response.code = 200
        response.msg = '生成成功'
        response.data = {'token': token}


    elif oper_type == 'test_article':
        print('-=-----------------------000000000000000000-----------------------------------=-')
        objs = models.Article.objects.filter(
            classify__create_user__isnull=True,

        )
        for obj in objs:
            content = json.loads(obj.content)
            if len(content) <= 5:
                print('obj.style------。 ', obj.style)
                if os.path.exists(obj.style):
                    os.remove(obj.style)
                if os.path.exists(obj.cover_img):
                    os.remove(obj.cover_img)
                url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/article/delete_article/{}?timestamp=1545822031837&rand_str=b965c1e6875a3d4e7793c3ca20801109&user_id=16'.format(
                    obj.id
                )
                ret = requests.post(url)
                print('ret.text-----> ', ret.text)
                print(ret.json())
                print('obj.id----------> ', obj.id)
                break



    return JsonResponse(response.__dict__)




