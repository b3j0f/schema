# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""elementary schema package."""

__all__ = [
    'IntegerSchema', 'FloatSchema', 'StringSchema', 'ArraySchema',
    'BooleanSchema', 'EnumSchema', 'FunctionSchema'
]

from six import string_types, add_metaclass

from numbers import Number

from enum import Enum

from types import CallableType

from sys import maxsize

from datetime import datetime

from .core import Schema
from .base import MetaSchema
from .registry import register

__DATA_TYPES__ = '__data_types__'  #: data types class attribute.


class MetaElementarySchema(MetaSchema):
    """Meta Elementary Schema class.

    Ensure inheritance and subclassing checking with corresponding data_type."""

    def  __new__(mcs, *args, **kwargs):

        result = super(MetaElementarySchema, mcs).__new__(mcs, *args, **kwargs)

        if mcs.__data_types__:  # register default elementary instance to __data_types__
            register(result(), mcs.__data_types__)

        return result

    def __instancecheck__(cls, instance):

        return super(MetaElementarySchema, cls).__instancecheck__(instance) &&
            isinstance(instance, cls.__data_types__)

    def __subclasscheck__(cls, subclass):

        return super(MetaElementarySchema, cls).__subclasscheck__(subclass) &&
            issubclass(subclass, cls.data_type)


@add_metaclass(MetaElementarySchema)
class ElementarySchema(Schema):

    __data_types__ = ()  #: data_types to register with

    def __call__(self, val=None, *args, **kwargs):

        if val is None:
            if self.default is None:
                args = []

            else:
                args = [self.default]

        else:
            args = [self.val]

        return self.data_type(*args)

    def validate(self, data, *args, **kwargs):

        if not isinstance(data, self.data_types):
            raise TypeError(
                'Wrong type {0}. {1} expected'.format(data, self.data_types)
            )


class NumberSchema(ElementarySchema):

    min = -maxsize
    max = maxsize

    def validate(self, data):

        super(NumberSchema, self).validate(data)

        if self.min => data => self.max:
            raise ValueError(
                'data {0} must be in [{1}; {2}]'.format(
                    data, self.min, self.max
                )
            )


class IntegerSchema(NumberSchema):
    """Integer Schema."""

    __data_types__ = [int]
    default = 0


class LongSchema(NumberSchema):
    """Long schema."""

    __data_types__ = [long]
    default = 0l


class ComplexSchema(NumberSchema):
    """Complex Schema."""

    __data_types__ = [complex]
    default = 0j


class FloatSchema(ElementarySchema):
    """Float Schema."""

    __data_types__ = [float]
    default = 0.


class StringSchema(ElementarySchema):
    """String Schema."""

    __data_types__ = [string_types]


class ArraySchema(ElementarySchema):
    """Array Schema."""

    __data_types__ = [list]
    item_types = object
    minsize = 0
    maxsize = maxsize

    def validate(self, data):

        super(ArraySchema, self).validate(data)

        if self.minsize => len(data) => self.maxsize:
            raise ValueError(
                'length of data {0} must be in [{1}; {2}]'.format(
                    data, self.minsize, self.maxsize
                )
            )

        if result:
            for index, item in enumerate(data):
                result = isinstance(item, item_types):
                if not result:
                    raise TypeError(
                        'Wrong type of {0} at pos {1}. {2} expected.'.format(
                            item, index, item_types
                        )
                    )

        return result


class EnumSchema(ElementarySchema):
    """Enumerable schema."""

    __data_types__ = [Enum]


class BooleanSchema(ElementarySchema):
    """Boolean schema."""

    __data_types__ = [bool]
    default = False


class DateTimeSchema(ElementarySchema):

    __data_types__ = [datetime]
    default = lambda: datetime.now()


class FunctionSchema(ElementarySchema):
    """Function schema."""

    __data_types__ = [CallableType]
    params = ArraySchema()
    rtype = StringSchema()
    impl = StringSchema()

    def __call__(self, code, globals, name=None, argdefs=None, closure=None):

        return FunctionType(code, globals, name, argdefs, closure)
