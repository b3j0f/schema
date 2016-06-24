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

"""Schema registry module."""

__all__ = ['Registry', 'getbyname', 'register']


class Registry(object):
    """In charge of register schemas."""

    def __init__(self, schemas=None, *args, **kwargs):

        super(Registry, self).__init__(*args, **kwargs)

        self._schbyname = {}
        self._schbyuid = {}

        if schemas is not None:

            for schema in schemas:
                self.register(schema)

    def register(self, schema):
        """Register input schema.

        :param b3j0f.schema.Schema schema: schema to register."""

        if schema.uid is not None:
            self._schbyuid[schema.uid] = schema

        if schema.name is not None:
            self._schbyname.setdefault(schema.name, []).append(schema)

    def getbyname(self, name=None, uid=None):
        """Get a schema by given name or uid.

        :param str name: if uid is None, get the first schema using this name.
        :param str uid: schema uid to retrieve.
        :rtype: b3j0f.schema.Schema
        :raises: KeyError if name or uid not registered already.
        """

        if uid is not None:
            if uid not in self._schbyuid:
                raise KeyError('uid {0} not registered'.format(uid))

            result = self._schbyuid[uid]

        elif name is not None:
            if name not in self._schbyname:
                raise KeyError('name {0} not registered'.format(name))

            result = self._schbyname[name][0]

        return result

_REGISTRY = Registry()  #: global registry.


def register(schema):
    """Register globally input shema.

    :param b3j0f.schema.Schema: schema to register."""

    return _REGISTRY.register(schema)


def getbyname(name=None, uid=None):
    """Get globally a schema by given name or uid.

    :param str name: if uid is None, get the first schema using this name.
    :param str uid: schema uid to retrieve.
    :rtype: b3j0f.schema.Schema
    """

    return _REGISTRY.getbyname(name=name, uid=uid)
