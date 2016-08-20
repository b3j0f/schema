#!/usr/bin/env python
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


from unittest import main, skipIf

from b3j0f.utils.ut import UTCase

from ..base import Schema

from ..elementary import (
        IntegerSchema, FloatSchema, ComplexSchema, LongSchema,
        StringSchema,
        ArraySchema,
        BooleanSchema,
        EnumSchema
    )


class ElementaryTest(UTCase):

    __schemacls__ = None

    def _assert(self, data, error=False, **kwargs):

        schema = self.__schemacls__(**kwargs)

        if error:
            self.assertRaises(Exception, schema.validate, data=data)

        else:
            schema.validate(data)


class NumberSchemaTest(ElementaryTest):

    def test_default(self):

        if self.__schemacls__ is None:
            self.skipTest('base class')

        self._assert(
            self.__schemacls__.__data_types__[0](0)
        )

    def test_min(self):

        if self.__schemacls__ is None:
            self.skipTest('base class')

        self._assert(
            min=self.__schemacls__.__data_types__[0](0),
            data=self.__schemacls__.__data_types__[0](-1),
            error=True
        )

    def test_max(self):

        if self.__schemacls__ is None:
            self.skipTest('base class')

        self._assert(
            max=self.__schemacls__.__data_types__[0](0),
            data=self.__schemacls__.__data_types__[0](2),
            error=True
        )


class IntegerSchemaTest(NumberSchemaTest):

    __schemacls__ = IntegerSchema


class LongSchemaTest(NumberSchemaTest):

    __schemacls__ = LongSchema


class ComplexSchemaTest(NumberSchemaTest):

    __schemacls__ = ComplexSchema


class FloatSchemaTest(NumberSchemaTest):

    __schemacls__ = FloatSchema

if __name__ == '__main__':
    main()
