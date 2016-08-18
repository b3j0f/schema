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
from b3j0f.utils.path import getpath

from ...base import Schema
from ..python import clsschemamaker, functionschemamaker

from inspect import getmembers


class CLSSchemaMakerTest(UTCase):

    def test_default(self):

        @clsschemamaker
        class Test(object):
            pass

        self.assertEqual(Test.getschemas(), Schema.getschemas())

    def test_schema(self):

        @clsschemamaker
        class Test(Schema):
            pass

        self.assertEqual(Test.getschemas(), Schema.getschemas())

    def test_innergetschemas(self):

        @clsschemamaker
        class Test(object):

            a = Schema()

        self.assertNotEqual(Test.getschemas(), Schema.getschemas())

        schemas = Test.getschemas()

        self.assertEqual(Test.getschemas()[0][0], 'a')

    def test_innerschemas_schema(self):

        @clsschemamaker
        class Test(Schema):

            a = Schema()

        self.assertNotEqual(Test.getschemas(), Schema.getschemas())

        schemas = Test.getschemas()

        self.assertEqual(Test.getschemas()[0][0], 'a')

if __name__ == '__main__':
    main()