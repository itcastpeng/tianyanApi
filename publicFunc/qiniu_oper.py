import qiniu, requests, os



def qiniu_get_token():
    SecretKey = 'wVig2MgDzTmN_YqnL-hxVd6ErnFhrWYgoATFhccu'
    AccessKey = 'a1CqK8BZm94zbDoOrIyDlD7_w7O8PqJdBHK-cOzz'
    q = qiniu.Auth(AccessKey, SecretKey)
    bucket_name = 'bjhzkq_tianyan'
    token = q.upload_token(bucket_name)  # 可以指定key 图片名称
    return token

# 上传七牛云
def update_qiniu(img_path, token):
    url = 'https://up-z1.qiniup.com/'
    data = {
        'token': token,
    }
    files = {
        'file': open(img_path, 'rb')
    }
    ret = requests.post(url, data=data, files=files)

    if 'http://tianyan.zhugeyingxiao.com/' not in img_path and os.path.exists(img_path):
        os.remove(img_path)  # 删除本地图片
    img_path = 'http://tianyan.zhugeyingxiao.com/' + ret.json().get('key')
    return img_path
