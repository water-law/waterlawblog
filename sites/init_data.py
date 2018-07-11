from misaka.models import AliyunAccount, SmsSign, SmsTemplate, SmsMessage


def start():
    AliyunAccount.objects.update_or_create(name="misaka", app_id="LTAIbWS06lESOVuU", app_secret="Ovf1ab50lMdEDMNVyvSdzsu2TkIkJ5")
    SmsSign.objects.update_or_create(signature="py博客", price=0.045)
    SmsTemplate.objects.update_or_create(name="博客登錄身份驗證", template_code="SMS_87935002", price=0.045,
                               params={"actiCode": ""}, content="绑定的验证码是 ${actiCode}, 10 分钟內有效。")


if __name__ == '__main__':
    start()