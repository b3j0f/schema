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
    'SchemaRegistry',
    'getbyuuid', 'getbyname', 'register', 'unregister', 'fromobj',
    'getschemasbyuuid', 'registercls', 'unregistercls', 'getbydatatype'
]

from .factory import make

from six import iteritems

#: class attribute for Schema data_type association
__DATA_TYPES__ = '__data_types__'


class SchemaRegistry(object):
    """In charge of register schemas."""

    def __init__(
            self,
            schemas=None, schbyname=None, schbyuuid=None, schbytype=None,
            *args, **kwargs
    ):
        """
        :param list schemas: starting schemas to register.
        :param dict schbyname: schemas by name.
        :param dict schyuid: schemas by uuid.
        :param dict schbytype: schemas by type.
        """

        super(SchemaRegistry, self).__init__(*args, **kwargs)

        self._schbyname = schbyname or {}
        self._schbyuuid = schbyuuid or {}
        self._schbytype = schbytype or {}

        if schemas:
            for schema in schemas:
                self.register(schema=schema)

    def getschemasbyuuid(self):
        """Get all schemas by uuid.

        :rtype: dict"""

        return dict(self._schbyuuid)

    def register(self, schema):
        """Register input schema class.

        When registering a schema, all inner schemas are registered as well.

        :param Schema schema: schema to register.
        :return: old registered schema.
        :rtype: type"""

        result = None

        uuid = schema.uuid

        if uuid in self._schbyuuid:
            result = self._schbyuuid[uuid]

        if result != schema:

            self._schbyuuid[uuid] = schema

            name = schema.name

            schemas = self._schbyname.setdefault(name, set())

            schemas.add(schema)

            for innername, innerschema in iteritems(schema.schemas()):

                if innerschema.uuid not in self._schbyuuid:
                    register(innerschema)

        return result

    def registercls(self, schemacls, data_types):
        """Register schema class with associated data_types.

        :param type schemacls: schema class to register.
        :param list data_types: data types to associate with schema class.
        """

        for data_type in data_types:
            self._schbytype[data_type] = schemacls

    def fromobj(self, obj, _force=False, _besteffort=True, *args, **kwargs):
        """Get the schema able to instanciate input object.

        The default value of schema will be obj.

        :param obj: object possibly generated by a schema.
        :param bool _force: if True (False by default), create the object schema
            on the fly if it does not exist.
        :param bool _besteffort: if True (default), find a schema class able to
            validate object class by inheritance.
        :param args: schema class vargs.
        :param kwargs: schema class kwargs.
        :return: Schema.
        :rtype: Schema."""

        result = None

        cls = type(obj)

        schemacls = self.getbydatatype(cls, besteffort=_besteffort)

        if schemacls is None and _force:
            schemacls = make(cls)

        if schemacls:
            result = schemacls(default=obj, *args, **kwargs)

        return result

    def unregister(self, uuid):
        """Unregister a schema registered with input uuid.

        :raises: KeyError if uuid is not already registered."""

        schema = self._schbyuuid.pop(uuid)

        # clean schemas by name
        self._schbyname[schema.name].remove(schema)
        if not self._schbyname[schema.name]:
            del self._schbyname[schema.name]

    def unregistercls(self, schemacls=None, data_types=None):
        """Unregister schema class or associated data_types.

        :param type schemacls: sub class of Schema.
        :param list data_types: data_types to unregister."""

        if schemacls is not None:

            # clean schemas by data type
            for data_type in list(self._schbytype):
                _schemacls = self._schbytype[data_type]
                if _schemacls is schemacls:
                    del self._schbytype[data_type]

        if data_types is not None:

            for data_type in data_types:
                if data_type in self._schbytype:
                    del self._schbytype[data_type]

    def getbyuuid(self, uuid):
        """Get a schema by given uuid.

        :param str uuid: schema uuid to retrieve.
        :rtype: Schema
        :raises: KeyError if uuid is not registered already."""

        if uuid not in self._schbyuuid:
            raise KeyError('uuid {0} not registered'.format(uuid))

        return self._schbyuuid[uuid]

    def getbyname(self, name):
        """Get schemas by given name.

        :param str name: schema names to retrieve.
        :rtype: list
        :raises: KeyError if name is not registered already."""

        if name not in self._schbyname:
            raise KeyError('name {0} not registered'.format(name))

        return self._schbyname[name]

    def getbydatatype(self, data_type, besteffort=True):
        """Get schema class by data type.

        :param type data_type: data type from where get schema class.
        :param bool besteffort: if True and data_type not registered, parse all
            registered data_types and stop when once data_type is a subclass of
            input data_type.
        :return: sub class of Schema.
        :rtype: type
        """

        result = None

        if data_type in self._schbytype:
            result = self._schbytype[data_type]

        elif besteffort:
            for rdata_type in self._schbytype:
                if issubclass(data_type, rdata_type):
                    result = self._schbytype[rdata_type]
                    break

        return result


_REGISTRY = SchemaRegistry()  #: global Schemaregistry.


def register(schema):
    """Register globally input shema.

    :param b3j0f.schema.Schema: schema to register."""

    return _REGISTRY.register(schema=schema)


def fromobj(obj, _force=False, _besteffort=True, *args, **kwargs):
    """Get the schema able to instanciate input object.

    The default value of schema will be obj.

    :param obj: object possibly generated by a schema.
    :param bool _force: if True (False by default), create the object schema
        on the fly if it does not exist.
    :param bool _besteffort: if True (default), find a schema class able to
        validate object class by inheritance.
    :param args: schema class vargs.
    :param kwargs: schema class kwargs.
    :return: Schema.
    :rtype: Schema."""

    return _REGISTRY.fromobj(
        obj, _force=_force, _besteffort=_besteffort, *args, **kwargs
    )


def unregister(uuid):
    """Unregister"""

    return _REGISTRY.unregister(uuid=uuid)


def getbyuuid(uuid):
    """Get globally a schema by given uuid.

    :param str uuid: schema uuid to retrieve.
    :rtype: type
    :raises: KeyError if name is not registered already."""

    return _REGISTRY.getbyuuid(uuid=uuid)


def getbyname(name):
    """Get globally a schema by given name.

    :param str name: schema names to retrieve.
    :rtype: list
    :raises: KeyError if name is not registered already."""

    return _REGISTRY.getbyname(name=name)


def getschemasbyuuid():
        """Get all schemas by uuid.

        :rtype: dict"""

        return _REGISTRY.getschemasbyuuid()


def getbydatatype(self, data_type):
    """Get schema by type.

    :param type data_type: data type from where get schema class.
    :return: sub class of Schema.
    :rtype: type
    """

    return _REGISTRY.getbydatatype(data_type=data_type)


def registercls(schemacls, data_types):
    """Register schema class with associated data_types.

    :param type schemacls: schema class to register.
    :param list data_types: data types to associate with schema class.
    """

    return _REGISTRY.registercls(schemacls=schemacls, data_types=data_types)


def unregistercls(self, schemacls=None, data_types=None):
    """Unregister schema class or associated data_types.

    :param type schemacls: sub class of Schema.
    :param list data_types: data_types to unregister."""

    return _REGISTRY.unregistercls(schemacls=schemacls, data_types=data_types)
