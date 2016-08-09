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

from ..factory import SchemaFactory


class TestFactory(UTCase):

    def setUp(self):

        self.factory = SchemaFactory()

    def maker(self, _type):
        """maker generator."""

        def result(resource):
            if not isinstance(resource, _type):
                raise TypeError()

            return resource

        return result

    def test_register(self):

        makerstr = self.maker(str)
        makerint = self.maker(int)

        schemastr = 'test'
        schemaint = 2

        self.factory = SchemaFactory()

        self.assertRaises(TypeError, self.factory.make, schemaint)
        self.assertRaises(KeyError, self.factory.getschemacls, schemaint)
        self.assertRaises(TypeError, self.factory.make, schemastr)
        self.assertRaises(KeyError, self.factory.getschemacls, schemastr)

        self.factory.registermaker(name='str', maker=makerstr)

        self.assertRaises(TypeError, self.factory.make, schemaint)
        self.assertRaises(KeyError, self.factory.getschemacls, schemaint)

        schemacls = self.factory.make(schemastr)
        self.assertEqual(schemacls, schemastr)

        schemacls = self.factory.getschemacls(schemastr)
        self.assertEqual(schemacls, schemastr)

        self.factory.registermaker(name='int', maker=makerint)

        schemacls = self.factory.make(schemaint)
        self.assertEqual(schemacls, schemaint)

        schemacls = self.factory.getschemacls(schemaint)
        self.assertEqual(schemacls, schemaint)

        schemacls = self.factory.make(schemastr)
        self.assertEqual(schemacls, schemastr)

        schemacls = self.factory.getschemacls(schemastr)
        self.assertEqual(schemacls, schemastr)

        self.factory.unregistermaker('str')

        schemacls = self.factory.make(schemastr)
        self.assertEqual(schemacls, schemastr)

        self.assertRaises(
            TypeError, self.factory.make, schemastr, cache=False
        )

        schemacls = self.factory.getschemacls(schemastr)
        self.assertEqual(schemacls, schemastr)

        schemacls = self.factory.make(schemaint)
        self.assertEqual(schemacls, schemaint)

        schemacls = self.factory.make(schemastr)
        self.assertEqual(schemacls, schemastr)

    def test_decorator(self):

        @self.factory.registermaker
        def make():
            pass

        self.assertIn('make', self.factory._makers)

    def test_decorator_name(self):

        @self.factory.registermaker('test')
        def make():
            pass

        self.assertIn('test', self.factory._makers)


if __name__ == '__main__':
    main()
