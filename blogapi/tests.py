from django.test import TestCase
import sys


# Create your tests here.


def test_str_cache():
    a = "hello2"
    b = "hello2"
    d = "hello2"
    print(a is b)
    print(b is d)
    c = sys.intern(a)
    print(type(c))
    print("sys.intern(a) is {}".format(c))
    print(sys.intern(a) is sys.intern(b))


test_str_cache()
