import markdown
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import strip_tags
import django.utils.timezone as timezone
from django.urls import reverse


class Github(models.Model):
    """ Github """
    login_name = models.CharField(max_length=30, verbose_name='Github 登录名')
    github_id = models.IntegerField(verbose_name='Github 用户ID')
    avatar_url = models.URLField(verbose_name='头像', blank=True)

    def __str__(self):
        return "Github<Github:{}>".format(self.login_name)


class User(AbstractUser):
    """ 用户 """
    phone_number = models.CharField(max_length=13, verbose_name="手机号")
    github = models.ForeignKey(Github, verbose_name='与用户关联的 Github', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "用户<用户名:{}>".format(self.username)


class Category(models.Model):
    """ 分类 """
    name = models.CharField(max_length=100, verbose_name="分类名")

    def __str__(self):
        return "分类<分类名:{}>".format(self.name)


class Tag(models.Model):
    """ 标签 """
    name = models.CharField(max_length=100, verbose_name="标签名")

    def __str__(self):
        return "标签<标签名:{}>".format(self.name)


class Post(models.Model):
    """ 文章 """
    title = models.CharField(max_length=70, verbose_name="文章标题")
    body = models.TextField(verbose_name="文章内容")
    # timezone.now 默认为当前时间并且可以修改
    create_time = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    modify_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")
    abstract = models.CharField(max_length=200, blank=True, verbose_name="文章摘要")
    views = models.PositiveIntegerField(default=0, verbose_name="浏览数量")
    category = models.ForeignKey(Category, verbose_name="分类")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="标签")
    author = models.ForeignKey(User, verbose_name="作者")

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return "文章<标题:{}>".format(self.title)

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})
    """
    自动生成文章摘要： 重写 save() 方法， 将 markdown 转为 html 文本， 
    去掉 html 标签， 然后截取前 54 个字符做摘要 
    """
    def save(self, *args, **kwargs):
        # 如果没有填写摘要
        # 实例化一个 markdown
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite'
        ])
        """
        先将 Markdown 文本渲染成 HTML 文本
        strip_tags 去掉 HTML 文本的全部 HTML 标签
        从文本摘取前 54 个字符赋给 excerpt
        """
        self.abstract = strip_tags(md.convert(self.body))[:54]
        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)