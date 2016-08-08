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

from ..registry import SchemaRegistry, getbyuuid, getbyname, unregister, fromobj

from uuid import uuid4

from numbers import Number


class TestSchema(object):

    def __init__(
            self, name=None, uuid=None, _=None, default=None, *args, **kwargs
    ):

        super(TestSchema, self).__init__(*args, **kwargs)

        self.name = name or TestSchema.__name__
        self.uuid = uuid or uuid4()
        self._testschema = _ or TestSchema(_=self)
        self.default = default

    def __eq__(self, other):

        return self.name == other.name and self.uuid == other.uuid

    def schemas(self):

        return (('one', self), ('two', self._testschema))


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

        schemaregistry = SchemaRegistry(schbyname =2, schbyuuid=3, schbytype=4)
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

    def test_register_with_data_types(self):

        schemaint = TestSchema()
        schemabool = TestSchema()
        schemanumber = TestSchema()

        self.assertRaises(TypeError, self.registry.fromobj, 1)

        self.assertRaises(TypeError, self.registry.fromobj, TestSchema())

        self.registry.register(schemaint, data_types=[int])
        self.registry.register(schemabool, data_types=[bool])
        self.registry.register(schemanumber, data_types=[Number])

        _schema = self.registry.fromobj(1, uuid=schemaint.uuid)
        self.assertEqual(schemaint, _schema)

        _schema = self.registry.fromobj(lambda: 1, uuid=schemaint.uuid)
        self.assertEqual(schemaint, _schema)

        _schema = self.registry.fromobj(True, uuid=schemabool.uuid)
        self.assertEqual(_schema, schemabool)

        _schema = self.registry.fromobj(lambda: True, uuid=schemabool.uuid)
        self.assertEqual(_schema, schemabool)

        self.registry.unregister(schemaint.uuid)
        _schema = self.registry.fromobj(1, uuid=schemanumber.uuid)
        self.assertEqual(_schema, schemanumber)

        _schema = self.registry.fromobj(lambda: 1, uuid=schemanumber.uuid)
        self.assertEqual(_schema, schemanumber)

if __name__ == '__main__':
    main()
