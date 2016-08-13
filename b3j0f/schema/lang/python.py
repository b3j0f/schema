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

from ..factory import registermaker, getschemacls
from ..base import Schema


@registermaker
def clsschemamaker(resource, name=None):
    """Default function which make a schema class from a resource.

    :param type resource: input resource is a class.
    :param str name: schema type name to use. Default is resource name.
    :param type schemacls: sub class of schema to inherit from.
    :rtype: type
    :raise: TypeError if resource is not a class."""

    if not isinstance(resource, type):
        raise TypeError('Wrong type {0}, \'type\' expected'.format(resource))

    if issubclass(resource, Schema):
        result = resource

    else:
        try:
            result = getschemacls(resource)

        except KeyError:
            resname = resource.__name__ if name is None else name
            result = type(resname, (Schema, resource), {})

    return result
