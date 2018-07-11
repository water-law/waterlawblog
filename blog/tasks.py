from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task


@shared_task
def send_at_somebody(title, to_email, msg):
    """
    title: 邮件标题
    msg: 文字信息
    to_email: 目标邮件地址， 为 list
    """
    try:
        send_mail(title,
                  msg,
                  settings.EMAIL_FROM,
                  to_email)
    except Exception as e:
        print(str(e))
