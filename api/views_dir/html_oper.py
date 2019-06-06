from django.shortcuts import render, redirect
from api import models
from publicFunc import Response
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode
from publicFunc.host import host_url
from PIL import Image,ImageFont,ImageDraw
from publicFunc.image_color_recognition import image_color_recognition
from publicFunc.article_oper import get_ent_info
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
import datetime


def html_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')  # 用户ID
    if oper_type == 'zhengnengliang':
        pass
        # posters = request.GET.get('posters')  # 海报ID
        # posters_objs = models.Posters.objects.get(id=posters)
        # img_path = posters_objs.posters_url
        #
        # user_obj = models.Userprofile.objects.get(id=user_id)
        #
        # img_url = img_path.split(host_url)[1]  # 切除域名
        # image = Image.open(img_url).convert('RGBA')
        # color = image_color_recognition(image)  # 识别图片颜色 给出对应文字颜色
        # print('b64decode(user_obj.name)----------> ', b64decode(user_obj.name))
        # # color = (0,0,0)
        # data = {
        #     'img_path': img_path,
        #     'name': b64decode(user_obj.name),
        #     'phone': user_obj.phone_number,
        #     'set_avator': user_obj.set_avator,
        #     'color': color,
        # }
        # print('data====----> ', data)
        # return render(request, 'zhengnengliang.html', locals())
    elif oper_type == 'tuiguang':
        data = get_ent_info(user_id)
        weichat_api_obj = WeChatApi(data)
        qc_code_url = weichat_api_obj.generate_qrcode({'inviter_user_id': user_id})
        print(qc_code_url)

        expire_date = (datetime.datetime.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        data = {
            'qc_code_url': qc_code_url,
            'expire_date': expire_date,
            'user_name': data.get('user_name'),  # 用户名称
            'user_set_avator': data.get('user_set_avator'),  # 头像
        }

        return render(request, 'tuiguang.html', locals())


    return JsonResponse(response.__dict__)