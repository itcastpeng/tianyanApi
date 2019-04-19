from django.shortcuts import render, redirect
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode
from publicFunc.host import host_url
from PIL import Image,ImageFont,ImageDraw

from publicFunc.image_color_recognition import image_color_recognition

def html_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'zhengnengliang':
        posters = request.GET.get('posters')  # 海报ID
        user_id = request.GET.get('user_id')  # 用户ID
        posters_objs = models.Posters.objects.get(id=posters)
        img_path = posters_objs.posters_url

        user_obj = models.Userprofile.objects.get(id=user_id)

        img_url = img_path.split(host_url)[1]  # 切除域名
        image = Image.open(img_url).convert('RGBA')
        color = image_color_recognition(image)  # 识别图片颜色 给出对应文字颜色
        print('b64decode(user_obj.name)----------> ', b64decode(user_obj.name))
        # color = (0,0,0)
        data = {
            'img_path': img_path,
            'name': b64decode(user_obj.name),
            'phone': user_obj.phone_number,
            'set_avator': user_obj.set_avator,
            'color': color,
        }
        print('data====----> ', data)
        return render(request, 'zhengnengliang.html', locals())



    return JsonResponse(response.__dict__)