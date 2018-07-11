import os
import re
import base64
import datetime
import pytz
from django.conf.urls import url, include
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from blogapi.serializers import PhoneSerializer, RegisterSerializer, PostSerializer, \
    PublishSerializer, CommentSerializer
from blog.models import Post, Category, Tag, User
from blog.verf_mobile_code import send_code, generate_verification_code
from blog.verf_image_code import get_random_code, generate_random_code

EXPIRE_MINUTES = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES', 1)


class ObtainExpiringAuthToken(ObtainAuthToken):
    """Create user token"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])
            # offset-naive 类型
            # 保存到 django 中的时间为 settings 中的 TIME_ZONE
            time_now = datetime.datetime.now()
            time_now = time_now.replace(tzinfo=pytz.timezone(getattr(settings, 'TIME_ZONE')))
            if created or token.created < time_now - datetime.timedelta(minutes=EXPIRE_MINUTES):
                # Update the created time of the token to keep it valid
                token.delete()
                token = Token.objects.create(user=serializer.validated_data['user'])
                token.created = time_now
                token.save()

            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = (IsAuthenticatedOrReadOnly,)


class MobileCodeView(APIView):
    """ 生成验证码 """
    permission_classes = ()

    def post(self, request, format=None):
        serializer = PhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.data['phone_number']
        if not re.findall(r"1[34578]\d{9}", phone_number):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        activate_code = generate_verification_code()
        send_code_status = send_code(activate_code, phone_number)
        if send_code_status != 'OK':
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 将验证码存在 session 中， 格式<手机号， 验证码>
        request.session[phone_number] = activate_code
        # 设置会话过期时间
        request.session.set_expiry(10 * 60)
        return Response(status=status.HTTP_200_OK)


# FIXME:
class RegisterView(APIView):
    """ 注册帐号 """

    permission_classes = ()

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(username=serializer.data.get('username'))
        if user is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if serializer.data.get('password') != serializer.data.get('password1'):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User()
        user.username = serializer.data.get('username')
        user.set_password(serializer.data.get('password'))
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# FIXME:
class PublishView(APIView):
    """ 发布文章 """

    def post(self, request, format=None):
        serializer = PublishSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        category = serializer.data.get('category')
        category = Category.objects.get(pk=category)
        if category is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tags = serializer.data.get('tags')
        with transaction.atomic():
            post = Post()
            post.title = serializer.data.get('title')
            post.body = serializer.data.get('body')
            post.category = category
            post.author = request.user
            post.save()

            for tag in tags:
                tag = Tag.objects.get(pk=tag)
                post.tags.add(tag)

        return Response(status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    """ 跳转到文章页面 """

    permission_classes = ()

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        post.increase_views()
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Response(status=status.HTTP_404_NOT_FOUND)


class ArticleListCreateAPIView(ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()


class CommentView(APIView):
    """ 评论文章页面 """

    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class CaptchaImageView(APIView):
    """ 生成图片验证码 """

    permission_classes = ()

    def get(self, request, format=None):
        image_path = get_image_path(request)
        # 随机生成4位的验证码图片
        random_code = generate_random_code()
        get_random_code(random_code, image_path)

        # 将验证码存在 session 中, 过期时间设置为 1 分钟, 格式为<Host, Code>
        request.session['image_name'] = random_code
        request.session.set_expiry(60)
        image_data = open(image_path, "rb").read()
        # 图片使用 base64 必须加上 [data:image/png;base64,]
        return Response(base64.b64encode(image_data), content_type="image/png")


class ArchivesView(ListAPIView):
    """ 按月归档文章 """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = ()

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(create_time__year=year, create_time__month=month)


class CategoryView(ListAPIView):
    """ 按分类归档文章 """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = ()

    def get_queryset(self):
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=category)


class TagView(ListAPIView):
    """ 按标签归档文章 """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = ()

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


def get_image_path(request):
    """ 取得验证码图片的位置 """
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    image_path = os.path.join(path, "code-img/" + request.get_host() + ".png")
    return image_path


urlpatterns = [
    # 登陆时获取一个 token
    # url(r'^api-token-auth/', obtain_jwt_token),
    # # 如果返回的 token 与上传的一致， 表明验证成功
    # url(r'^api-token-verify/', verify_jwt_token),
    # url(r'^api-token-refresh/', refresh_jwt_token),
    # token 丢失或过期则重新登录， 登陆时获取 token, 以后每次请求都带上 token, 验证 token 的有效性
    url(r'^api-token/$', ObtainExpiringAuthToken.as_view()),
    url(r'^articles$', PostView.as_view()),
    url(r'^accounts/register/vmobile$', MobileCodeView.as_view()),
    url(r'^accounts/register$', RegisterView.as_view()),

    # # 登录操作
    # url(r'^accounts/profile', views.sign_in),
    #
    # # 将 auth 应用中的 urls 模块包含进来
    # url(r'^users/', include('django.contrib.auth.urls')),
    # # publish
    # # 发表文章
    url(r'^articles/publish$', PublishView.as_view()),
    # 文章页面
    url(r'^articles/(?P<pk>\d+)$', PostDetailView.as_view()),
    url(r'^articles/$', ArticleListCreateAPIView.as_view()),
    # # 评论
    url(r'^comments/publish/\d+$', CommentView.as_view()),
    #
    # # 评论前的验证
    # url(r'^comments/verify$', views.verf_image_code),
    #
    # 返回验证码图片
    url(r'^passports/captcha$', CaptchaImageView.as_view()),
    #
    #
    # 按月归档
    url(r'^archives/(?P<year>\d{4})/(?P<month>\d{1,2})$', ArchivesView.as_view()),
    # 分类
    url(r'^categories/(?P<pk>\d+)$', CategoryView.as_view()),
    # 按标签归档文章
    url(r'^tags/(?P<pk>\d+)$', TagView.as_view()),
]