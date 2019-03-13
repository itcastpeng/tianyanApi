from django.db import models


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
    )

    qr_code = models.CharField(verbose_name="微信二维码", max_length=256, null=True, blank=True)

    openid = models.CharField(verbose_name="微信公众号openid", max_length=64)

    vip_type_choices = (
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
        max_length=128
    )
    openid = models.CharField(verbose_name="openid", max_length=64)
    subscribe = models.BooleanField(verbose_name="是否关注公众号", default=False)


# 客户信息备注 对应 用户
class customer_information_the_user(models.Model):
    user = models.ForeignKey(to='Userprofile', verbose_name='用户', null=True, blank=True)
    customer = models.ForeignKey(to='Customer', verbose_name='客户', null=True, blank=True)
    remote_type_choices = (
        (1, "跟进状态"),
        (2, "产品购买"),
        (3, "课程活动"),
    )
    remote_type = models.SmallIntegerField(verbose_name="备注类型", choices=remote_type_choices, default=1)

    remote = models.TextField(verbose_name="记录信息，存json格式", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 用户备注客户信息  所有信息 性别等。。。。
class user_comments_customer_information(models.Model):
    customer = models.ForeignKey('Customer', verbose_name="客户")
    user = models.ForeignKey(to='Userprofile', verbose_name='用户', null=True, blank=True)
    customer_info = models.TextField(verbose_name='客户信息', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 客户查看文章日志表
class SelectArticleLog(models.Model):
    customer = models.ForeignKey('Customer', verbose_name="查看人")
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

# 客户点赞文章日志表
class SelectClickArticleLog(models.Model):
    customer = models.ForeignKey('Customer', verbose_name="查看人")
    article = models.ForeignKey('Article', verbose_name="点赞文章")
    is_click = models.BooleanField(verbose_name='是否点赞', default=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 用户分享文章表
class users_forward_articles(models.Model):
    user = models.ForeignKey('Userprofile', verbose_name='分享文章的用户')
    article = models.ForeignKey('Article', verbose_name='分享的文章')
    article_url = models.TextField(verbose_name='文章链接')

# 团队表
class Team(models.Model):
    name = models.CharField(verbose_name="团队名称", max_length=128)
    create_user = models.ForeignKey('Userprofile', verbose_name="创建人", related_name="team_create_user")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


# 分类表
class Classify(models.Model):
    name = models.CharField(verbose_name="分类名称", max_length=128)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey(
        'Userprofile',
        verbose_name='创建用户',
        related_name="classify_create_user",
        null=True,
        blank=True
    )  # 该字段为空，表示为默认(推荐)分类，不为空表示品牌分类

# 用户分享的文章
class user_share_article(models.Model):
    share_user = models.ForeignKey('Userprofile', verbose_name='分享的用户',
        related_name="user_share_article_share_user", null=True)
    share_article = models.ForeignKey('Article', verbose_name='分享的文章')
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

# 文章管理
class Article(models.Model):
    title = models.CharField(verbose_name="文章标题", max_length=256)
    content = models.TextField(verbose_name="文章内容")
    classify = models.ForeignKey('Classify', verbose_name='所属分类', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    create_user = models.ForeignKey('Userprofile', verbose_name='创建用户', related_name="article_create_user")
    source_link = models.CharField(verbose_name="微信文章链接", max_length=256, null=True, blank=True)
    look_num = models.IntegerField(verbose_name="查看次数", default=0)
    like_num = models.IntegerField(verbose_name="点赞(喜欢)次数", default=0)
    cover_img = models.CharField(verbose_name='封面图', max_length=256, null=True, blank=True)


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


# 续费管理
class renewal_management(models.Model):
    price = models.CharField(verbose_name='价格', max_length=128, null=True, blank=True)
    original_price = models.CharField(verbose_name='原价格', max_length=128, null=True, blank=True)
    the_length_choices = (
        (1, '一个月'),
        (2, '半年'),
        (3, '一年'),
        (4, '两年'),
    )
    the_length = models.SmallIntegerField(verbose_name='时长', choices=the_length_choices, default=1)
    renewal_number_days = models.IntegerField(verbose_name='续费天数', default=30)
    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    create_user = models.ForeignKey('Userprofile', verbose_name='创建人', null=True, blank=True)


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
