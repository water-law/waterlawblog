from .utils import EnumWithDescription


class SignType(EnumWithDescription):
    Default = (1, "验证码或短信通知")
    Promotion = (2, "推广短信或群发助手")


class SignUse(EnumWithDescription):
    Default = (1, "签名为自己产品名／网站名")
    SignOther = (2, "签名为他人产品名／网站名")


class TemplateType(EnumWithDescription):
    Default = (1, "验证码")
    SmsNotice = (2, "短信通知")
