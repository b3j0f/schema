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
from b3j0f.utils.path import getpath

from ...base import Schema
from ..python import (
    PythonSchemaBuilder, FunctionSchema, buildschema, ParamSchema, ParamType
)
from ...elementary import (
    StringSchema, IntegerSchema, FloatSchema, BooleanSchema
)

from inspect import getmembers


class ParamSchemaTest(UTCase):

    def test_default(self):

        param = ParamSchema()

        self.assertFalse(param.hasvalue)
        self.assertEqual(param.type, ParamType.default)
        self.assertIsNone(param.ref)

        param.default = 2
        self.assertEqual(param.default, 2)

    def test_ref(self):

        param = ParamSchema(ref=StringSchema())

        param.default = 'test'

        self.assertEqual(param.default, 'test')

        self.assertRaises(TypeError, setattr, param, 'default', 2)

    def test_hasvalue(self):

        param = ParamSchema(hasvalue=True)

        self.assertTrue(param.hasvalue)

    def test_type(self):

        param = ParamSchema(type=ParamType.keywords)

        self.assertEqual(param.type, ParamType.keywords)

        param.type = ParamType.varargs

        self.assertEqual(param.type, ParamType.varargs)


class FunctionSchemaTest(UTCase):

    def test_lambda_default(self):

        schema = FunctionSchema(default=lambda: None)

        self.assertFalse(schema.params)

    def test_lambda_params(self):

        schema = FunctionSchema(default=lambda a, b=2: None)

        self.assertTrue(schema.params)

    def test_function(self):

        def test(a, b, c=3.):
            """
            :param str a:
            :type b: int
            :rtype: bool
            """

        schema = FunctionSchema(default=test)

        self.assertIsInstance(schema.params[0], StringSchema)
        self.assertIsInstance(schema.params[1], IntegerSchema)
        self.assertIsInstance(schema.params[2], FloatSchema)
        self.assertIsInstance(schema.rtype, BooleanSchema)


class BuildSchemaTest(UTCase):

    def test_default(self):

        @buildschema
        class Test(object):
            pass

        test = Test()

        self.assertIsInstance(test, Schema)
        self.assertTrue(issubclass(Test, Schema))
        self.assertEqual(test.name, 'Test')

    def test_name(self):

        @buildschema(name='test')
        class Test(object):
            pass

        test = Test()
        self.assertIsInstance(test, Schema)
        self.assertTrue(issubclass(Test, Schema))
        self.assertEqual(test.name, 'test')

if __name__ == '__main__':
    main()
