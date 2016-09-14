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
    StringSchema, IntegerSchema, FloatSchema, BooleanSchema, ArraySchema,
    DictSchema
)

from inspect import getmembers


class ParamSchemaTest(UTCase):

    def test_autotype(self):

        param = ParamSchema(default=1)

        self.assertIsInstance(param.ref, IntegerSchema)

    def test_notautotype(self):

        param = ParamSchema(autotype=False, default=1)

        self.assertIsNone(param.ref)

        self.assertRaises(TypeError, ParamSchema, ref=IntegerSchema, default='')

    def test_autotype_dynamique(self):

        param = ParamSchema()

        param.default = 1

        self.assertIsInstance(param.ref, IntegerSchema)

        param.ref = None

        self.assertEqual(param.default, 1)

    def test_notautotype_dynamique(self):

        param = ParamSchema(autotype=False)

        param.default = 1

        self.assertIsNone(param.ref)

    def test_default(self):

        param = ParamSchema()

        self.assertEqual(param.type, ParamType.default)
        self.assertIsNone(param.ref)

        param.default = 2
        self.assertEqual(param.default, 2)

    def test_ref(self):

        param = ParamSchema(ref=StringSchema())

        param.default = 'test'

        self.assertEqual(param.default, 'test')

        self.assertRaises(TypeError, setattr, param, 'default', 2)

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

        def test(a, b, c, d, e=3., *args, **kwargs):
            """
            :param bool b:
            :type c: int
            :rtype: bool
            """

        schema = FunctionSchema(
            default=test,
            params=[ParamSchema(name='d', default=3)]
        )

        self.assertEqual(len(schema.params), 7)

        aparam = schema.params[0]
        self.assertIsNone(aparam.ref)
        self.assertEqual(aparam.name, 'a')
        self.assertEqual(aparam.type, ParamType.default)
        self.assertIsNone(aparam.default)

        bparam = schema.params[1]
        self.assertIsInstance(bparam.ref, BooleanSchema)
        self.assertEqual(bparam.name, 'b')
        self.assertEqual(bparam.type, ParamType.default)
        self.assertIs(bparam.default, False)

        cparam = schema.params[2]
        self.assertIsInstance(cparam.ref, IntegerSchema)
        self.assertEqual(cparam.name, 'c')
        self.assertEqual(cparam.type, ParamType.default)
        self.assertIs(cparam.default, 0)

        dparam = schema.params[3]

        self.assertIsInstance(dparam.ref, IntegerSchema)
        self.assertEqual(dparam.name, 'd')
        self.assertEqual(dparam.type, ParamType.default)
        self.assertIs(dparam.default, 3)

        eparam = schema.params[4]

        self.assertIsInstance(eparam.ref, FloatSchema)
        self.assertEqual(eparam.name, 'e')
        self.assertEqual(eparam.type, ParamType.default)
        self.assertIs(eparam.default, 3.)

        fparam = schema.params[5]

        self.assertIsInstance(fparam.ref, ArraySchema)
        self.assertEqual(fparam.name, 'args')
        self.assertEqual(fparam.type, ParamType.varargs)
        self.assertEqual(fparam.default, [])

        gparam = schema.params[6]

        self.assertIsInstance(gparam.ref, DictSchema)
        self.assertEqual(gparam.name, 'kwargs')
        self.assertEqual(gparam.type, ParamType.keywords)
        self.assertEqual(gparam.default, {})

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
