from django import template
from django.db.models.aggregates import Count
from ..models import Post, Category, Tag

register = template.Library()


@register.simple_tag
def get_recent_posts(num=5):
    """ @register.simple_tag: 注册这个函数为模板标签 """
    return Post.objects.all()[:num]


@register.simple_tag
def archives():
    """
        dates 方法会返回一个列表，列表中的元素为每一篇文章（Post）的创建时间，且是
        Python 的 date 对象，精确到月份，降序排列。
    """
    return Post.objects.dates('create_time', 'month', order='DESC')


@register.simple_tag
def get_categories():
    """ 得到分类 """
    # annotate 方法在底层调用了数据库的数据聚合函数
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_tags():
    """ 得到标签 """
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_all_categories():
    return Category.objects.all()


@register.simple_tag
def get_all_tags():
    return Tag.objects.all()
