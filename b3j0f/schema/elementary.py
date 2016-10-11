# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

from six import string_types, add_metaclass, PY3

from numbers import Number

from enum import Enum

from datetime import datetime

from .registry import registercls
from .utils import (
    DynamicValue, RegisteredSchema, ThisSchema, MetaRegisteredSchema
)

__all__ = [
    'NumberSchema',
    'IntegerSchema', 'FloatSchema', 'ComplexSchema', 'LongSchema',
    'StringSchema',
    'ArraySchema',
    'DictSchema',
    'BooleanSchema',
    'EnumSchema',
    'DateTimeSchema',
    'OneOfSchema'
]

NoneType = type(None)


class MetaElementarySchema(MetaRegisteredSchema):
    """Automatically register schemas with data types."""

    def __new__(mcs, *args, **kwargs):

        result = super(MetaElementarySchema, mcs).__new__(mcs, *args, **kwargs)

        if result.__data_types__:
            registercls(data_types=result.__data_types__, schemacls=result)

        return result


@add_metaclass(MetaElementarySchema)
class ElementarySchema(RegisteredSchema):
    """Base elementary schema."""

    __register__ = False

    nullable = False

    #: data types which can be instanciated by this schema.
    __data_types__ = []

    def _validate(self, data, owner=None, *args, **kwargs):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :param Schema owner: schema owner.
        :raises: Exception if the data is not validated.
        """
        if isinstance(data, DynamicValue):
            data = data()

        if data is None and not self.nullable:
            raise TypeError('Value can not be null')

        elif data is not None:
            # data must inherits from this data_types
            if not isinstance(data, tuple(self.__data_types__)):
                raise TypeError(
                    'Wrong data value: {0}. {1} expected.'.format(
                        data, self.__data_types__
                    )
                )


class BooleanSchema(ElementarySchema):
    """Boolean schema."""

    __data_types__ = [bool]
    default = False


class NumberSchema(ElementarySchema):
    """Schema for number such as float, long, complex and float.

    If allows to bound data values.
    """

    __data_types__ = [Number]
    default = 0

    #: minimum allowed value if not None.
    min = ThisSchema(nullable=True, default=None)
    #: maximal allowed value if not None.
    max = ThisSchema(nullable=True, default=None)

    def _validate(self, data, *args, **kwargs):

        ElementarySchema._validate(self, data, *args, **kwargs)

        if data is None:
            return

        selfmin = self.min
        if isinstance(selfmin, ThisSchema):
            selfmin = None

        if selfmin is not None and selfmin > data:
            raise ValueError(
                'Data {0} must be greater or equal than {1}'.format(
                    data, selfmin
                )
            )

        selfmax = self.max
        if isinstance(selfmax, ThisSchema):
            selfmax = None

        if selfmax is not None and selfmax < data:
            raise ValueError(
                'Data {0} must be lesser or equal than {1}'.format(
                    data, self.max
                )
            )


class LongSchema(NumberSchema):
    """Long Schema."""

    __data_types__ = [int] if PY3 else [long]
    default = 0 if PY3 else long(0)


class IntegerSchema(NumberSchema):
    """Integer Schema."""

    __data_types__ = [int]
    default = 0


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

        if data is None:
            return

        selfminsize = self.minsize
        if isinstance(selfminsize, ThisSchema):
            selfminsize = None

        if selfminsize is not None and selfminsize > len(data):
            raise ValueError(
                'length of data {0} must be greater than {1}.'.format(
                    data, self.minsize
                )
            )

        selfmaxsize = self.maxsize
        if isinstance(selfmaxsize, ThisSchema):
            selfmaxsize = None

        if selfmaxsize is not None and len(data) > selfmaxsize:
            raise ValueError(
                'length of data {0} must be lesser than {1}.'.format(
                    data, self.maxsize
                )
            )

        if data:
            if self.unique and len(set(data)) != len(data):
                raise ValueError('Duplicated items in {0}'.format(data))

            if self.itemtype is not None:
                for index, item in enumerate(data):
                    if not isinstance(item, self.itemtype):
                        raise TypeError(
                            'Wrong type of {0} at {1}. {2} expected.'.format(
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
                raise ValueError('Duplicated items in {0}'.format(data))

            if self.valuetype is not None:
                for key, item in data.items():
                    if not isinstance(item, self.valuetype):
                        raise TypeError(
                            'Wrong type of {0} at {1}. {2} expected.'.format(
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


class OneOfSchema(ElementarySchema):
    """Validate one of input types."""

    itemtype = TypeSchema(type)
