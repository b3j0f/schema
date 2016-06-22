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

from ..base import getschema
from ..property import Property, SchemaProperty, FunctionProperty
from ..cls import ClassSchema, PythonFunctionProperty


class ClassSchemaTest(UTCase):

    def test(self):

        class Test(object):

            a = 'a'

            def b(self, b):
                return b

        test = Test()

        schema = getschema(Test)

        self.assertIsInstance(schema, ClassSchema)

        self.assertIsInstance(schema['a'], Property)
        self.assertNotIsInstance(schema['a'], FunctionProperty)
        self.assertNotIsInstance(schema['a'], PythonFunctionProperty)

        self.assertIsInstance(schema['b'], Property)
        self.assertIsInstance(schema['b'], FunctionProperty)
        self.assertIsInstance(schema['b'], PythonFunctionProperty)

        self.assertEqual(schema['b'](test, [2]), 2)
        self.assertEqual(schema['b'](test, None, {'b': 2}), 2)

        self.assertEqual(len(schema), 2)

        self.assertNotIn('c', schema)

        Test.c = schema

        schema = getschema(Test)

        self.assertIsInstance(schema, ClassSchema)

        self.assertIsInstance(schema['a'], Property)
        self.assertNotIsInstance(schema['a'], FunctionProperty)
        self.assertNotIsInstance(schema['a'], PythonFunctionProperty)

        self.assertIsInstance(schema['b'], Property)
        self.assertIsInstance(schema['b'], FunctionProperty)
        self.assertIsInstance(schema['b'], PythonFunctionProperty)

        self.assertIsInstance(schema['c'], Property)
        self.assertIsInstance(schema['c'], SchemaProperty)

        self.assertEqual(len(schema), 3)

        schema = getschema(Test, public=False)

        self.assertEqual(len(schema), len(dir(Test)))

if __name__ == '__main__':
    main()
