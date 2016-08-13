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

from ..registry import registercls
from ..base import Schema, DynamicValue, resolveschema


class CLSSchemaMaker(UTCase):

    class Test(object):
        pass

    def setUp(self):

        class TestSchema(Schema):
            pass

        registercls(Schema, [CLSSchemaMaker.Test])

    def test_schema(self):

        class TestSchema(Schema):
            pass

        self.assertEqual(TestSchema.getschemas(), Schema.getschemas())

    def test_content_schema(self):

        class TestSchema(Schema):

            a = 'a'
            b = CLSSchemaMaker.Test()

        self.assertEqual(TestSchema.a, 'a')
        self.assertIsInstance(TestSchema.b, Schema)
        self.assertIsInstance(TestSchema.b.default, CLSSchemaMaker.Test)


class SchemaTest(UTCase):

    def test_init(self):

        schema = Schema()

        self.assertIsNone(schema._fget)
        self.assertIsNone(schema._fset)
        self.assertIsNone(schema._fdel)
        self.assertIsNone(schema._value)

    def test_init_gsd(self):

        processing = []

        class Test(object):

            test = Schema()

        test = Test()

        res = test.test
        self.assertIsNone(res)

        test.test = Schema()
        self.assertIsInstance(test.test, Schema)

        del test.test
        self.assertFalse(hasattr(test, 'test'))

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


class TestResolveSchema(UTCase):

    class Test(object):
        pass

    class SchemaTest(Schema):
        pass

    def setUp(self):

        registercls(TestResolveSchema.SchemaTest, [TestResolveSchema.Test])

    def test_default(self):

        class Test(Schema):

            default = TestResolveSchema.Test()

        test = Test()

        self.assertIsInstance(test.default, TestResolveSchema.SchemaTest)

    def test_subtest(self):

        class Test(Schema):

            subtest = TestResolveSchema.Test()

        test = Test()

        self.assertIsInstance(test.subtest, TestResolveSchema.SchemaTest)

if __name__ == '__main__':
    main()
