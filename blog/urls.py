from django.conf.urls import url, include
from . import views
from .feeds import AllPostsRssFeed

# app_name = 'sites'
urlpatterns = [

    # 主页面
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^test$', views.test, name="test"),
    # 关于页面
    url(r'^about$', views.about, name="about"),
    # 下载 app
    url(r'^app$', views.app),

    # 注册操作
    url(r'^accounts/register/vmobile$', views.register_vmobile),
    url(r'^accounts/register/next$', views.register_next),
    url(r'^accounts/register$', views.register, name="register"),
    # 登录操作
    url(r'^accounts/profile', views.sign_in),

    # 将 auth 应用中的 urls 模块包含进来
    url(r'^users/', include('django.contrib.auth.urls')),
    # publish
    # 发表文章
    url(r'^articles/publish$', views.publish, name="publish"),
    # 文章页面
    url(r'^articles/(?P<pk>\d+)$', views.PostDetailView.as_view(), name="detail"),
    # 修改文章
    url(r'^articles/(?P<pk>\d+)/update$', views.article_update, name="update"),
    # 评论
    url(r'^comments/publish/(?P<pk>\d+)$', views.comment),

    # 评论前的验证
    url(r'^comments/verify$', views.verf_image_code),

    # 返回验证码图片
    url(r'^passports/captcha$', views.captcha_image),


    # 按月归档
    url(r'^archives/(?P<year>\d{4})/(?P<month>\d{1,2})$', views.ArchivesView.as_view(), name="archives"),
    # 分类
    url(r'^categories/(?P<pk>\d+)$', views.CategoryView.as_view(), name="category"),
    # 按标签归档文章
    url(r'^tags/(?P<pk>\d+)$', views.TagView.as_view(), name="tag"),

    url(r'^all/rss/$', AllPostsRssFeed(), name='rss'),
]