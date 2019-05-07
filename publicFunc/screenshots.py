import os, sys
from selenium import webdriver
from tianyanApi import settings
from PIL import Image,ImageFont,ImageDraw
from publicFunc.qiniu_oper import update_qiniu


# 截图

def screenshots(poster_url, path):
    print('--------------------------截图===========截图------>', poster_url)
    if 'linux' in sys.platform:  # 获取平台
        base_dir_path = os.path.join(settings.BASE_DIR, 'api', 'views_dir', 'tools')
        phantomjs_path = base_dir_path + '/phantomjs'

    else:
        base_dir_path = 'api/views_dir/tools'
        # base_dir_path = os.path.join(settings.BASE_DIR, 'api', 'views_dir', 'tools')
        phantomjs_path = base_dir_path + '/phantomjs.exe'
    print('phantomjs_path----------> ', phantomjs_path)

    driver = webdriver.PhantomJS(executable_path=phantomjs_path)
    driver.implicitly_wait(10)
    driver.maximize_window()
    driver.get(poster_url)
    element = driver.find_element_by_id("jietu")
    locations = element.location
    sizes = element.size
    rangle = (locations['x'], locations['y'], int(locations['x'] + sizes['width']), sizes['height'])
    print('rangle-------> ', rangle)
    driver.save_screenshot(path)  # 截图
    img = Image.open(path)
    jpg = img.crop(rangle)  # 左上右下
    jpg.save(path)
    driver.quit()
    img_path = update_qiniu(path)  # 上传七牛云
    return img_path

if __name__ == '__main__':
    post_url = 'http://127.0.0.1:8008/api/html_oper/tuiguang?user_id=1'
    # post_url = 'https://www.cnblogs.com/leeboke/p/5014131.html'
    path = './1.png'
    screenshots(post_url, path)
