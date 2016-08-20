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

from six import string_types

from numbers import Number

from enum import Enum

from types import FunctionType, MethodType, LambdaType

from datetime import datetime

from inspect import getargspec

from .base import Schema, RefSchema, This
from .utils import DynamicValue


class ElementarySchema(Schema):

    nullable = False


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

    def validate(self, data, *args, **kwargs):

        super(NumberSchema, self).validate(data, *args, **kwargs)

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
    item_type = TypeSchema(nullable=True, default=None)
    #: minimal array size. Default None.
    minsize = IntegerSchema(nullable=True, default=None)
    #: maximal array size. Default None
    maxsize = IntegerSchema(nullable=True, default=None)
    unique = False  #: are items unique ? False by default.
    default = DynamicValue(lambda: [])

    def validate(self, data, *args, **kwargs):

        super(ArraySchema, self).validate(data, *args, **kwargs)

        if self.minsize > len(data):
            raise ValueError(
                'length of data {0} must be greater than {1}.'.format(
                    data, self.minsize
                )
            )

        if self.maxsize is not None and len(data) >= self.maxsize:
            raise ValueError(
                'length of data {0} must be lesser than {1}.'.format(
                    data, self.maxsize
                )
            )

        if data:
            if self.unique and len(set(data)) != len(data):
                raise ValueError('Duplicated items in {0}'.format(result))

            if self.item_type is not None:
                for index, item in enumerate(data):
                    if not isinstance(item, self.item_type):
                        raise TypeError(
                            'Wrong type of {0} at pos {1}. {2} expected.'.format(
                                item, index, self.item_type
                            )
                        )


class DictSchema(ArraySchema):
    """Array Schema."""

    __data_types__ = [dict]

    #: value type
    value_type = TypeSchema(nullable=True, default=None)
    default = DynamicValue(lambda: {})

    def validate(self, data, *args, **kwargs):

        super(DictSchema, self).validate(data, *args, **kwargs)

        if self.maxsize is not None and len(data) >= self.maxsize:
            raise ValueError(
                'length of data {0} must be lesser than {1}.'.format(
                    data, self.maxsize
                )
            )

        if data:
            if self.unique and len(set(data.values())) != len(data):
                raise ValueError('Duplicated items in {0}'.format(result))

            if self.value_type is not None:
                for key, item in data.items():
                    if not isinstance(value, self.value_type):
                        raise TypeError(
                            'Wrong type of {0} at pos {1}. {2} expected.'.format(
                                item, key, self.value_type
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


class FunctionSchema(ElementarySchema):
    """Function schema.

    Dedicated to describe functions, methods and lambda objects."""

    class ParamSchema(Schema):
        """Function parameter schema."""

        type = object
        hasvalue = False

    __data_types__ = [FunctionType, MethodType, LambdaType]

    params = ArraySchema(item_type=ParamSchema)
    rtype = TypeSchema(nullable=True, default=None)
    impl = ''
    fget = This()
    fset = This()
    fdel = This()

    def validate(self, data, *args, **kwargs):

        result = super(FunctionSchema, self).validate(
            data=data, *args, **kwargs
        )

        if result:

            args, vargs, kwargs, default = getargspec(data)

            for param in self.params:
                if param.validate(args, )

            params = []

            indexlen = len(args) - (0 if default is None else len(default))

            for index, arg in enumerate(args):

                pkwargs = {name: arg}  # param kwargs
                if index == indexlen:
                    value = default[index - len(default)]
                    pkwargs['default'] = value
                    pkwargs['type'] = type(value)
                    pkwargs['hasvalue'] = True
                    indexlen += 1

                param = FunctionSchema.ParamSchema(**pkwargs)
                params.append(param)

        return result

    def _setvalue(self, schema, value, *args, **kwargs):

        if schema.name == 'default':

            self.params = FunctionSchema._getparams(value)


    @staticmethod
    def _getparams(function):
        """Get function params from input function.

        :return: list of param schema.
        :rtype: list"""

        result = []

        args, vargs, _, default = getargspec(function)

        indexlen = len(args) - (0 if default is None else len(default))

        for index, arg in enumerate(args):

            pkwargs = {name: arg}  # param kwargs

            if index >= indexlen:  # has default value
                value = default[index - indexlen]
                pkwargs['default'] = value
                pkwargs['type'] = type(value)
                pkwargs['hasvalue'] = True

            param = FunctionSchema.ParamSchema(**pkwargs)
            params.append(param)

        return result

        self.params = params
