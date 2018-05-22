import os
import markdown
import re
import logging
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import HttpResponse, StreamingHttpResponse
from django.conf import settings
from django.core.mail import send_mail
from .models import Post, Category, Tag, User
from .forms import RegisterForm, CommentForm, PublishForm
from .verf_mobile_code import send_code, generate_verification_code
from .verf_image_code import get_random_code, generate_random_code


logger = logging.getLogger(__name__)


def test(request):
    """ 跳转到关于网站的页面 """
    return render(request, 'test.html')


class IndexView(ListView):
    """ 首页 """
    model = Post
    template_name = 'index.html'
    context_object_name = 'post_list'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated():
            qs = Post.objects.filter(author__username='Misaka')
        else:
            qs = Post.objects.filter(author=user)
        return qs

    def get_context_data(self, **kwargs):
        """
        在视图函数中将模板变量传递给模板是通过给 render 函数的 context 参数传递一个字典实现的，
        例如 render(request, 'blog/index.html', context={'post_list': post_list})，
        这里传递了一个 {'post_list': post_list} 字典给模板。
        在类视图中，这个需要传递的模板变量字典是通过 get_context_data 获得的，
        所以我们复写该方法，以便我们能够自己再插入一些我们自定义的模板变量进去。
        """

        # 首先获得父类生成的传递给模板的字典。
        context = super().get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 关于什么是 Paginator，Page 类在 Django Pagination 简单分页：http://zmrenwu.com/post/34/ 中已有详细说明。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        # 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
        # 注意此时 context 字典中已有了显示分页导航条所需的数据。
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，则无需显示分页导航条，不用任何分页导航条的数据，因此返回一个空的字典
            return {}

        # 当前页左边连续的页码号，初始值为空
        left = []

        # 当前页右边连续的页码号，初始值为空
        right = []

        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False

        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
            # 此时只要获取当前页右边的连续页码号，
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]。
            # 注意这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 2]

            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示。
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号，
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


def sign_in(request):
    """ 登录操作 """
    return redirect('/')


def about(request):
    """ 跳转到关于网站的页面 """
    return render(request, 'about.html')


def app(request):
    """ 下载 """
    path = os.path.dirname(__file__)

    def file_iterator(file, chunk_size=1024):
        with open(file) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield
                else:
                    break
    file_name = os.path.join(path, "static/app/" + "app.apk")
    response = StreamingHttpResponse(file_iterator(file_name))
    # 保存到硬盘时不会乱码
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
    return response


def register_vmobile(request):
    """ 注册时发送验证码操作 """
    if request.method == 'GET':
        return HttpResponse("failed")

    phone_number = request.POST.get('phone_number')

    # 清除旧的验证码
    if phone_number in request.session:
        request.session.delete(phone_number)

    """
    activate_code 为 6 位数字随机验证码, send_code_status 为阿里云 SDK 
    生成验证码的状态信息， 为 'OK' 时表示验证码生成成功.
    """
    activate_code = generate_verification_code()
    send_code_status = send_code(activate_code, phone_number)
    if send_code_status != 'OK':
        return HttpResponse("failed")

    # 将验证码存在 session 中， 格式<手机号， 验证码>
    request.session[phone_number] = activate_code
    # 设置会话过期时间
    request.session.set_expiry(10 * 60)
    return HttpResponse("success")


def register_next(request):
    """ 验证手机验证码是否正确 """

    ctx = {}
    if request.method == 'GET':
        return render(request, 'users/register.html')

    ctx['message'] = "手机号有误，请重新验证"
    phone_number = request.POST.get('phone_number')
    vmobile_code = request.POST.get('vmobile_code')

    # 没有填写手机号或验证码已过期
    if phone_number not in request.session:
        render(request, 'users/register.html', ctx)

    ctx['message'] = "验证码输入不正确"
    activate_code = request.session.get(phone_number)

    # 验证码输入不正确
    if vmobile_code != activate_code:
        render(request, 'users/register.html', ctx)

    # 将手机号存在 session 中， 格式<‘phone_number’， 手机号>
    request.session['phone_number'] = phone_number
    request.session.set_expiry(10 * 60)
    ctx['message'] = "验证成功"
    ctx['step'] = 2  # 当前注册进度为 2
    return render(request, 'users/register.html', ctx)


def register(request):

    """ 注册帐号 采用两步认证的方法 """
    if request.method == 'GET':
        return render(request, 'users/register.html')

    # 当前注册进度为 2, 默认进度为 None
    ctx = {'step': 2}

    if request.method == 'POST':
        phone_number = request.session.get('phone_number')
        if phone_number is None:
            ctx['message'] = "会话已过期，请重新验证手机"
            return render(request, 'users/register.html', ctx)
        if not re.findall(r"1[34578]\d{9}", phone_number):
            ctx['message'] = "手机号有误， 请重新验证"
            return render(request, 'users/register.html', ctx)

        form = RegisterForm(request.POST)
        if not form.is_valid():
            ctx['message'] = form.errors
            return render(request, 'users/register.html', ctx)

        # 创建实例，需要做些数据处理，暂不做保存
        new_user = form.save(commit=False)
        new_user.phone_number = phone_number
        new_user.save()
        del request.session['phone_number']
        ctx['message'] = "注册成功"
        ctx['step'] = 3
        return render(request, "users/register.html", ctx)

    return render(request, "users/register.html", ctx)


def publish(request):
    """ 发布文章 """

    """ 写博客的页面 """
    if request.method == 'GET':
        return render(request, "publish.html")

    author = request.user
    # 未登录
    if not author.is_authenticated:
        return render(request, "publish.html", {"err": "未登录"})

    # FIXME: ModelForm 多对多表单验证与多对一验证
    form = PublishForm(request.POST)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = author
        form.save()
        redirect_url = "/articles/" + str(new_post.id)
        return HttpResponseRedirect(redirect_url)
    else:
        return render(request, "publish.html", form.errors)


def article_update(request, pk):
    """ 发布文章 """
    post = get_object_or_404(Post, pk=pk)
    """ 写博客的页面 """
    if request.method == 'GET':
        return render(request, "publish_update.html", {"post": post})

    author = request.user
    # 未登录
    if author != post.author:
        return render(request, "publish_detail.html", {"err": "未登录"})
    # FIXME: ModelForm 多对多表单验证与多对一验证
    form = PublishForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        redirect_url = "/articles/" + str(pk)
        return HttpResponseRedirect(redirect_url)
    else:
        return render(request, "publish_detail.html", form.errors)


class PostDetailView(DetailView):
    """ 发布文章后跳转到发布后的文章页面 """
    model = Post
    template_name = 'publish_detail.html'
    context_object_name = 'post'

    # 获取文章时 阅读数量加 1
    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        # 获取文章内容
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
        # 将文本转为 markdown 语法的 html
        post.body = md.convert(post.body)
        # 生成目录
        post.toc = md.toc
        return post

    # 获取其他的 context 数据
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        comment_list = self.object.comment_set.all()
        context.update({'comment_list': comment_list})
        return context


def comment(request, pk):
    """ 评论文章页面 """
    post = get_object_or_404(Post, pk=pk)

    if not request.POST:
        return redirect(post)
    user = request.user
    # 没有登录或输入验证码
    if not user.is_authenticated:  # and 'visitor' not in request.session
        return redirect(post)

    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.post = post
        new_comment.tourist = user
        new_comment.save()

        content = form.data.get("content")
        to_users = re.findall(r'@(\w+)*', content)
        title = "{username}在 Water Law 社区@了你".format(username=user.username)
        msg = "{title}：{content}, {link}".format(
            title=post.title,
            content=content,
            link="{}/articles/{}".format(request.get_host(), pk))
        for to_user in to_users:
            try:
                to_user = User.objects.get(username=to_user)
                to_email = to_user.email
                if to_email:
                    send_mail(title, msg, settings.EMAIL_FROM, [to_email])
            except User.DoesNotExist:
                logger.info("@的用户不存在")
            except Exception as e:
                logger.error("发送回复提醒失败，{}".format(str(e)))

    return redirect(post)


def captcha_image(request):
    """ 验证码图片 """
    image_path = get_image_path(request)

    # 随机生成4位的验证码图片
    random_code = generate_random_code()
    get_random_code(random_code, image_path)

    # 将验证码存在 session 中, 过期时间设置为 1 分钟, 格式为<Host, Code>
    request.session['image_name'] = random_code
    request.session.set_expiry(60)
    image_data = open(image_path, "rb").read()
    return HttpResponse(image_data, content_type="image/png")


def verf_image_code(request):
    """ 验证游客的验证码是否正确 """
    if not request.POST:
        return HttpResponse("4")

    input_code = request.POST['image_code']
    random_code = request.session['image_name']

    if not random_code:
        return HttpResponse("3")

    if input_code.lower() != random_code.lower():
        return HttpResponse("2")

    # 验证码没有过期且正确
    request.session['visitor'] = request.get_host()
    request.session.set_expiry(60 * 60 * 60)
    image_path = get_image_path(request)
    # 删除验证码图片
    if os.path.exists(image_path):
        os.remove(image_path)
    return HttpResponse("1")


class ArchivesView(ListView):
    """ 按月归档文章 """
    model = Post
    template_name = 'index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        user = self.request.user
        if not user.is_authenticated():
            return Post.objects.none()
        return super(ArchivesView, self).get_queryset().filter(create_time__year=year, create_time__month=month, author=user)


class CategoryView(ListView):
    """ 按分类归档文章 """
    model = Post
    template_name = 'index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated():
            return Post.objects.none()
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=category, author=user)


class TagView(ListView):
    """ 按标签归档文章 """
    model = Post
    template_name = 'index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated():
            return Post.objects.none()
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag, author=user)


def get_image_path(request):
    """ 取得验证码图片的位置 """
    path = os.path.dirname(os.path.dirname(__file__))
    image_path = os.path.join(path, "code-img/" + request.get_host() + ".png")
    return image_path
