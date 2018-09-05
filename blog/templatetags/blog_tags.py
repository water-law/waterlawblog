from django import template
from django.db.models.aggregates import Count
from ..models import Post, Category, Tag, User

register = template.Library()


@register.simple_tag
def get_recent_posts(num=5):
    """ @register.simple_tag: 注册这个函数为模板标签 """
    return Post.objects.all()[:num]


@register.simple_tag
def archives(username=None):
    """
        dates 方法会返回一个列表，列表中的元素为每一篇文章（Post）的创建时间，且是
        Python 的 date 对象，精确到月份，降序排列。
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Post.objects.none()
    return Post.objects.filter(author=user).dates('create_time', 'month', order='DESC')


@register.simple_tag
def get_categories(username=None):
    """ 得到分类 """
    # annotate 方法在底层调用了数据库的数据聚合函数
    qs = []
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Category.objects.none()
    categories = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    for category in categories:
        if Post.objects.filter(category=category, author=user).exists():
            qs.append(category)
    return qs


@register.simple_tag
def get_tags(username=None):
    """ 得到标签 """
    qs = []
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Tag.objects.none()
    tags = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    for tag in tags:
        if Post.objects.filter(tags=tag, author=user).exists():
            qs.append(tag)
    return qs


@register.simple_tag
def get_all_categories():
    return Category.objects.all()


@register.simple_tag
def get_all_tags():
    return Tag.objects.all()
