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

from ..base import Schema, getschema
from ..prop import Property as P


class SchemaTest(UTCase):

    def test_getschema(self):

        self.assertRaises(ValueError, getschema, '')

        class TestSchema(Schema):
            pass

        resource = 'resource'

        schema = getschema(resource)

        self.assertEqual(schema.resource, resource)

    def test_init(self):

        schema = Schema('')

        self.assertIsNone(schema.name)
        self.assertIsNone(schema.uid)
        self.assertIsNone(schema.ids)
        self.assertIsNone(schema.pids)

        schema = Schema(
            '',
            name='a', uid='b', ids=['a', 'b'], properties=[P('a'), P('b')]
        )

        self.assertEqual(schema.name, 'a')
        self.assertEqual(schema.uid, 'b')
        self.assertEqual(schema.ids, ['a', 'b'])
        self.assertEqual(schema.pids, [schema['a'], schema['b']])

if __name__ == '__main__':
    main()