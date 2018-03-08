from django.db import models
from django.contrib.postgres import fields
import django.utils.timezone as timezone
from sites.constant import SignType, SignUse, TemplateType


class AliyunAccount(models.Model):
    """ 阿里云配置 """
    name = models.CharField(max_length=100, verbose_name="阿里云用户名")
    app_id = models.CharField(max_length=64, editable=False, verbose_name="阿里云app_id")
    app_secret = models.CharField(max_length=64, editable=False, verbose_name="阿里云app_secret")

    def __str__(self):
        return "阿里云账户<账户别名:{}>".format(self.name)


class SmsSign(models.Model):
    signature = models.CharField(max_length=30, verbose_name="签名")
    sign_type = models.SmallIntegerField(default=SignType.Default.code, choices=SignType.all(), verbose_name="签名类型")
    price = models.FloatField(verbose_name="每条短信的价格")
    sign_use = models.SmallIntegerField(default=SignUse.Default.code, choices=SignUse.all(), verbose_name="签名用途")
    enabled = models.BooleanField(default=True, verbose_name="是否启用")

    def __str__(self):
        return "短信签名<签名:{}>".format(self.signature)


class SmsTemplate(models.Model):
    name = models.CharField(max_length=50, verbose_name="模版名称")
    template_code = models.CharField(max_length=30, verbose_name="模版CODE")
    template_type = models.SmallIntegerField(default=TemplateType.Default.code, choices=TemplateType.all(), verbose_name="模版类型")
    price = models.FloatField(verbose_name="每条短信的价格")
    params = fields.JSONField(default=dict, verbose_name="模板参数")
    content = models.TextField(verbose_name="模版内容", blank=True)
    enabled = models.BooleanField(default=True, verbose_name="是否启用")

    def __str__(self):
        return "短信模板<模板:{}>".format(self.name)


class SmsMessage(models.Model):
    phone_numbers = models.CharField(max_length=30, verbose_name="短信接收号码")
    sign = models.ForeignKey(SmsSign, verbose_name="短信签名")
    template = models.ForeignKey(SmsTemplate, verbose_name="短信模板")
    params = fields.JSONField(default=dict, verbose_name="消息参数")
    up_extend_code = models.CharField(max_length=20, verbose_name="上行短信扩展码", blank=True)
    out_id = models.CharField(max_length=30, verbose_name="外部流水扩展字段", blank=True)
    code = models.CharField(max_length=20, verbose_name="短信接口返回码")
    created = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return "短信<手机号:{}>".format(self.phone_numbers)