from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from api.forms import upload_form
import os, requests, re, hashlib, platform, time, random, json, base64

sysstr = platform.system()

# 加密名字
def encryption():
    string = str(random.randint(10, 99)) + str(int(time.time())) + str(random.randint(10, 99))
    pwd = str(string)
    hash = hashlib.md5()
    hash.update(pwd.encode())
    return hash.hexdigest()

# 获取名字后缀
def get_name_suffix(fileName):
    houzhui = re.search(r'[^.]+$', fileName).group(0)  # 获取点后面的后缀
    return houzhui



# 分片
@csrf_exempt
def upload_shard(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        print('request.POST------> ', request.FILES)

        forms_obj = upload_form.imgUploadForm(request.POST)
        if forms_obj.is_valid():
            img_data = request.FILES.get('img_data')       # 文件内容
            img_name = forms_obj.cleaned_data.get('img_name')       # 图片名称
            img_source = forms_obj.cleaned_data.get('img_source')   # 文件类型
            timestamp = forms_obj.cleaned_data.get('timestamp')     # 时间戳
            chunk = forms_obj.cleaned_data.get('chunk')             # 第几片文件
            expanded_name = get_name_suffix(img_name)               # 获取扩展名称
            if img_source == 'file':
                if expanded_name.lower().strip() not in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']:
                    response.code = 301
                    response.msg = '请上传正确(文件)格式'
                    return JsonResponse(response.__dict__)

            elif img_source == 'img':
                if expanded_name.lower().strip() not in ['bmp', 'dib', 'rle', 'emf', 'gif', 'jpg', 'jpeg', 'jpe', 'jif',
                                                         'pcx', 'dcx', 'pic', 'png', 'tga', 'tif', 'tiffxif', 'wmf', 'jfif', 'pdf']:
                    response.code = 301
                    response.msg = '请上传正确(图片)格式'
                    return JsonResponse(response.__dict__)

            # elif img_source == 'video':
            #     if expanded_name.lower().strip() not in ['rm', 'rmvb', '3gp','avi','mpeg','mpg','mkv','dat','asf',
            #             'wmv', 'flv', 'mov','mp4','ogg','ogm']:
            #         response.code = 301
            #         response.msg = '请上传正确视频格式'
            #         return JsonResponse(response.__dict__)

            else:
                response.code = 301
                response.msg = '请上传正确格式'
                return JsonResponse(response.__dict__)

            img_name = timestamp + "_" + str(chunk) + '.' + expanded_name
            img_save_path = os.path.join('statics', 'tmp', img_name)
            with open(img_save_path, "wb") as f:
                data = ''
                for chunk in img_data.chunks():
                    data += str(chunk)
                f.write(eval(data))
            if os.path.exists(img_save_path):
                response.code = 200
                response.msg = '上传成功'
            else:
                response.code = 301
                response.msg = '上传失败'
        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)


# 合并
@csrf_exempt
def merge(request):
    response = Response.ResponseObj()
    if request.method == 'POST':
        forms_obj = upload_form.imgMergeForm(request.POST)
        if forms_obj.is_valid():

            img_source = forms_obj.cleaned_data.get('img_source')   # 文件类型
            img_name = forms_obj.cleaned_data.get('img_name')       # 图片名称
            timestamp = forms_obj.cleaned_data.get('timestamp')     # 时间戳
            chunk_num = forms_obj.cleaned_data.get('chunk_num')     # 一共多少份
            expanded_name = get_name_suffix(img_name)               # 获取扩展名称

            file_dir = ''
            file_type = '图片'

            if img_source == 'img':
                file_dir = os.path.join('statics', 'img')

            elif img_source == 'file':
                file_dir = os.path.join('statics', 'file')
                file_type = '文件'

            # elif img_source == 'video':
            #     file_dir = os.path.join('statics', 'video')
            #     file_type = '视频'

            else:
                response.code = 402
                response.msg = '合并异常'

            fileData = ''
            for chunk in range(chunk_num):
                file_name = timestamp + "_" + str(chunk) + '.' + expanded_name
                file_save_path = os.path.join('statics', 'tmp', file_name)
                if os.path.exists(file_save_path):
                    print('---file_save_path---file_save_path-----', file_save_path)
                    with open(file_save_path, 'rb') as f:
                        fileData += str(f.read())
                    # os.remove(file_save_path)  # 删除分片 文件


            video_name = encryption() + img_name
            path = os.path.join(file_dir, video_name)
            try:
                with open(path, 'ab')as f:
                    f.write(eval(fileData))         # 写入
            except Exception as e:
                print('e--> ', e)
            response.data = {'url': path}


            response.code = 200
            response.msg = "上传{}成功".format(file_type)

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = '请求异常'
    return JsonResponse(response.__dict__)




















# 上传图片/视频
# @csrf_exempt
# @account.is_token(models.hzxy_userprofile)
# def img_upload(request, oper_type):
#     response = Response.ResponseObj()
#
#     if (sysstr == "Windows"):  # windows 系统
#         YUMING = 'http://192.168.10.207:8004/'
#     else:
#         YUMING = 'http://xueyuan.bjhzkq.com/'
#
#
#     # 上传文件
#     if oper_type == 'file_upload':
#         test = request.GET.get('test')     # 判断是否为机器请求
#         file_obj = request.FILES.get('file')
#
#         if file_obj:
#             fileName, houzhui = get_name_suffix(file_obj.name) # 获取点后面的后缀
#
#             # 判断是否有后缀
#             if '.' not in fileName:
#                 response.code = 301
#                 response.msg = '后缀名不能为空'
#                 return JsonResponse(response.__dict__)
#
#             # 判断文件格式
#             if houzhui.lower().strip() not in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf']:
#                 response.code = 301
#                 response.msg = '请上传正确(文件)格式'
#                 return JsonResponse(response.__dict__)
#
#             if test:        # 自动上传数据 使用原文件名
#                 file = fileName
#
#             else:  # 用户手动上传
#                 file_name = encryption() # 加密字符串
#                 file = file_name + '.' + houzhui
#
#             # 写入
#             file_abs_name = os.path.join("statics", 'file', file)
#             with open(file_abs_name, "wb") as f:
#                 for chunk in file_obj.chunks():
#                     f.write(chunk)
#
#             # 拼接路径
#             path_name = '{}statics/file/'.format(YUMING) + file
#             print('path_name=========> ',path_name)
#             response.code = 200
#             response.msg = '上传成功'
#             response.data = path_name
#
#         else:
#             response.code = 301
#             response.msg = '上传为空'
#
#     # 上传图片
#     elif oper_type == 'book_upload':
#         test = request.GET.get('test')     # 判断是否为机器请求
#         file_obj = request.FILES.get('file')
#
#         if file_obj:
#             fileName = file_obj.name
#             houzhui = re.search(r'[^.]+$', fileName).group(0)   # 获取点后面的后缀
#
#             if test:    # 本地上传数据
#                 file = fileName
#                 if '127' in YUMING:
#                     file = str(1) + fileName
#
#             else:   # 外网用户上传
#                 file_name = encryption()    # 加密字符串
#                 # 判断是否有后缀
#                 file = file_name + '.' + houzhui
#                 if '.' not in fileName:
#                     response.code = 301
#                     response.msg = '后缀名不能为空'
#                     return JsonResponse(response.__dict__)
#
#             # 判断图片格式
#             if houzhui.lower().strip() not in ['bmp', 'dib', 'rle', 'emf', 'gif', 'jpg', 'jpeg', 'jpe',
#                     'jif', 'pcx', 'dcx', 'pic', 'png', 'tga', 'tif', 'tiffxif', 'wmf', 'jfif', 'pdf']:
#                 response.code = 301
#                 response.msg = '请上传正确(图片)格式'
#                 return JsonResponse(response.__dict__)
#
#             # 写入
#             file_abs_name = os.path.join("statics", 'img', file)
#             with open(file_abs_name, "wb") as f:
#                 for chunk in file_obj.chunks():
#                     f.write(chunk)
#
#             # 拼接路径
#             path_name = '{YUMING}statics/img/'.format(YUMING=YUMING) + file
#             print('path_name=========> ',path_name)
#             response.code = 200
#             response.msg = '上传成功'
#             response.data = path_name
#
#         else:
#             response.code = 301
#             response.msg = '上传为空'
#
#     # 上传视频
#     elif oper_type == 'video_upload':
#         file_obj = request.FILES.get('file')
#         test = request.GET.get('test')  # 判断是否为机器请求
#         if file_obj:
#             fileName = file_obj.name
#             houzhui = re.search(r'[^.]+$', fileName).group(0)
#
#             # 判断是否有后缀
#             if '.' not in fileName:
#                 response.code = 301
#                 response.msg = '后缀名不能为空'
#                 return JsonResponse(response.__dict__)
#
#             if test:
#                 file = fileName
#                 if '127' in YUMING:
#                     file = str(1) + fileName
#
#             else:
#                 # 判断视频格式
#                 file_name = encryption()  # 加密字符串
#                 file = file_name + '.' + houzhui
#
#             if houzhui.lower().strip() not in ['rm', 'rmvb', '3gp','avi','mpeg','mpg','mkv','dat','asf',
#                     'wmv', 'flv', 'mov','mp4','ogg','ogm']:
#                 response.code = 301
#                 response.msg = '请上传正确视频格式'
#                 return JsonResponse(response.__dict__)
#
#             # 写入
#             file_abs_name = os.path.join("statics", 'video', file)
#             with open(file_abs_name, "wb") as f:
#                 for chunk in file_obj.chunks():
#                     f.write(chunk)
#
#             # 拼接视频路径
#             path_name = '{}statics/video/'.format(YUMING) + file
#
#             cover_path = ''
#             # 截取视频第一帧 (封面)
#             if not test:
#                 num = 0
#                 time.sleep(1)
#                 while True:
#                     if num >= 3:
#                         break
#                     work_path = os.path.exists('statics/video/' + file)
#                     if work_path:
#
#                         path = 'statics/video/' + file
#                         cover_path = 'statics/img/' + encryption() + '.jpg'
#                         if (sysstr == "Windows"):   # windows 系统
#                             cmd = "C:\\baidu_Downloads\\ffmpeg-20190114-d52a1be-win64-static\\bin/ffmpeg -i {video_path} -y -f image2 -ss 8 -t 0.001 -s 1024*768 {img_path}".format(
#                             video_path=path,
#                             img_path=cover_path
#                         )
#                         elif (sysstr == "Linux"):   # Linux 系统
#                             cmd = "/usr/local/bin/ffmpeg -i {video_path} -y -f image2 -ss 8 -t 0.001 -s 1024*768 {img_path}".format(
#                                 video_path=path,
#                                 img_path=cover_path
#                             )
#                         else:
#                             cmd = ''
#
#                         os.system(cmd)
#                         break
#
#                     else:
#                         num += 1
#                         continue
#
#             response.code = 200
#             response.msg = '上传成功'
#             response.data = {
#                 'path_name':path_name,
#                 'cover_path':YUMING + cover_path,
#             }
#         else:
#             response.code = 301
#             response.msg = '上传为空'
#
#
#     # 图片,视频 上传到线上服务器(内部服务器定时刷新, statics图片视频上传线上)
#     elif oper_type == 'upload_online':
#         path_list = ['video'] # 路径
#         for path in path_list:
#             # 判断该路径下是否有文件
#             work_path = os.listdir(os.path.join("statics", path))
#             if work_path:
#                 # 循环该文件夹中文件
#                 for i in range(0, len(work_path)):
#                     file_path = os.path.join('statics', path, work_path[i])
#
#                     params = {
#                         'timestamp': '1545822031837',
#                         'rand_str': 'a02d66aba9e84f59a0912513eab37eaf',
#                         'user_id': '2',
#                         'test': '1',
#                     }
#
#                     if path == 'video':
#                         qubie_path = 'video_upload'  # 上传路径拼接
#                     else:
#                         qubie_path = 'book_upload'
#                     url = '{YUMING}/upload_video_book/{qubie_path}'.format(YUMING=YUMING, qubie_path=qubie_path)
#
#                     try:
#                         # 打开文件并且上传到服务器
#                         with open(file_path, 'rb') as f:
#                             data = {'file': f}
#                             ret = requests.post(url, files=data, params=params)
#
#                         if ret.json():
#                             if int(ret.json().get('code')) == 200:
#                                 os.remove(file_path)
#
#                     except Exception:
#                         continue
#                 response.code = 200
#                 response.msg = '上传成功'
#
#             else:
#                 response.code = 301
#                 response.msg = '无任务'
#
#     else:
#         response.code = 402
#         response.msg = '请求异常'
#
#     return JsonResponse(response.__dict__)
