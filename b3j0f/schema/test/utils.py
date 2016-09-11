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

from .base import Schema
from ..utils import (
    DynamicValue, data2schema, This, validate, updatecontent, RegisteredSchema,
    dump
)
from ..registry import registercls, unregistercls

from six import string_types

from numbers import Number


class UpdateContentTest(UTCase):

    def setUp(self):

        @registercls([Number])
        class NumberSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, Number)

        self.NumberSchema = NumberSchema

        @registercls([string_types])
        class StrSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, string_types)

        self.StrSchema = StrSchema

        @registercls([type])
        class ObjectSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, type)

        self.ObjectSchema = ObjectSchema

    def tearDown(self):

        unregistercls(self.NumberSchema)
        unregistercls(self.StrSchema)
        unregistercls(self.ObjectSchema)

    def _assert(self, schemacls):

        self.assertIsInstance(schemacls.a, self.NumberSchema)
        self.assertIsInstance(schemacls.b, self.NumberSchema)
        self.assertIsInstance(schemacls.c, self.StrSchema)
        self.assertIsInstance(schemacls.d, self.ObjectSchema)
        self.assertIsNone(schemacls.e)

    def test_object(self):

        class TestSchema(object):

            a = 1
            b = 2.
            c = str()
            d = object
            e = None

        updatecontent(TestSchema, updateparents=False)

        self._assert(TestSchema)

    def test_schema(self):

        class TestSchema(Schema):

            a = 1
            b = 2.
            c = str()
            d = object
            e = None

        updatecontent(TestSchema, updateparents=False)

        self._assert(TestSchema)

    def test_object_decorator(self):

        @updatecontent(updateparents=False)
        class TestSchema(object):

            a = 1
            b = 2.
            c = str()
            d = object
            e = None

        self._assert(TestSchema)

    def test_schema_decorator(self):

        @updatecontent(updateparents=False)
        class TestSchema(Schema):

            a = 1
            b = 2.
            c = str()
            d = object
            e = None

        self._assert(TestSchema)


class DumpTest(UTCase):

    def test_dump(self):

        schema = Schema()

        dumped = dump(schema)

        self.assertEqual(
            dumped,
            {
                'default': schema.default,
                #'doc': schema.doc,
                #'name': schema.name,
                #'nullable': schema.nullable,
                #'uuid': schema.uuid,
                #'version': schema.version
            }
        )

    def test_dumped_content(self):

        class TestSchema(RegisteredSchema):

            a = Schema(default=Schema())

            b = Schema()

        schema = TestSchema()

        dumped = dump(schema)

        self.assertEqual(
            dumped,
            {
                'a': {
                    'default': schema.a.default,
                    #'doc': schema.a.doc,
                    #'name': schema.a.name,
                    #'nullable': schema.a.nullable,
                    #'uuid': schema.a.uuid,
                    #'version': schema.a.version
                },
                'b': None,
                'default': schema.default,
                #'doc': schema.doc,
                #'name': schema.name,
                #'nullable': schema.nullable,
                #'uuid': schema.uuid,
                #'version': schema.version
            }
        )


class ValidateTest(UTCase):

    def test_validate(self):

        schema = Schema()

        validate(schema, None)
        self.assertRaises(TypeError, validate, schema, 1)
        schema.nullable = False
        self.assertRaises(TypeError, validate, schema, None)
        schema.nullable = True
        validate(schema, None)


class ThisTest(UTCase):

    def test_error(self):

        def definition():

            class Test(RegisteredSchema):

                test = This(default='test', nullable=False)

                def __init__(self, *args, **kwargs):

                    super(Test, self).__init__(*args, **kwargs)

        self.assertRaises(NameError, definition)

    def test_error_deco(self):

        def definition():

            @updatecontent
            class Test(Schema):

                __update_content__ = False

                test = This(default='test', nullable=False)

                def __init__(self, *args, **kwargs):

                    super(Test, self).__init__(*args, **kwargs)

        self.assertRaises(NameError, definition)

    def test(self):

        class Test(Schema):

            __update_content__ = False

            test = This(default='test', nullable=False)

            def __init__(self, *args, **kwargs):

                super(Test, self).__init__(*args, **kwargs)

        self.assertIsInstance(Test.test, This)

        updatecontent(Test)

        self.assertIsInstance(Test.test, Test)
        self.assertEqual(Test.test.default, 'test')
        self.assertFalse(Test.test.nullable)

    def test_params(self):

        this = This(1, 2, a=3, b=4)

        self.assertEqual(this.args, (1, 2))
        self.assertEqual(this.kwargs, {'a': 3, 'b': 4})


class DynamicValueTest(UTCase):

    def test(self):

        dvalue = DynamicValue(lambda: 'test')

        self.assertEqual('test', dvalue())


class FromObjTest(UTCase):

    class BaseTest(Schema):

        def __init__(self, default=None, *args, **kwargs):

            super(FromObjTest.BaseTest, self).__init__(*args, **kwargs)
            self.default = default

    class Test(BaseTest):
        pass

    def setUp(self):

        registercls(
            schemacls=FromObjTest.BaseTest, data_types=[FromObjTest.BaseTest]
        )

    def test_default(self):

        self.assertIsNone(data2schema(True))

    def test_default_force(self):

        self.assertRaises(NotImplementedError, data2schema, True, _force=True)

    def test_default_besteffort(self):

        self.assertIsNone(data2schema(True, _besteffort=False))

    def test_dynamicvalue(self):

        self.assertIsNone(data2schema(DynamicValue(lambda: True)))

    def test_registered(self):

        test = FromObjTest.Test()
        res = data2schema(test)

        self.assertEqual(res.default, test)

    def test_registered_besteffort(self):

        test = FromObjTest.Test()
        res = data2schema(test, _besteffort=False)

        self.assertIsNone(res)


class DefaultTest(UTCase):

    def test(self):

        class TestSchema(RegisteredSchema):

            default = 0

        schema = TestSchema()
        self.assertEqual(schema.default, 0)

        schema = TestSchema(default=None)
        self.assertIsNone(schema._default)
        self.assertIsNone(schema.default)


if __name__ == '__main__':
    main()
