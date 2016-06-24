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

from ..reg import Registry, getbyname, register
from ..base import Schema


class RegistryTest(UTCase):

    def test(self):

        name = 'name'
        uid = 'uid'

        registry = Registry()

        self.assertRaises(KeyError, registry.getbyname, name=name)
        self.assertRaises(KeyError, registry.getbyname, uid=uid)

        schema = Schema('', name=name, uid=uid)
        registry.register(schema)

        schematest = registry.getbyname(name=name)
        self.assertIs(schematest, schema)
        schematest = registry.getbyname(uid=uid)
        self.assertIs(schematest, schema)

    def test_global(self):

        name = 'name'
        uid = 'uid'

        self.assertRaises(KeyError, getbyname, name=name)
        self.assertRaises(KeyError, getbyname, uid=uid)

        schema = Schema('', name=name, uid=uid)
        register(schema)

        schematest = getbyname(name=name)
        self.assertIs(schematest, schema)
        schematest = getbyname(uid=uid)
        self.assertIs(schematest, schema)


if __name__ == '__main__':
    main()
