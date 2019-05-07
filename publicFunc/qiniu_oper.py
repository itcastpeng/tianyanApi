import qiniu, requests, os, base64
from publicFunc.account import randon_str
from qiniu import put_file

def qiniu_get_token():
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    token = q.upload_token(bucket_name)  # 可以指定key 图片名称
    return token

# 上传七牛云
def update_qiniu(img_path, token):
    # url = 'https://up-z1.qiniup.com/'
    # data = {
    #     'token': token,
    # }
    # files = {
    #     'file': open(img_path, 'rb')
    # }
    # headers = {
    #     'Content-Type': 'multipart/form-data; charset=utf-8',
    #     'Access-Control-Allow-Methods': 'GET, POST, PUT,DELETE'
    # }
    # ret = requests.post(url, data=data, files=files, headers=headers)
    print('----------------上传七牛云--------------')
    key = randon_str()
    ret, info = put_file(token, key, img_path)
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
    token = qiniu_get_token()
    update_qiniu('1.png', token)

    # url = 'http://thirdwx.qlogo.cn/mmopen/PeW1cmicnQppB7nYSsEKoR2HzTic5eMpTeMPEqmMtnLoXgt3Ro0z5nSNbbpL5fV6gzDWZbudSMrRleZDeAyKTNoZyKzd4YriafO/132'
    # requests_img_download(url)

