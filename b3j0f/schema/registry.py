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

__all__ = [
    'Registry', 'getbyuid', 'getbyname', 'register', 'unregister', 'fromobj'
]


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
        """Register input schema class.

        When registering a schema, all inner schemas are registered as well.

        :param type schema: schema to register.
        :return: old registered schema.
        :rtype: type"""

        result = None

        uid = schema.UID

        if uid in self._schbyuid:
            result = self._schbyuid[uid]

        if result is not schema:

            self._schbyuid[uid] = schema

            name = schema.__name__

            schemas = self._schbyname.setdefault(schema.__name__, set())

            schemas.add(schema)

            for name, innerschema in schema.innerschemas():

                if innerschema.UID not in self._schbyuid:
                    register(innerschema)

        return result

    def unregister(self, uid):
        """Unregister a schema registered with input uid.

        :raises: KeyError if uid is not already registered."""

        schema = self._schbyuid.pop(uid)

        self._schbyname[schema.__name__].remove(schema)

    def getbyuid(self, uid):
        """Get a schema by given uid.

        :param str uid: schema uid to retrieve.
        :rtype: type
        :raises: KeyError if uid is not registered already."""

        if uid not in self._schbyuid:
            raise KeyError('uid {0} not registered'.format(uid))

        return self._schbyuid[uid]

    def getbyname(self, name):
        """Get schemas by given name.

        :param str name: schema names to retrieve.
        :rtype: list
        :raises: KeyError if name is not registered already."""

        if name not in self._schbyname:
            raise KeyError('name {0} not registered'.format(name))

        return self._schbyname[name]


_REGISTRY = Registry()  #: global registry.


def register(schema):
    """Register globally input shema.

    :param b3j0f.schema.Schema: schema to register."""

    return _REGISTRY.register(schema)


def unregister(uid):
    """Unregister"""

    return _REGISTRY.unregister(uid=uid)


def getbyuid(uid):
    """Get globally a schema by given uid.

    :param str uid: schema uid to retrieve.
    :rtype: type
    :raises: KeyError if name is not registered already."""

    return _REGISTRY.getbyuid(uid=uid)


def getbyname(name):
    """Get globally a schema by given name.

    :param str name: schema names to retrieve.
    :rtype: list
    :raises: KeyError if name is not registered already."""

    return _REGISTRY.getbyname(name=name)
