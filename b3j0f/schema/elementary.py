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
    'IntegerSchema', 'FloatSchema', 'ComplexSchema', 'LongSchema',
    'StringSchema',
    'ArraySchema',
    'BooleanSchema',
    'EnumSchema',
    'FunctionSchema'
]

from six import string_types, add_metaclass

from numbers import Number

from enum import Enum

from types import FunctionType, MethodType, LambdaType

from sys import maxsize

from datetime import datetime

from .base import Schema, MetaSchema, DynamicValue
from .registry import register


class ElementarySchema(Schema):

    nullable = False

    def validate(self, data, *args, **kwargs):

        if not isinstance(data, tuple(self.__data_types__)):
            raise TypeError(
                'Wrong data value: {0}. {1} expected.'.format(
                    data, self.__data_types__
                )
            )


class NumberSchema(ElementarySchema):

    min = -maxsize
    max = maxsize

    def validate(self, data, *args, **kwargs):

        super(NumberSchema, self).validate(data, *args, **kwargs)

        if self.min > data or data > self.max:
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
    default = ''


class BooleanSchema(ElementarySchema):
    """Boolean schema."""

    __data_types__ = [bool]
    default = False


class ArraySchema(ElementarySchema):
    """Array Schema."""

    __data_types__ = [list, tuple, set]
    item_types = object  #: item types. Default any.
    minsize = 0  #: minimal array size. Default 0.
    maxsize = maxsize  # maximal array size. Default sys.maxsize
    unique = False  #: are items unique ? False by default.
    default = DynamicValue(lambda: [])

    def validate(self, data, *args, **kwargs):

        super(ArraySchema, self).validate(data, *args, **kwargs)

        if self.minsize >= len(data) or len(data) >= self.maxsize:
            raise ValueError(
                'length of data {0} must be in [{1}; {2}]'.format(
                    data, self.minsize, self.maxsize
                )
            )

        if data:
            if self.unique and len(set(data)) != len(data):
                raise ValueError('Duplicated items in {0}'.format(result))

            for index, item in enumerate(data):
                if not isinstance(item, item_types):
                    raise TypeError(
                        'Wrong type of {0} at pos {1}. {2} expected.'.format(
                            item, index, item_types
                        )
                    )


class EnumSchema(ElementarySchema):
    """Enumerable schema."""

    __data_types__ = [Enum]


class DateTimeSchema(ElementarySchema):

    __data_types__ = [datetime]
    default = DynamicValue(lambda: datetime.now())


class FunctionSchema(ElementarySchema):

    __data_types__ = [FunctionType, MethodType, LambdaType]
