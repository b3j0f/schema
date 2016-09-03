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
from ..base import (
    Schema, DynamicValue, updatecontent, RefSchema, This, dump, validate
)


class ThisTest(UTCase):

    def test_error(self):

        def definition():

            class Test(Schema):

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


class DefaultTest(UTCase):

    def test(self):

        class TestSchema(Schema):

            default = 0

        schema = TestSchema()
        self.assertEqual(schema.default, 0)

        schema = TestSchema(default=None)
        self.assertIsNone(schema.default)


class UpdateContentTest(UTCase):

    class NumberSchema(Schema):

        __data_types__ = [Number]

        def _validate(self, data, *args, **kwargs):

            return isinstance(data, Number)

    class StrSchema(Schema):

        __data_types__  = [string_types]

        def _validate(self, data, *args, **kwargs):

            return isinstance(data, string_types)

    class ObjectSchema(Schema):

        __data_types__ = [type]

        def _validate(self, data, *args, **kwargs):

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

        @updatecontent
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

        self.assertRaises(AttributeError, schema._validate, 0)

    def test_owner(self):

        schema = RefSchema()

        class NumberSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, Number)

        numberschema = NumberSchema()

        schema._validate(0, owner=numberschema)

    def test_ref(self):

        class NumberSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, Number)

        numberschema = NumberSchema()

        schema = RefSchema(ref=numberschema)

        schema._validate(0)


class SchemaTest(UTCase):

    def test_init(self):

        schema = Schema()

        self.assertIsNone(schema._fget)
        self.assertIsNone(schema._fset)
        self.assertIsNone(schema._fdel)

    def test_uuid(self):

        schema1 = Schema()
        schema2 = Schema()

        self.assertNotEqual(schema1.uuid, schema2.uuid)

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
        self.assertFalse(hasattr(test, Test.test._attrname()))

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

    def test__validate(self):

        schema = Schema()

        schema._validate(None)
        self.assertRaises(TypeError, schema._validate, 1)
        schema.nullable = False
        self.assertRaises(TypeError, schema._validate, None)
        schema.nullable = True
        schema._validate(None)

    def test_validate(self):

        schema = Schema()

        validate(schema, None)
        self.assertRaises(TypeError, validate, schema, 1)
        schema.nullable = False
        self.assertRaises(TypeError, validate, schema, None)
        schema.nullable = True
        validate(schema, None)

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

        dumped = dump(schema)

        self.assertEqual(
            dumped,
            {
                'default': schema.default,
                'doc': schema.doc,
                'name': schema.name,
                'nullable': schema.nullable,
                'uuid': schema.uuid,
                'version': schema.version
            }
        )

    def test_dumped_content(self):

        class TestSchema(Schema):

            a = Schema(default=Schema())

            b = Schema()

        schema = TestSchema()

        dumped = dump(schema)

        self.assertEqual(
            dumped,
            {
                'a': {
                    'default': schema.a.default,
                    'doc': schema.a.doc,
                    'name': schema.a.name,
                    'nullable': schema.a.nullable,
                    'uuid': schema.a.uuid,
                    'version': schema.a.version
                },
                'b': None,
                'default': schema.default,
                'doc': schema.doc,
                'name': schema.name,
                'nullable': schema.nullable,
                'uuid': schema.uuid,
                'version': schema.version
            }
        )

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
