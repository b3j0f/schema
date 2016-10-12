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

"""Utils UTs."""

from unittest import main

from b3j0f.utils.ut import UTCase

from .base import Schema
from ..utils import (
    DynamicValue, data2schema, ThisSchema, validate, updatecontent,
    RegisteredSchema, dump, RefSchema, AnySchema, data2schemacls
)
from ..elementary import (
    StringSchema, IntegerSchema, TypeSchema, FloatSchema, BooleanSchema
)
from ..registry import registercls, unregistercls

from six import string_types

from numbers import Number


class UpdateContentTest(UTCase):

    def _assert(self, schemacls):

        self.assertIsInstance(schemacls.a, IntegerSchema)
        self.assertIsInstance(schemacls.b, FloatSchema)
        self.assertIsInstance(schemacls.c, StringSchema)
        self.assertIsInstance(schemacls.d, TypeSchema)
        self.assertIsInstance(schemacls.e, AnySchema)

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
                'name': '',
                'uuid': schema.uuid,
                'nullable': schema.nullable,
                'required': schema.required,
                'version': schema.version,
                'doc': schema.doc
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
                    'default': None,
                    'name': '',
                    'uuid': schema.a.uuid,
                    'nullable': schema.a.nullable,
                    'required': schema.a.required,
                    'version': schema.a.version,
                    'doc': schema.a.doc
                },
                'b': None,
                'default': schema.default,
                'name': '',
                'uuid': schema.uuid,
                'nullable': schema.nullable,
                'required': schema.required,
                'version': schema.version,
                'doc': schema.doc
            }
        )


class ValidateTest(UTCase):

    def test_validate(self):

        schema = Schema()

        validate(schema, None)
        validate(schema, 1)

        schema.nullable = False
        self.assertRaises(ValueError, validate, schema, None)

        schema.nullable = True
        validate(schema, None)


class ThisSchemaTest(UTCase):

    def test_error(self):

        def definition():

            class Test(RegisteredSchema):

                test = ThisSchema(default='test', nullable=False)

                def __init__(self, *args, **kwargs):

                    super(Test, self).__init__(*args, **kwargs)

        self.assertRaises(NameError, definition)

    def test_error_deco(self):

        def definition():

            @updatecontent
            class Test(Schema):

                __update_content__ = False

                test = ThisSchema(default='test', nullable=False)

                def __init__(self, *args, **kwargs):

                    super(Test, self).__init__(*args, **kwargs)

        self.assertRaises(NameError, definition)

    def test(self):

        class Test(Schema):

            __update_content__ = False

            test = ThisSchema(test='test', nullable=False)

            def __init__(self, *args, **kwargs):

                super(Test, self).__init__(*args, **kwargs)

        self.assertIsInstance(Test.test, ThisSchema)

        updatecontent(Test)

        self.assertIsInstance(Test.test, Test)
        self.assertEqual(Test.test._test_, 'test')
        self.assertFalse(Test.test.nullable)

    def test_params(self):

        this = ThisSchema(1, 2, a=3, b=4)

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
            schemacls=FromObjTest.BaseTest,
            data_types=[FromObjTest.BaseTest]
        )

    def tearDown(self):

        unregistercls(FromObjTest.BaseTest)
        unregistercls(FromObjTest.Test)
        unregistercls(object)

    def test_default(self):

        self.assertIsNone(data2schema(object()))

    def test_default_force(self):

        res = data2schema(_data=map, _force=True, name='test')

        self.assertIsNotNone(res)
        self.assertEqual(res.name, 'test')

    def test_default_besteffort(self):

        self.assertIsNone(data2schema(object(), _besteffort=False))

    def test_dynamicvalue(self):

        res = data2schema(DynamicValue(lambda: ''), name='test', _force=True)

        self.assertIsNotNone(res)
        self.assertEqual(res.name, 'test')

    def test_registered(self):

        test = FromObjTest.Test()
        res = data2schema(_data=test)

        self.assertEqual(res.default, test)

    def test_registered_besteffort(self):

        test = FromObjTest.Test()
        res = data2schema(_data=test, _besteffort=False)

        self.assertIsNone(res)

    def test_w_attrs(self):

        class Test(object):
            pass

        test = Test()
        test.test = 1

        res = data2schema(_data=test, _force=True)

        self.assertTrue(hasattr(res, 'test'))


class DefaultTest(UTCase):

    def test(self):

        class TestSchema(RegisteredSchema):

            default = ThisSchema()

        schema = TestSchema()
        self.assertIsInstance(schema.default, TestSchema)

        schema = TestSchema(default=None)
        self.assertIsNone(schema._default_)
        self.assertIsNone(schema.default)


class RefSchemaTest(UTCase):

    def setUp(self):

        class NumberSchema(Schema):

            default = 0

            def _validate(self, data, *args, **kwargs):

                if not isinstance(data, Number):
                    raise TypeError()

        self.numberschema = NumberSchema()

        class StringSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                if not isinstance(data, string_types):
                    raise TypeError()

        self.stringschema = StringSchema()

    def test_default_noref(self):

        schema = RefSchema()

        schema.default = 0

    def test_default(self):

        schema = RefSchema(ref=self.numberschema, default=1)

        self.assertEqual(schema.default, 1)

        schema.default = 0

        self.assertEqual(schema.default, 0)

        self.assertRaises(TypeError, setattr, schema, 'default', '')

    def test_owner(self):

        schema = RefSchema()

        schema._validate(0, owner=self.numberschema)

    def test_ref(self):

        schema = RefSchema(ref=self.numberschema)

        self.assertEqual(schema.default, self.numberschema.default)

        self.assertRaises(TypeError, setattr, schema, 'ref', self.stringschema)


class Dict2SchemaClsTest(UTCase):

    def test_dict(self):

        data = {
            'a': 1,
            'b': True
        }

        schemacls = data2schemacls(_data=data, name='test')

        self.assertIsInstance(schemacls.a, IntegerSchema)
        self.assertEqual(schemacls.a.default, 1)
        self.assertIsInstance(schemacls.b, BooleanSchema)
        self.assertEqual(schemacls.b.default, True)
        self.assertIsInstance(schemacls.name, StringSchema)
        self.assertEqual(schemacls.name.default, 'test')

        validate(schemacls(), data)

    def test_object(self):

        class Test(object):
            a = 1
            b = True

        schemacls = data2schemacls(_data=Test, name='test')

        self.assertIsInstance(schemacls.a, IntegerSchema)
        self.assertEqual(schemacls.a.default, 1)
        self.assertIsInstance(schemacls.b, BooleanSchema)
        self.assertEqual(schemacls.b.default, True)
        self.assertIsInstance(schemacls.name, StringSchema)
        self.assertEqual(schemacls.name.default, 'test')

        validate(schemacls(), Test)
        validate(schemacls(), Test())

if __name__ == '__main__':
    main()
