#!/usr/bin/env python
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


from unittest import main

from b3j0f.utils.ut import UTCase

from ..utils import validate

from ..elementary import (
    IntegerSchema, FloatSchema, ComplexSchema, LongSchema,
    StringSchema,
    ArraySchema,
    TypeSchema,
    DictSchema
)


class ElementaryTest(UTCase):

    __schemacls__ = None

    def _assert(self, data, error=False, **kwargs):

        if error:
            self.assertRaises(
                Exception, self.__schemacls__, default=data, **kwargs
            )

        else:
            schema = self.__schemacls__(default=data, **kwargs)
            validate(schema, data)

    def test_default(self):

        if self.__schemacls__ is None:
            return

        schema = self.__schemacls__()

        data = schema.default

        validate(schema, data=data)

    def test_none(self):

        if self.__schemacls__ is None:
            return

        schema = self.__schemacls__()

        if schema.nullable:
            validate(schema, data=None)

        else:
            self.assertRaises(TypeError, validate, schema, data=None)


class NumberSchemaTest(ElementaryTest):

    def test_min(self):

        if self.__schemacls__ is None:
            return

        self._assert(
            min=self.__schemacls__.__data_types__[0](0),
            data=self.__schemacls__.__data_types__[0](-1),
            error=True
        )

    def test_max(self):

        if self.__schemacls__ is None:
            return

        self._assert(
            max=self.__schemacls__.__data_types__[0](0),
            data=self.__schemacls__.__data_types__[0](2),
            error=True
        )


class IntegerSchemaTest(NumberSchemaTest):

    __schemacls__ = IntegerSchema


class ComplexSchemaTest(NumberSchemaTest):

    __schemacls__ = ComplexSchema


class LongSchemaTest(NumberSchemaTest):

    __schemacls__ = LongSchema


class FloatSchemaTest(NumberSchemaTest):

    __schemacls__ = FloatSchema


class StringSchemaTest(ElementaryTest):

    __schemacls__ = StringSchema


class TypeSchemaTest(ElementaryTest):

    __schemacls__ = TypeSchema

    def test_cls(self):

        self._assert(data=type)


class ArraySchemaTest(ElementaryTest):

    __schemacls__ = ArraySchema

    def test_maxsize(self):

        self._assert(maxsize=0, data=[])

    def test_maxsize_1(self):

        self._assert(maxsize=1, data=[1])

    def test_maxsize_1_0(self):

        self._assert(maxsize=1, data=[])

    def test_maxsize_error(self):

        self._assert(maxsize=1, data=[1, 0], error=True)

    def test_minsize(self):

        self._assert(minsize=0, data=[])

    def test_minsize_0(self):

        self._assert(minsize=0, data=[1])

    def test_minsize_1(self):

        self._assert(minsize=1, data=[1])

    def test_minsize_error(self):

        self._assert(minsize=1, data=[], error=True)

    def test_itemtype(self):

        self._assert(data=[1, 2], itemtype=int)

    def test_itemtype_error(self):

        self._assert(data=[1, 2.], itemtype=int, error=True)

    def test_unique(self):

        self._assert(data=[1, 2], unique=True)

    def test_unique_error(self):

        self._assert(data=[1, 1], unique=True, error=True)


class DictSchemaTest(ElementaryTest):

    __schemacls__ = DictSchema

    def test_maxsize(self):

        self._assert(maxsize=0, data={})

    def test_maxsize_1(self):

        self._assert(maxsize=1, data={None: None})

    def test_maxsize_1_0(self):

        self._assert(maxsize=1, data={})

    def test_maxsize_error(self):

        self._assert(maxsize=1, data={None: None, 1: 1}, error=True)

    def test_minsize(self):

        self._assert(minsize=0, data={})

    def test_minsize_0(self):

        self._assert(minsize=0, data={None: None})

    def test_minsize_1(self):

        self._assert(minsize=1, data={None: None})

    def test_minsize_error(self):

        self._assert(minsize=1, data={}, error=True)

    def test_itemtype(self):

        self._assert(data={1: 1, 2: 2}, itemtype=int)

    def test_itemtype_error(self):

        self._assert(data={1: None, 2.: None}, itemtype=int, error=True)

    def test_valuetype(self):

        self._assert(data={1: 1, 2.: 2}, valuetype=int)

    def test_valuetype_error(self):

        self._assert(data={1: 1, 2: 2.}, valuetype=int, error=True)

    def test_unique(self):

        self._assert(data={1: 1, 2: 2}, unique=True)

    def test_unique_error(self):

        self._assert(data={1: 1, 2: 1}, unique=True, error=True)

if __name__ == '__main__':
    main()
