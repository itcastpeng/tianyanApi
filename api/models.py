from django.db import models


# 企业
class Enterprise(models.Model):
    name = models.CharField(verbose_name='企业名称', max_length=64)
    password = models.CharField(verbose_name='密码', max_length=256)
    token = models.CharField(verbose_name="token值", max_length=128)
    phone = models.CharField(verbose_name="电话", max_length=16)
    role_choices = (
        (1, "OEM用户"),
        (2, "超级管理员"),
    )
    role = models.SmallIntegerField(verbose_name='角色', choices=role_choices, default=1)
    appid = models.CharField(verbose_name='公众号APPID', max_length=128, null=True)
    appsecret = models.CharField(verbose_name='公众号APPSECRET', max_length=256, null=True)
    access_token = models.CharField(verbose_name='公众号access_token', max_length=256, null=True)
    oper_user = models.ForeignKey('Enterprise', verbose_name='创建人')
    create_datetime = models.CharField(verbose_name="access_token更新时间", max_length=32)
    create_date = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    status_choices = (
        (1, "已审核"),
        (2, "未审核"),
        (3, "已驳回"),
    )
    status = models.SmallIntegerField(verbose_name='是否审核', choices=status_choices, default=2)

    primary_distribution = models.IntegerField(verbose_name='一级分销占比', default=30)
    secondary_distribution = models.IntegerField(verbose_name='二级分销占比', default=15)
    working_days = models.IntegerField(verbose_name='创建天数时长', default=1)
    weChat_qr_code = models.CharField(verbose_name='微信二维码', max_length=512, null=True)

# 修改 分销记录
class distribution_log(models.Model):
    create_user = models.ForeignKey('Enterprise', verbose_name='创建人')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    old_primary_distribution = models.IntegerField(verbose_name='原一级分销占比')
    old_secondary_distribution = models.IntegerField(verbose_name='原二级分销占比')

    primary_distribution = models.IntegerField(verbose_name='一级分销占比')
    secondary_distribution = models.IntegerField(verbose_name='二级分销占比')
    stop_time = models.CharField(verbose_name='截止时间', max_length=64)
    status_choices = (
        (1, '已审核'),
        (2, '已驳回'),
        (3, '未审核'),
    )
    status = models.SmallIntegerField(verbose_name='审核状态', choices=status_choices, default=3)

# 微商用户表
class Userprofile(models.Model):
    name = models.CharField(verbose_name="姓名", max_length=128)

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices)
    country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)

    phone_number = models.CharField(verbose_name="手机号", max_length=11, null=True, blank=True)
    signature = models.TextField(verbose_name="个性签名", null=True, blank=True)
    show_product = models.BooleanField(verbose_name="文章底部是否显示产品", default=True)

    token = models.CharField(verbose_name="token值", max_length=128)

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    register_date = models.DateField(verbose_name="注册时间", auto_now_add=True)
    overdue_date = models.DateField(verbose_name="过期时间")

    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)

    set_avator = models.CharField(
        verbose_name='头像',
        default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg',
        max_length=256
    )  # 首次进入 为微信头像 可修改

    headimgurl = models.CharField(verbose_name='记录微信头像', max_length=256, null=True)
    wechat_name = models.CharField(verbose_name='微信名称', max_length=64, null=True)

    qr_code = models.CharField(verbose_name="微信二维码", max_length=256, null=True, blank=True)

    openid = models.CharField(verbose_name="微信公众号openid", max_length=64)

    vip_type_choices = (
        (0, "vip已过期"),
        (1, "试用会员"),
        (2, "高级会员"),
    )
    vip_type = models.SmallIntegerField(verbose_name="会员类型", choices=vip_type_choices, default=1)

    recommend_classify = models.ManyToManyField(
        'Classify', verbose_name="推荐分类",
        related_name="userprofile_recommend_classify"
    )
    brand_classify = models.ManyToManyField(
        'Classify', verbose_name="品牌分类",
        related_name="userprofile_brand_classify"
    )
    # team = models.ManyToManyField('Team', verbose_name="所属团队", related_name="userprofile_team")

    inviter = models.ForeignKey(
        'self',
        verbose_name="邀请人",
        related_name="userprofile_inviter",
        null=True,
        blank=True,
        default=None
    )

    small_shop_name = models.CharField(verbose_name='微店名称', max_length=32, default='店小二')
    small_shop_avator = models.CharField(verbose_name='微店头像', max_length=256, default='http://tianyan.zhangcong.top/statics/img/f4578f133cd9fc4b88449b1e373c5d4cnews4.png')
    small_shop_image = models.CharField(verbose_name='微店顶部静态横图', max_length=256, null=True, blank=True)

    top_advertising = models.TextField(verbose_name='顶层广告' ,null=True, blank=True)
    end_advertising = models.TextField(verbose_name='底层广告' ,null=True, blank=True)

    enterprise = models.ForeignKey('Enterprise', verbose_name='企业', default=1)

    cumulative_amount = models.CharField(verbose_name='累计钱数', max_length=64, default=0)
    make_money = models.CharField(verbose_name='待提钱数', max_length=64, default=0)

    last_active_time = models.DateTimeField(verbose_name='用户最后活跃时间', null=True) # 记录用户最后一次与公众号互动的时间
    is_send_msg = models.BooleanField(verbose_name='是否发送过互动超时消息', default=0) # 互动则为未发送 发送消息后改为1

    message_remind_status = (
        (0, '立即提醒我'),
        (1, '15分钟内提醒我一次(汇总提醒)'),
        (2, '1小时内提醒我一次(汇总提醒)'),
        (3, '3小时内提醒我一次(汇总提醒)'),
        (4, '关闭提醒')
    )
    message_remind = models.SmallIntegerField(verbose_name='消息提醒', choices=message_remind_status, default=0)
    last_message_remind_time = models.DateTimeField(verbose_name='最后发送消息提醒时间', null=True)

    # 我的名片 名字下边简介
    introduction = models.CharField(verbose_name='名片简介', max_length=512, null=True)

    promote_earning_qr_code_pictures = models.CharField(verbose_name='推广赚钱二维码图片', max_length=512, null=True)
    generate_models_qr_code_pictures_time = models.DateField(verbose_name='生成推广赚钱二维码图片时间', null=True)

# 客户表(用户的客户)
class Customer(models.Model):
    name = models.CharField(verbose_name="微信姓名", max_length=128)

    sex_choices = (
        (1, "男"),
        (2, "女"),
    )
    sex = models.SmallIntegerField(verbose_name="性别", choices=sex_choices)
    country = models.CharField(verbose_name="国家", max_length=128, null=True, blank=True)
    province = models.CharField(verbose_name="省份", max_length=128, null=True, blank=True)
    city = models.CharField(verbose_name="城市", max_length=128, null=True, blank=True)

    phone_number = models.CharField(verbose_name="手机号", max_length=11, null=True, blank=True)
    token = models.CharField(verbose_name="token值", max_length=128)

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    set_avator = models.CharField(
        verbose_name='头像',
        default='http://api.zhugeyingxiao.com/statics/imgs/setAvator.jpg',
        max_length=256
    )
    openid = models.CharField(verbose_name="openid", max_length=64)
    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)

# 客户信息备注 对应 用户
class customer_information_the_user(models.Model):
    user = models.ForeignKey(to='Userprofile', verbose_name='用户', null=True, blank=True)
    customer = models.ForeignKey(to='Customer', verbose_name='客户', null=True, blank=True)
    # remote_type_choices = (
    #     (1, "跟进状态"),
    #     (2, "产品购买"),
    #     (3, "课程活动"),
    # )
    # remote_type = models.SmallIntegerField(verbose_name="备注类型", choices=remote_type_choices, default=1)

    remote = models.TextField(verbose_name="记录信息，存json格式", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 用户备注客户信息  所有信息 性别等。。。。
class user_comments_customer_information(models.Model):
    customer = models.ForeignKey('Customer', verbose_name="客户")
    user = models.ForeignKey(to='Userprofile', verbose_name='用户', null=True, blank=True)
    customer_info = models.TextField(verbose_name='客户信息', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 文章管理
class Article(models.Model):
    title = models.CharField(verbose_name="文章标题", max_length=256, null=True)
    summary = models.TextField(verbose_name="文章描述", null=True)
    content = models.TextField(verbose_name="文章内容", null=True)
    classify = models.ManyToManyField('Classify', verbose_name='所属分类')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('Userprofile', verbose_name='创建用户', related_name="article_create_user", null=True)
    source_link = models.CharField(verbose_name="微信文章链接", max_length=256, null=True, blank=True)
    look_num = models.IntegerField(verbose_name="查看次数", default=0)
    like_num = models.IntegerField(verbose_name="点赞(喜欢)次数", default=0)
    cover_img = models.CharField(verbose_name='封面图', max_length=256, null=True, blank=True)
    style = models.TextField(verbose_name='文章样式', null=True, blank=True)
    ownership_team = models.ForeignKey('Team', verbose_name='归属团队', null=True)

    original_link = models.TextField(verbose_name="原文链接", null=True)

# 文章/品牌 分类
class Classify(models.Model):
    last_update_time = models.DateField(verbose_name='最后更新时间', null=True) # 爬取数据最后一次时间 只限创建人为空的
    name = models.CharField(verbose_name="分类名称", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey(
        'Userprofile',
        verbose_name='创建用户',
        related_name="classify_create_user",
        null=True,
        blank=True
    )  # 该字段为空，表示为默认(推荐)分类，不为空表示品牌分类

# 客户/用户 查看文章日志表
class SelectArticleLog(models.Model):
    # action_choices = (
    #     (1, "分享文章"),    # 用户分享出去的
    #     (2, "热门文章"),    # 系统自动发布热门文章
    # )
    # action = models.SmallIntegerField(verbose_name='判断是分享的还是系统发布热门的', choices=action_choices, default=1)
    customer = models.ForeignKey('Customer', verbose_name="查看人", null=True) # 此字段为空 为用户查看文章
    inviter = models.ForeignKey(
        'Userprofile',
        verbose_name="分享人",
        related_name="select_article_log_inviter",
        null=True,
        blank=True,
        default=None
    )

    article = models.ForeignKey('Article', verbose_name="查看文章")
    close_datetime = models.DateTimeField(verbose_name="关闭页面时间", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    click_modify = models.BooleanField(verbose_name='客户 是否点击了修改成我的名片', default=0)

# 客户点赞文章日志表
class SelectClickArticleLog(models.Model):
    user = models.ForeignKey('Userprofile', verbose_name='用户点赞', null=True)
    customer = models.ForeignKey('Customer', verbose_name="客户点赞", null=True)
    article = models.ForeignKey('Article', verbose_name="点赞文章")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 商品分类
class GoodsClassify(models.Model):
    oper_user = models.ForeignKey(to='Userprofile', verbose_name='归属人')
    # parent_classify = models.ForeignKey(to='self', verbose_name='父级分类名称', null=True, blank=True)
    goods_classify = models.CharField(verbose_name='分类名称', max_length=16)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 商品
class Goods(models.Model):
    goods_classify = models.ForeignKey(to='GoodsClassify', verbose_name='归属分类')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    goods_name = models.CharField(verbose_name='商品名称', max_length=128)
    price = models.CharField(verbose_name='价格', max_length=16)
    inventory = models.IntegerField(verbose_name='库存', default=1)
    freight = models.IntegerField(verbose_name='运费', default=0)
    goods_describe = models.TextField(verbose_name='商品描述', default=[])
    point_origin = models.CharField(verbose_name='发货地', max_length=256)
    goods_status_choices = (
        (1, '上架'),
        (2, '下架')
    )
    goods_status = models.SmallIntegerField(verbose_name='商品状态', choices=goods_status_choices, default=2)
    # goods_picture = models.TextField(verbose_name='商品图片')
    cover_img = models.CharField(verbose_name='封面图', max_length=256, null=True, blank=True)

# 客户查看商品 日志表
class customer_look_goods_log(models.Model):
    customer = models.ForeignKey(to='Customer', verbose_name='哪个客户查看了商品', null=True)
    goods = models.ForeignKey(to='Goods', verbose_name='查看了哪个商品', null=True)
    user = models.ForeignKey(to='Userprofile', verbose_name='查看的那个用户', null=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    close_datetime = models.DateTimeField(verbose_name="关闭页面时间", null=True, blank=True)

# 海报管理
class Posters(models.Model):
    create_user = models.ForeignKey('Userprofile', verbose_name='创建用户', related_name="posters_create_user")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    posters_url = models.CharField(verbose_name='海报链接', max_length=256, null=True, blank=True)
    posters_choices = (
        (1, '正能量'),
        (2, '邀请函')
    )
    posters_status = models.SmallIntegerField(verbose_name='海报类型', choices=posters_choices, default=1)

# 团队表
class Team(models.Model):
    name = models.CharField(verbose_name="团队名称", max_length=128)
    create_user = models.ForeignKey('Userprofile', verbose_name="创建人", related_name="team_create_user")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 微商用户和团队关系表
class UserprofileTeam(models.Model):
    user = models.ForeignKey('Userprofile', verbose_name="微商用户")
    team = models.ForeignKey('Team', verbose_name="团队")
    type_choices = (
        (1, "普通成员"),
        (2, "管理员"),
    )
    type = models.SmallIntegerField(verbose_name="成员类型", choices=type_choices, default=1)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 保存微信回调code用 (获取用户信息 微信会回调多次 code一致 多次请求微信同样code获取不到用户信息)
class save_code(models.Model):
    save_code = models.CharField(verbose_name='存在的code', max_length=128, null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 客户给公众号发送 同一时间 多次重复消息  发送一次会回调多次 微信回调问题
class send_msg_duplicate(models.Model):
    user_id = models.IntegerField(verbose_name='记录user_id避免重复', null=True)
    create_date_time = models.CharField(verbose_name='创建时间', max_length=64, null=True)

# 天眼谁看了我
class day_eye_celery(models.Model):
    user = models.ForeignKey(to='Userprofile', verbose_name='哪个用户的数据', null=True)
    customer = models.ForeignKey(to='Customer', verbose_name='哪个客户', null=True)
    text = models.CharField(verbose_name='文本内容', max_length=256, null=True)
    status_choices = (
        (1, '文章'),
        (2, '商品')
    )
    status = models.SmallIntegerField(verbose_name='类别 区分文章和商品', choices=status_choices, null=True)
    is_new_msg = models.BooleanField(verbose_name='是否有新消息', default=False) # 判断 用户最后一次点击查看 该客户时间 如果日志有大于最后一次点击的 则有新消息
    last_click_customer = models.DateTimeField(verbose_name='最后一次点击该客户', null=True)
    create_date = models.DateTimeField(verbose_name='创建时间', null=True)

# 设置消息提醒 未提醒的消息 汇总提醒消息
class summary_message_reminder(models.Model):
    user = models.ForeignKey('Userprofile', verbose_name='提醒的人')
    customer = models.ForeignKey('Customer', verbose_name='查看 (文章) 人')
    check_type = models.CharField(verbose_name='查看了什么名称 (文章/微店)', max_length=32)
    title = models.CharField(verbose_name='文章标题', max_length=256)
    is_send = models.BooleanField(verbose_name='是否发送', default=0)
    select_num = models.IntegerField(verbose_name='查看次数', default=1)

    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

# 续费管理
class renewal_management(models.Model):
    price = models.CharField(verbose_name='价格', max_length=128, null=True, blank=True)
    original_price = models.CharField(verbose_name='原价格', max_length=128, null=True, blank=True)
    the_length_choices = (
        (1, '三个月'),
        (2, '一年'),
        (3, '三年'),
    )
    the_length = models.SmallIntegerField(verbose_name='时长', choices=the_length_choices, default=1)
    renewal_number_days = models.IntegerField(verbose_name='续费天数', default=30)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    create_user = models.ForeignKey('Enterprise', verbose_name='创建人', null=True, blank=True)

# 修改续费日志
class update_renewal_log(models.Model):
    price = models.CharField(verbose_name='修改前价格', max_length=128, null=True, blank=True)
    original_price = models.CharField(verbose_name='修改前原价格', max_length=128, null=True, blank=True)

    update_price = models.CharField(verbose_name='修改后价格', max_length=128, null=True, blank=True)
    update_original_price = models.CharField(verbose_name='修改后原价格', max_length=128, null=True, blank=True)
    renewal = models.ForeignKey('renewal_management', verbose_name='对应续费')
    status_choices = (
        (1, '审核通过'),
        (2, '审核驳回'),
        (3, '未审核')
    )
    status = models.SmallIntegerField(verbose_name='审核状态', choices=status_choices, default=3)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

# 续费日志
class renewal_log(models.Model):
    pay_order_no = models.CharField(verbose_name='订单号', max_length=128, null=True, blank=True)
    the_length = models.CharField(verbose_name='时长', max_length=128, null=True, blank=True)
    renewal_number_days = models.IntegerField(verbose_name='续费天数', default=30)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    create_user = models.ForeignKey('Userprofile', verbose_name='创建人', null=True, blank=True)
    price = models.CharField(verbose_name='价格', max_length=128, null=True, blank=True)
    original_price = models.CharField(verbose_name='原价格', max_length=128, null=True, blank=True)
    overdue_date = models.DateField(verbose_name="过期时间", null=True, blank=True)
    isSuccess = models.IntegerField(verbose_name='是否成功', default=0)
    status_choices = (
        (1, '微信支付'),
        (2, '余额支付')
    )
    status = models.SmallIntegerField(verbose_name='支付方式', choices=status_choices, default=1)


# 提现日志
class withdrawal_log(models.Model):
    user = models.ForeignKey('Userprofile', verbose_name='提现人')
    withdrawal_befor = models.CharField(verbose_name='提现前余额 make_money字段', max_length=64)
    withdrawal_amount = models.CharField(verbose_name='提现钱数', max_length=64)
    withdrawal_after = models.CharField(verbose_name='提现后余额 make_money字段', max_length=64)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    is_success = models.BooleanField(verbose_name='是否提现成功', default=0)
    wechat_returns_data = models.TextField(verbose_name='微信返回数据, 相当于失败信息', null=True)
    dingdanhao = models.CharField(verbose_name='订单号', max_length=256, null=True)

# 记录充值人充值钱数 和 给父级钱数  # 充值分销的钱记录
class distribute_money_log(models.Model):
    user = models.ForeignKey('Userprofile', verbose_name='充值人')
    inviter = models.ForeignKey('Userprofile', verbose_name='分销人', related_name='distribute_money_log_inviter')
    price = models.CharField(verbose_name='充值钱数', max_length=128)
    money = models.CharField(verbose_name='钱数', max_length=128)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    status_choices = (
        (1, '一级分销'),
        (2, '二级分销')
    )
    status = models.SmallIntegerField(verbose_name='分销等级', choices=status_choices, default=1)
    renewal = models.ForeignKey('renewal_log', verbose_name='有关续费(哪个续费创建的数据)', null=True)

# 记录天眼 用户 访问日志
class log_access(models.Model):
    oper_user = models.ForeignKey('Userprofile', verbose_name='访问人')
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    message = models.CharField(verbose_name='记录做了什么操作', max_length=256, null=True, blank=True)






