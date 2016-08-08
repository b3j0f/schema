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


from unittest import main

from b3j0f.utils.ut import UTCase

from ..base import Schema

from ..elementary import (
        IntegerSchema, FloatSchema, ComplexSchema, LongSchema,
        StringSchema,
        ArraySchema,
        BooleanSchema,
        EnumSchema,
        FunctionSchema,
        ElementaryTest
    )


class ElementaryTest(UTCase):

    __class__ = None

    def _assert(self, value, error=False, **kwargs):

        schema = self.__class__(**kwargs)

        if error:
            self.assertRaises(Exception, schema.validate, value)

        else:
            schema.validate(value)


class IntegerSchemaTest(ElementaryTest):

    __class__ = IntegerSchema

    def test_default(self):

        self._assert(0)

    def test_min(self):

        self._assert(min=0, value=-2, error=True)

    def test_max(self):

        self._assert(max=0, value=2, error=True)


if __name__ == '__main__':
    main()
