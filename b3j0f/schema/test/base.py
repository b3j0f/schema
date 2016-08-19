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

from numbers import Number
from six import string_types

from ..registry import registercls, getbydatatype
from ..base import Schema, DynamicValue, updatecontent, RefSchema, This


class ThisTest(UTCase):

    def test(self):

        class Test(Schema):

            test = This(default='test', nullable=False)

        self.assertIsInstance(Test.test, Test)
        self.assertEqual(Test.test.default, 'test')
        self.assertFalse(Test.test.nullable)


class UpdateContentTest(UTCase):

    class NumberSchema(Schema):

        __data_types__ = [Number]

        def validate(self, data, *args, **kwargs):

            return isinstance(data, Number)

    class StrSchema(Schema):

        __data_types__  = [string_types]

        def validate(self, data, *args, **kwargs):

            return isinstance(data, string_types)

    class ObjectSchema(Schema):

        __data_types__ = [type]

        def validate(self, data, *args, **kwargs):

            return isinstance(data, type)

    def test_number(self):

        schemacls = getbydatatype(int)
        self.assertIs(schemacls, UpdateContentTest.NumberSchema)

    def test_str(self):

        schemacls = getbydatatype(str)
        self.assertIs(schemacls, UpdateContentTest.StrSchema)

    def test_object(self):

        schemacls = getbydatatype(type)
        self.assertIs(schemacls, UpdateContentTest.ObjectSchema)

    def _assert(self, schemacls):

        self.assertIsInstance(schemacls.a, UpdateContentTest.NumberSchema)
        self.assertIsInstance(schemacls.b, UpdateContentTest.NumberSchema)
        self.assertIsInstance(schemacls.c, UpdateContentTest.StrSchema)
        self.assertIsInstance(schemacls.d, UpdateContentTest.ObjectSchema)
        self.assertIsNone(schemacls.e)

    def test_object(self):

        class TestSchema(object):

            a = 1
            b = 2.
            c = str()
            d = object
            e = None

        updatecontent(TestSchema)

        self._assert(TestSchema)

    def test_schema(self):

        class TestSchema(Schema):

            a = 1
            b = 2.
            c = str()
            d = object
            e = None

        self._assert(TestSchema)


class RefSchemaTest(UTCase):

    def test_default(self):

        schema = RefSchema()

        self.assertRaises(AttributeError, schema.validate, 0)

    def test_owner(self):

        schema = RefSchema()

        class NumberSchema(Schema):
            def validate(self, data, *args, **kwargs):

                return isinstance(data, Number)

        numberschema = NumberSchema()

        schema.validate(0, owner=numberschema)

    def test_ref(self):

        class NumberSchema(Schema):
            def validate(self, data, *args, **kwargs):

                return isinstance(data, Number)

        numberschema = NumberSchema()

        schema = RefSchema(ref=numberschema)

        schema.validate(0)


class SchemaTest(UTCase):

    def test_init(self):

        schema = Schema()

        self.assertIsNone(schema._fget)
        self.assertIsNone(schema._fset)
        self.assertIsNone(schema._fdel)

    def test_init_gsd(self):

        processing = []

        class Test(object):

            test = Schema()

        test = Test()

        res = test.test
        self.assertIsNone(res)

        schema = Schema()

        test.test = schema
        self.assertIsInstance(test.test, Schema)

        del test.test
        self.assertFalse(hasattr(test, Test.test.attrname()))

        test.test = Schema()
        self.assertIsInstance(test.test, Schema)

    def test_init_gsd_custom(self):

        processing = []

        class Test(object):

            @Schema
            def test(self):
                processing.append('getter')
                return getattr(self, '_value', self)

            @test.setter
            def test(self, value):
                processing.append('setter')
                self._value = value

            @test.deleter
            def test(self):
                processing.append('deleter')
                del self._value

        test = Test()
        self.assertNotIn('getter', processing)
        self.assertNotIn('setter', processing)
        self.assertNotIn('deleter', processing)

        res = test.test
        self.assertEqual(res, test)
        self.assertIn('getter', processing)
        self.assertNotIn('setter', processing)
        self.assertNotIn('deleter', processing)

        test.test = Schema()
        self.assertIsInstance(test.test, Schema)
        self.assertIn('getter', processing)
        self.assertIn('setter', processing)
        self.assertNotIn('deleter', processing)

        test.test = None
        Test.test.nullable = False
        self.assertRaises(TypeError, setattr, test, 'test', None)
        self.assertRaises(TypeError, setattr, test, 'test', 1)

        test.test = DynamicValue(lambda: Schema())

        self.assertRaises(TypeError, setattr, test, 'test', lambda: None)
        self.assertRaises(TypeError, setattr, test, 'test', lambda: 1)

        Test.test.nullable = True
        test.test = DynamicValue(lambda: None)

        del test.test
        self.assertFalse(hasattr(test, '_value'))
        self.assertIn('getter', processing)
        self.assertIn('setter', processing)
        self.assertIn('deleter', processing)

        test.test = Schema()
        self.assertIsInstance(test.test, Schema)
        self.assertIn('getter', processing)
        self.assertIn('setter', processing)
        self.assertIn('deleter', processing)

    def test_validate(self):

        schema = Schema()

        schema.validate(None)
        self.assertRaises(TypeError, schema.validate, 1)
        schema.nullable = False
        self.assertRaises(TypeError, schema.validate, None)
        schema.nullable = True
        schema.validate(None)

    def test_getschemas(self):

        class TestSchema(Schema):

            a = Schema()

            b = Schema()

        names = ['a', 'b']

        schemas = TestSchema.getschemas()

        self.assertEqual(len(Schema.getschemas()) + 2, len(schemas))

        schema = TestSchema()

        schemas = schema.getschemas()

        self.assertEqual(len(Schema.getschemas()) + 2, len(schemas))

    def test_dump(self):

        schema = Schema()

        dump = schema.dump()

        _dump = {}
        for name, schema in schema.getschemas().items():
            _dump[name] = schema.default

        self.assertEqual(dump, _dump)

    def test_dump_content(self):

        class TestSchema(Schema):

            a = Schema(default=Schema())

            b = Schema()

        schema = TestSchema()

        dump = schema.dump()

        _dump = {}
        for name, schema in schema.getschemas().items():
            _dump[name] = schema.default

        self.assertEqual(dump, _dump)

    def test_notify_get(self):

        class TestSchema(Schema):

            test = Schema()
            schema = None
            value = None

            def _getvalue(self, schema, value):

                if schema.name == 'test':
                    self.schema = schema
                    self.value = value

        self.assertIsNone(TestSchema.schema)
        self.assertIsNone(TestSchema.value)

        schema = TestSchema()
        schema.test = Schema()
        schema.test

        self.assertIs(schema.schema, TestSchema.test)
        self.assertIs(schema.value, schema.test)

    def test_notify_set(self):

        class TestSchema(Schema):

            test = Schema()
            schema = None
            value = None

            def _setvalue(self, schema, value):

                if schema.name == 'test':
                    self.schema = schema
                    self.value = value

        self.assertIsNone(TestSchema.schema)
        self.assertIsNone(TestSchema.value)

        schema = TestSchema()
        schema.test = Schema()

        self.assertIs(schema.schema, TestSchema.test)
        self.assertIs(schema.value, schema.test)

    def test_notify_del(self):

        class TestSchema(Schema):

            test = Schema()
            schema = None

            def _delvalue(self, schema):

                if schema.name == 'test':
                    self.schema = schema

        self.assertIsNone(TestSchema.schema)

        schema = TestSchema()
        del schema.test

        self.assertIs(schema.schema, TestSchema.test)

if __name__ == '__main__':
    main()
