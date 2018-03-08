# -*- coding:utf-8 -*-
import enum


class EnumWithDescription(enum.Enum):
    def __init__(self, code, description):
        self.code, self.description = code, description

    @property
    def str_code(self):
        return str(self.code)

    @classmethod
    def all(cls):
        return [(e.code, e.description) for e in cls]

    @classmethod
    def from_code(cls, code):
        for obj in cls:
            if obj.code == code:
                return obj
        return None

    @classmethod
    def from_name(cls, name):
        for obj in cls:
            if obj.name.lower() == name.lower():
                return obj
        return None

    @classmethod
    def from_description(cls, description, fuzzy=False):
        for obj in cls:
            if fuzzy and description in obj.description:
                return obj
            if obj.description == description:
                return obj
        return None
