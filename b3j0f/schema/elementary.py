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

"""Elementary schema package."""

__all__ = [
    'NoneSchema',
    'IntegerSchema', 'FloatSchema', 'ComplexSchema', 'LongSchema',
    'StringSchema',
    'ArraySchema',
    'DictSchema',
    'BooleanSchema',
    'EnumSchema',
    'DateTimeSchema'
]

from six import string_types

from numbers import Number

from enum import Enum

from types import FunctionType, MethodType, LambdaType, NoneType

from datetime import datetime

from inspect import getargspec

from .base import Schema, RefSchema, This
from .utils import DynamicValue


class ElementarySchema(Schema):
    """Base elementary schema."""

    nullable = False


class NoneSchema(ElementarySchema):
    """None schema."""

    __data_types__ = [NoneType]
    nullable = True


class BooleanSchema(ElementarySchema):
    """Boolean schema."""

    __data_types__ = [bool]
    default = False


class NumberSchema(ElementarySchema):
    """Schema for number such as float, long, complex and float.

    If allows to bound data values."""

    __data_types__ = [Number]

    #: minimum allowed value if not None.
    min = This(nullable=True, default=None)
    #: maximal allowed value if not None.
    max = This(nullable=True, default=None)

    def _validate(self, data, *args, **kwargs):

        ElementarySchema._validate(self, data, *args, **kwargs)

        if self.min is not None and self.min > data:
            raise ValueError(
                'Data {0} must be greater or equal than {1}'.format(
                    data, self.min
                )
            )

        if self.max is not None and self.max < data:
            raise ValueError(
                'Data {0} must be lesser or equal than {1}'.format(
                    data, self.max
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


class FloatSchema(NumberSchema):
    """Float Schema."""

    __data_types__ = [float]
    default = 0.


class StringSchema(ElementarySchema):
    """String Schema."""

    __data_types__ = [string_types]
    default = ''


class TypeSchema(ElementarySchema):
    """Type schema."""

    __data_types__ = [type]
    default = object


class ArraySchema(ElementarySchema):
    """Array Schema."""

    __data_types__ = [list, tuple, set]

    #: item types. Default any.
    itemtype = TypeSchema(nullable=True, default=None)
    #: minimal array size. Default None.
    minsize = IntegerSchema(nullable=True, default=None)
    #: maximal array size. Default None.
    maxsize = IntegerSchema(nullable=True, default=None)
    unique = False  #: are items unique ? False by default.
    default = DynamicValue(lambda: [])

    def _validate(self, data, *args, **kwargs):

        ElementarySchema._validate(self, data, *args, **kwargs)

        if self.minsize is not None and self.minsize > len(data):
            raise ValueError(
                'length of data {0} must be greater than {1}.'.format(
                    data, self.minsize
                )
            )

        if self.maxsize is not None and len(data) > self.maxsize:
            raise ValueError(
                'length of data {0} must be lesser than {1}.'.format(
                    data, self.maxsize
                )
            )

        if data:
            if self.unique and len(set(data)) != len(data):
                raise ValueError('Duplicated items in {0}'.format(result))

            if self.itemtype is not None:
                for index, item in enumerate(data):
                    if not isinstance(item, self.itemtype):
                        raise TypeError(
                            'Wrong type of {0} at pos {1}. {2} expected.'.format(
                                item, index, self.itemtype
                            )
                        )


class DictSchema(ArraySchema):
    """Array Schema."""

    __data_types__ = [dict]

    #: value type
    valuetype = TypeSchema(nullable=True, default=None)
    default = DynamicValue(lambda: {})

    def _validate(self, data, *args, **kwargs):

        super(DictSchema, self)._validate(data, *args, **kwargs)

        if data:
            if self.unique and len(set(data.values())) != len(data):
                raise ValueError('Duplicated items in {0}'.format(result))

            if self.valuetype is not None:
                for key, item in data.items():
                    if not isinstance(item, self.valuetype):
                        raise TypeError(
                            'Wrong type of {0} at pos {1}. {2} expected.'.format(
                                item, key, self.valuetype
                            )
                        )


class EnumSchema(ElementarySchema):
    """Enumerable schema."""

    __data_types__ = [Enum]


class DateTimeSchema(ElementarySchema):
    """Date time schema."""

    __data_types__ = [datetime]

    ms = IntegerSchema(nullable=True, default=None)
    s = IntegerSchema(nullable=True, default=None)
    mn = IntegerSchema(nullable=True, default=None)
    hr = IntegerSchema(nullable=True, default=None)
    day = IntegerSchema(nullable=True, default=None)
    month = IntegerSchema(nullable=True, default=None)
    year = IntegerSchema(nullable=True, default=None)

    default = DynamicValue(lambda: datetime.now())
