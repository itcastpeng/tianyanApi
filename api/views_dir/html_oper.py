from django.shortcuts import render, redirect
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode



def html_oper(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'zhengnengliang':
        posters = request.GET.get('posters')  # 海报ID
        user_id = request.GET.get('user_id')  # 用户ID
        color = request.GET.get('color')  # 用户ID
        posters_objs = models.Posters.objects.get(id=posters)
        img_path = posters_objs.posters_url

        user_obj = models.Userprofile.objects.get(id=user_id)

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