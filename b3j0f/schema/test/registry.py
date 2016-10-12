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

from ..base import Schema
from ..registry import (
    SchemaRegistry, registercls, getbydatatype, unregistercls
)

from uuid import uuid4

from numbers import Number


class AAA(object):
    pass


class UpdateContentTest(UTCase):

    def setUp(self):

        class AAA(object):
            pass

        self.AAA = AAA

        class BBB(object):
            pass

        self.BBB = BBB

        class CCC(object):
            pass

        self.CCC = CCC

        @registercls([AAA])
        class AAASchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, AAA)

        self.AAASchema = AAASchema

        @registercls([BBB])
        class BBBSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, BBB)

        self.BBBSchema = BBBSchema

        @registercls([CCC])
        class CCCSchema(Schema):

            def _validate(self, data, *args, **kwargs):

                return isinstance(data, CCC)

        self.CCCSchema = CCCSchema

    def tearDown(self):

        unregistercls(self.AAASchema)
        unregistercls(self.BBBSchema)
        unregistercls(self.CCCSchema)

    def test_number(self):

        schemacls = getbydatatype(self.AAA)
        self.assertIs(schemacls, self.AAASchema)

    def test_str(self):

        schemacls = getbydatatype(self.BBB)
        self.assertIs(schemacls, self.BBBSchema)

    def test_object(self):

        schemacls = getbydatatype(self.CCC)
        self.assertIs(schemacls, self.CCCSchema)


class DefaultTest(UTCase):

    def test(self):

        class TestSchema(Schema):

            default = 0

        schema = TestSchema()
        self.assertEqual(schema.default, 0)

        schema = TestSchema(default=None)
        self.assertIsNone(schema._default_)


class TestSchema(Schema):

    def __init__(
            self, name=None, uuid=None, _=None, default=None, *args, **kwargs
    ):

        super(TestSchema, self).__init__(*args, **kwargs)

        self.name = name or TestSchema.__name__
        self.uuid = str(uuid or uuid4())
        self._testschema = _ or TestSchema(_=self)
        self.default = default

    def __hash__(self):

        return hash(self.uuid)

    def getschemas(self):

        return {'one': self, 'two': self._testschema}


class SchemaRegistryTest(UTCase):

    def setUp(self):

        self.registry = SchemaRegistry()
        self.schemas = set([TestSchema() for i in range(5)])

    def test_init(self):

        schemaregistry = SchemaRegistry()
        self.assertFalse(schemaregistry._schbyname)
        self.assertFalse(schemaregistry._schbyuuid)
        self.assertFalse(schemaregistry._schbytype)

    def test_init_w_params(self):

        schemaregistry = SchemaRegistry(schbyname=2, schbyuuid=3, schbytype=4)
        self.assertEqual(schemaregistry._schbyname, 2)
        self.assertEqual(schemaregistry._schbyuuid, 3)
        self.assertEqual(schemaregistry._schbytype, 4)

    def test_register(self):

        for schema in self.schemas:
            self.registry.register(schema)

        schemas = self.registry.getbyname(TestSchema.__name__)

        self.assertEqual(schemas, self.schemas)

        for schema in self.schemas:
            uuid = schema.uuid
            _schema = self.registry.getbyuuid(uuid)
            self.assertEqual(schema, _schema)

            self.registry.unregister(uuid)
            self.assertRaises(KeyError, self.registry.getbyuuid, uuid)

    def test_registertype(self):

        class Schema(object):

            def __init__(self, default, *args, **kwargs):
                super(Schema, self).__init__(*args, **kwargs)
                self.default = default

        class IntSchema(Schema):
            pass

        class BoolSchema(Schema):
            pass

        class AAASchema(Schema):
            pass

        self.registry.registercls(schemacls=IntSchema, data_types=[int])
        self.registry.registercls(schemacls=BoolSchema, data_types=[bool])
        self.registry.registercls(schemacls=AAASchema, data_types=[Number])

        schemacls = self.registry.getbydatatype(int)
        self.assertIs(schemacls, IntSchema)

        schemacls = self.registry.getbydatatype(bool)
        self.assertIs(schemacls, BoolSchema)

        self.registry.unregistercls(schemacls=IntSchema)
        schemacls = self.registry.getbydatatype(int)
        self.assertIs(schemacls, AAASchema)

    def test_registertype_decorator(self):

        class Schema(object):

            def __init__(self, default, *args, **kwargs):
                super(Schema, self).__init__(*args, **kwargs)
                self.default = default

        @self.registry.registercls([int])
        class IntSchema(Schema):
            pass

        @self.registry.registercls([bool])
        class BoolSchema(Schema):
            pass

        @self.registry.registercls([Number])
        class AAASchema(Schema):
            pass

        schemacls = self.registry.getbydatatype(int)
        self.assertIs(schemacls, IntSchema)

        schemacls = self.registry.getbydatatype(bool)
        self.assertIs(schemacls, BoolSchema)

        self.registry.unregistercls(schemacls=IntSchema)
        schemacls = self.registry.getbydatatype(int)
        self.assertIs(schemacls, AAASchema)

if __name__ == '__main__':
    main()
