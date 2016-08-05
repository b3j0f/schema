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

__all__ = ['NumberSchema', 'StringSchema', 'ArraySchema', 'BooleanSchema']

from six import string_types

from numbers import Number

from enum import Enum

from types import FunctionType

from sys import maxsize

from six import add_metaclass

from .base import Schema, MetaSchema
from .prop import Property


class MetaElementarySchema(MetaSchema):

    _SCHEMAS_BY_DATA_TYPE = {}

    def __call__(mcs, *args, **kwargs):

        result = super(MetaElementarySchema, mcs).__call__(*args, **kwargs)

        _SCHEMAS_BY_DATA_TYPE[mcs.data_type] = mcs
        mcs.data_type = result.data_type
        mcs.subclass

        return result

    def __instancecheck__(self, instance):

        if isinstance(instance, tuple):
            instance = tuple(list(instance) + [self.data_type])

        return super(MetaElementarySchema, self).__instancecheck__(instance)

    def __subclasscheck__(self, subclass):

        if isinstance(subclass, tuple):
            subclass = tuple(list(subclass) + [self.data_type])

        return super(MetaElementarySchema, self).__subclasscheck__(
            (other, self.data_type)
        )


def getelementaryschema(data):
    """Get the right Elementary schema."""

    return MetaElementarySchema._SCHEMAS_BY_DATA_ID[type(data)]


@add_metaclass(MetaElementarySchema)
class ElementarySchema(Schema):

    data_type = object

    def __call__(self, val=None):

        if val is None:
            if self.default is None:
                args = []

            else:
                args = [self.default]

        else:
            args = [self.val]

        return self.data_type(*args)

    def validate(self, data):

        if not isinstance(data, self.data_type):
            raise TypeError(
                'Wrong type {0}. {1} expected'.format(data, self.data_type)
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


class IntegerSchema(ElementarySchema):
    """Integer Schema."""

    data_type = int
    default = 0


class FloatSchema(ElementarySchema):
    """Float Schema."""

    data_type = float
    default = 0.


class StringSchema(Schema, string_types):
    """String Schema."""

    data_type = string_types


class ArraySchema(Schema, Iterable):
    """Array Schema."""

    data_type = list
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


class EnumSchema(Schema, Enum):
    """Enumerable schema."""

    data_type = Enum


class BooleanSchema(Schema):
    """Boolean schema."""

    data_type = bool
    default = False


class FunctionSchema(Schema):
    """Function schema."""

    data_type = FunctionType

    def __call__(self, code, globals, name=None, argdefs=None, closure=None):

        return FunctionType(code, globals, name, argdefs, closure)
