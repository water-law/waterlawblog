目前实现的功能：
1. 导航条
2. 注册与登录
2. 写博客
3. 显示文章摘要
4. 增加 markdown 语法支持
5. 简单提交评论
6. 自定义模板（首页中右侧的 最近文章，归档，分类， 在用标签）

尚未实现的功能：
1. 权限认证
2. markdown 编辑器的页面太丑了
3. 表单校验
4. 图片验证码

[nginx 部署]
在 /etc/nginx/conf.d
sudo ln -s /home/zjp/waterlawblog/soya/conf/nginx/blog_187.conf /etc/nginx/conf.d/blog_187.conf