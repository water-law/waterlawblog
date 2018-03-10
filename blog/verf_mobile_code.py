import json
import uuid
import random

from aliyunsdk.aliyunsdkcore.client import AcsClient
from aliyunsdk.aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

from misaka.models import AliyunAccount, SmsSign, SmsTemplate, SmsMessage


def get_acs_client(aliyun_account_name):
    region = "cn-hangzhou"
    try:
        aliyun_account = AliyunAccount.objects.get(name=aliyun_account_name)
    except AliyunAccount.DoesNotExist:
        aliyun_account = None
    if aliyun_account is None:
        return
    else:
        return AcsClient(aliyun_account.app_id, aliyun_account.app_secret, region)


def send_sms(business_id, phone_number, sign_name, template_code, template_param=None):
    acs_client = get_acs_client("misaka")
    if acs_client is None:
        print("没有配置阿里云帐号")
        return
    smsRequest = SendSmsRequest.SendSmsRequest()
    smsRequest.set_TemplateCode(template_code)
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)
    smsRequest.set_OutId(business_id)
    smsRequest.set_SignName(sign_name)
    smsRequest.set_PhoneNumbers(phone_number)
    smsResponse = acs_client.do_action_with_exception(smsRequest)
    return smsResponse


def send_code(activate_code, phone_number):
    """ 验证码发送代码 """
    business_id = uuid.uuid1()
    template = SmsTemplate.objects.get(name="博客登錄身份驗證")
    sign = SmsSign.objects.get(signature="py博客")
    template_param = {
        "actiCode": activate_code
    }
    template_param = json.dumps(template_param)
    verifiy_send_code = send_sms(business_id, phone_number, sign.signature, template.template_code, template_param)
    json_send_code = json.loads(verifiy_send_code)
    api_resp_code = json_send_code['Code']
    params = {
        "phone_numbers": str(phone_number),
        "sign": sign,
        "template": template,
        "params": template_param,
        "code": api_resp_code
    }
    try:
        SmsMessage.objects.create(**params)
    except Exception:
        pass
    return api_resp_code


def generate_verification_code():
    """ 随机生成6位的验证码 """
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    vcode = random.sample(code_list, 6)  # 从list中随机获取6个元素，作为一个片断返回
    verification_code = ''.join(vcode)  # list to string
    return verification_code
