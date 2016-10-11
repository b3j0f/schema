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

from ...base import Schema
from ...utils import updatecontent, AnySchema
from ..python import (
    FunctionSchema, buildschema, ParamSchema
)
from ...elementary import (
    StringSchema, IntegerSchema, FloatSchema, BooleanSchema
)


class ParamSchemaTest(UTCase):

    def test_autotype(self):

        param = ParamSchema(default=1)

        self.assertIsInstance(param.ref, IntegerSchema)

    def test_notautotype(self):

        param = ParamSchema(autotype=False, default=1)

        self.assertIsNone(param.ref)

        self.assertRaises(
            TypeError, ParamSchema, ref=IntegerSchema, default=''
        )

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

        self.assertIsNone(param.ref)

        param.default = 2
        self.assertEqual(param.default, 2)

    def test_ref(self):

        param = ParamSchema(ref=StringSchema())

        param.default = 'test'

        self.assertEqual(param.default, 'test')

        self.assertRaises(TypeError, setattr, param, 'default', 2)


class FunctionSchemaTest(UTCase):

    def test_lambda(self):

        schema = FunctionSchema(default=lambda: None)

        self.assertFalse(schema.params)

    def test_lambda_params(self):

        schema = FunctionSchema(default=lambda a, b=2: None)

        self.assertTrue(schema.params)

    def test_function(self):

        def test(a, b, c, d, e=3., f=None, *args, **kwargs):
            """
            :param bool b:
            :type c: int
            :rtype: bool
            """

        schema = FunctionSchema(
            default=test,
            params=[
                ParamSchema(name='d', default=3, mandatory=False),
                ParamSchema(name='c', mandatory=True)
            ]
        )

        self.assertEqual(len(schema.params), 6)

        aparam = schema.params[0]
        self.assertIsNone(aparam.ref)
        self.assertTrue(aparam.mandatory)
        self.assertEqual(aparam.name, 'a')
        self.assertIsNone(aparam.default)

        bparam = schema.params[1]
        self.assertIsInstance(bparam.ref, BooleanSchema)
        self.assertFalse(bparam.mandatory)
        self.assertEqual(bparam.name, 'b')
        self.assertIs(bparam.default, False)

        cparam = schema.params[2]
        self.assertIsInstance(cparam.ref, IntegerSchema)
        self.assertTrue(cparam.mandatory)
        self.assertEqual(cparam.name, 'c')
        self.assertIs(cparam.default, 0)

        dparam = schema.params[3]
        self.assertIsInstance(dparam.ref, IntegerSchema)
        self.assertTrue(dparam.mandatory)
        self.assertEqual(dparam.name, 'd')
        self.assertIs(dparam.default, 3)

        eparam = schema.params[4]
        self.assertIsInstance(eparam.ref, FloatSchema)
        self.assertFalse(eparam.mandatory)
        self.assertEqual(eparam.name, 'e')
        self.assertIs(eparam.default, 3.)

        fparam = schema.params[5]
        self.assertIsNone(fparam.ref, AnySchema)
        self.assertFalse(fparam.mandatory)
        self.assertEqual(fparam.name, 'f')
        self.assertIsNone(fparam.default)

        self.assertIsInstance(schema.rtype, BooleanSchema)

    def test_method(self):

        @updatecontent
        class Test(Schema):

            def test(self):
                """
                :param BuildSchemaTest self:
                """

                return self

        test = Test()

        self.assertIsInstance(Test.test, FunctionSchema)
        self.assertNotIsInstance(test.test, FunctionSchema)

        res = Test.test(test)

        self.assertIs(res, test)

        res = test.test()

        self.assertIs(res, test)

        param = Test.test.params[0]

        self.assertEqual(param.name, 'self')
        self.assertIsInstance(param.ref, Schema)


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
