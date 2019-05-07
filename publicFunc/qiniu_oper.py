import qiniu, requests, os, base64
from publicFunc.account import randon_str
from qiniu import put_file, Zone, set_default


# 上传七牛云
def update_qiniu(img_path):
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    key = randon_str()

    token = q.upload_token(bucket_name, key, 3600)  # 可以指定key 图片名称

    print('----------------上传七牛k云--------------')
    ret, info = put_file(token, key, img_path)
    print('###############@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#################_------------> ', ret, info)
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
    update_qiniu('1.png')

    # url = 'http://thirdwx.qlogo.cn/mmopen/PeW1cmicnQppB7nYSsEKoR2HzTic5eMpTeMPEqmMtnLoXgt3Ro0z5nSNbbpL5fV6gzDWZbudSMrRleZDeAyKTNoZyKzd4YriafO/132'
    # requests_img_download(url)

