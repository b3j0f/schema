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

"""Reference schema package."""

__all__ = ['RefSchema', 'uuidref']

from .core import Schema
from .registry import getbyuuid


class ReferenceSchema(Schema):
    """Handle reference to a schema."""

    ref = Schema()

    def getter(self, obj):

        return self.ref.getter(obj)

    def setter(self, obj, value):

        return self.ref.setter(obj, value)

    def deleter(self, obj):

        return self.ref.deleter(obj)

    def validate(self, data):

        return self.ref.validate(data)


def uuidref(refuuid, **kwargs):
    """Get a reference schema from a uuid.

    :param str refuuid: uuid of the refered schema.
    :rtype: RefSchema"""

    return Ref(ref=getbyuuid(uuid), **kwargs)
