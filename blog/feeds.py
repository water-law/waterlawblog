from django.contrib.syndication.views import Feed
from .models import Post


class AllPostsRssFeed(Feed):
    # 显示在聚合阅读器上的标题
    title = "WaterLaw 的博客"

    # 通过聚合阅读器跳转到网站的链接
    link = "/"

    # 显示在聚合阅读器上的描述信息
    description = "WaterLaw 的博客文章"

    # 显示在聚合器上的条目
    def items(self):
        return Post.objects.all()

    # 显示在聚合阅读器上的内容条目的标题
    def item_title(self, item):
        return '[%s] %s' % (item.category, item.title)

    # 显示在聚合阅读器上的内容条目的描述
    def item_description(self, item):
        return item.body

