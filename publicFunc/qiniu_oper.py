import qiniu, requests, os, base64
from publicFunc.account import randon_str
from qiniu import put_file, Zone, set_default


# 上传七牛云
def update_qiniu(img_path):
    # 需要填写你的 Access Key 和 Secret Key
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'

    # 构建鉴权对象
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    key = randon_str()

    policy = {  # 指定上传文件的格式 等

    }
    token = q.upload_token(bucket_name, None, 360000, policy)  # 可以指定key 图片名称

    ret, info = put_file(token, None, mime_type="text/js", file_path=img_path)



    # headers = {
    #     'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
    # }

    # url = 'https://up-z1.qiniup.com/'
    #
    # data = {
    #     'token': token
    # }
    # files = {
    #     'file':open(img_path, 'rb')
    # }
    #
    # print('----------------上传七牛k云--------------')
    # ret = requests.post(url, data=data, files=files, headers=headers)

    # zone = Zone(
    #     up_host='https://up-z1.qiniup.com/',
    #     up_host_backup='https://upload-z1.qiniup.com',
    #     io_host='http://iovip-z1.qbox.me',
    #     scheme='https')
    # set_default(default_zone=zone)
    #



    print('###############@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#################_------------> ', ret)
    if 'http://tianyan.zhugeyingxiao.com/' not in img_path and os.path.exists(img_path):
        os.remove(img_path)  # 删除本地图片
    img_path = 'http://tianyan.zhugeyingxiao.com/' + ret.get('key')
    return img_path

# 请求图片地址保存本地
def requests_img_download(old_url):
    ret = requests.get(old_url)
    path = os.path.join('statics', 'img', randon_str() + '.png')
    with open(path, 'wb') as e:
        e.write(ret.content)
    return path


if __name__ == '__main__':
    update_qiniu('1.jpg')

    # url = 'http://thirdwx.qlogo.cn/mmopen/PeW1cmicnQppB7nYSsEKoR2HzTic5eMpTeMPEqmMtnLoXgt3Ro0z5nSNbbpL5fV6gzDWZbudSMrRleZDeAyKTNoZyKzd4YriafO/132'
    # requests_img_download(url)

