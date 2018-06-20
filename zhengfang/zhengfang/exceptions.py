# coding: utf8


class ZhengFangException(Exception):
    def __init__(self, message):
        self.message = message


class RequestException(ZhengFangException):
    pass

class LoginException(ZhengFangException):
    pass

class GradeException(ZhengFangException):
    pass

class EvaluateException(ZhengFangException):
    pass