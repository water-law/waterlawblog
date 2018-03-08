from django.db import models
from blog.models import User, Post


class Comment(models.Model):
    """ 评论 """
    tourist = models.ForeignKey(User, verbose_name="评论人")
    content = models.TextField(verbose_name="评论内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    post = models.ForeignKey(Post, verbose_name="评论的文章")

    class Meta:
        ordering = ['-create_time']

    def __str__(self):
        return "评论<评论者:{}>".format(self.content[:20])
