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

from __future__ import absolute_import, unicode_literals

from unittest import main

from b3j0f.utils.ut import UTCase

from json import dumps

from ..json import JSONSchemaBuilder, _SCHEMASBYJSONNAME, _PARAMSBYNAME
from ...base import Schema
from ..factory import build


class JSONSchemaTest(UTCase):

    def setUp(self):

        self.builder = JSONSchemaBuilder()

    def test_default(self):

        resource = '{"id": "test", "property": {}, "title": "title"}'

        schema = self.builder.build(resource)

        self.assertTrue(issubclass(schema, Schema))

    def test_elementaries(self):

        resource = {'id': 'test', 'title': 'title'}

        for rtype, stype in _SCHEMASBYJSONNAME.items():

            fresource = resource.copy()
            fresource['type'] = rtype

            sresource = dumps(fresource)

            schema = self.builder.build(sresource)

            self.assertTrue(issubclass(schema, stype))

    def _test_composite(self):

        resource = {
            'type': 'object',
            'title': 'test',
            'id': 'uuid',
            'properties': {
                '': {
                        'type': 'integer',
                        'title': 'example'
                },
                'test': {
                        'type': 'boolean'
                }
            }
        }

        json = dumps(resource)

        schemacls = self.builder.build(json)

        self.assertTrue(
            issubclass(schemacls, _SCHEMASBYJSONNAME[resource['type']])
        )
        self.assertEqual(schemacls.__name__, resource['title'])

        self.assertIsInstance(
            schemacls.test,
            _SCHEMASBYJSONNAME[resource['properties']['test']['type']]
        )
        self.assertIsInstance(
            schemacls.example,
            _SCHEMASBYJSONNAME[resource['properties']['']['type']]
        )
        self.assertFalse(hasattr(schemacls.example))

if __name__ == '__main__':
    main()
