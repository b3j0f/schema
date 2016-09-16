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

from ..factory import SchemaFactory, SchemaBuilder, getbuilder


class TestFactory(UTCase):

    def setUp(self):

        self.factory = SchemaFactory()

        self.builder = lambda _type: TestFactory.SchemaBuilderTest(_type)

    class SchemaBuilderTest(SchemaBuilder):

        __register__ = False

        def __init__(self, _type, *args, **kwargs):

            super(TestFactory.SchemaBuilderTest, self).__init__(*args, **kwargs)
            self.type = _type

        def build(self, _resource, **kwargs):

            if not isinstance(_resource, self.type):
                raise TypeError()

            return _resource

        def getresource(self, schemacls):

            return schemacls

    def test_register(self):

        makerstr = self.builder(str)
        makerint = self.builder(int)

        schemastr = 'test'
        schemaint = 2

        self.factory = SchemaFactory()

        self.assertRaises(ValueError, self.factory.build, schemaint)
        self.assertIsNone(self.factory.getschemacls(schemaint))
        self.assertRaises(ValueError, self.factory.build, schemastr)
        self.assertIsNone(self.factory.getschemacls(schemastr))

        self.factory.registerbuilder(name='str', builder=makerstr)

        self.assertRaises(ValueError, self.factory.build, schemaint)
        self.assertIsNone(self.factory.getschemacls(schemaint))

        schemacls = self.factory.build(schemastr)
        self.assertEqual(schemacls, schemastr)

        schemacls = self.factory.getschemacls(schemastr)
        self.assertEqual(schemacls, schemastr)

        self.factory.registerbuilder(name='int', builder=makerint)

        schemacls = self.factory.build(schemaint)
        self.assertEqual(schemacls, schemaint)

        schemacls = self.factory.getschemacls(schemaint)
        self.assertEqual(schemacls, schemaint)

        schemacls = self.factory.build(schemastr)
        self.assertEqual(schemacls, schemastr)

        schemacls = self.factory.getschemacls(schemastr)
        self.assertEqual(schemacls, schemastr)

        self.factory.unregisterbuilder(name='str')

        schemacls = self.factory.build(schemastr)
        self.assertEqual(schemacls, schemastr)

        self.assertRaises(
            ValueError, self.factory.build, schemastr, _cache=False
        )

        schemacls = self.factory.getschemacls(schemastr)
        self.assertEqual(schemacls, schemastr)

        schemacls = self.factory.build(schemaint)
        self.assertEqual(schemacls, schemaint)

        schemacls = self.factory.build(schemastr)
        self.assertEqual(schemacls, schemastr)

    def test_autoregister(self):

        class TestSchemaBuilder(SchemaBuilder):
            pass

        builder = getbuilder(TestSchemaBuilder.__name__)

        self.assertIsInstance(builder, TestSchemaBuilder)


if __name__ == '__main__':
    main()
