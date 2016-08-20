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

from ..utils import DynamicValue, obj2schema, This
from ..registry import registercls


class DynamicValueTest(UTCase):

    def test(self):

        dvalue = DynamicValue(lambda: 'test')

        self.assertEqual('test', dvalue())


class FromObjTest(UTCase):

    class BaseTest(object):

        def __init__(self, default=None, *args, **kwargs):

            super(FromObjTest.BaseTest, self).__init__(*args, **kwargs)
            self.default = default

    class Test(BaseTest):
        pass

    def setUp(self):

        registercls(FromObjTest.BaseTest, [FromObjTest.BaseTest])

    def test_default(self):

        self.assertIsNone(obj2schema(True))

    def test_default_force(self):

        self.assertRaises(TypeError, obj2schema, True, _force=True)

    def test_default_besteffort(self):

        self.assertIsNone(obj2schema(True, _besteffort=False))

    def test_dynamicvalue(self):

        self.assertIsNone(obj2schema(DynamicValue(lambda: True)))

    def test_registered(self):

        test = FromObjTest.Test()
        res = obj2schema(test)

        self.assertEqual(res.default, test)

    def test_registered_besteffort(self):

        test = FromObjTest.Test()
        res = obj2schema(test, _besteffort=False)

        self.assertIsNone(res)


class ThisTest(UTCase):

    def test(self):

        this = This(1, 2, a=3, b=4)

        self.assertEqual(this.args, (1, 2))
        self.assertEqual(this.kwargs, {'a': 3, 'b': 4})

if __name__ == '__main__':
    main()
