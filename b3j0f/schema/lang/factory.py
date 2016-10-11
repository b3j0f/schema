# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""Schema factory module."""

from uuid import uuid4 as uuid

from six import add_metaclass

from inspect import isclass

__all__ = [
    'SchemaFactory', 'registerbuilder', 'unregisterbuilder', 'build',
    'getbuilder', 'getschemacls', 'getresource', 'SchemaBuilder'
]


class SchemaFactory(object):
    """Factory dedicated to generate schemas.

    Keys are schema builder names, and values are schema builders.
    """

    def __init__(self, builders=None, schemasbyresource=None, *args, **kwargs):

        super(SchemaFactory, self).__init__(*args, **kwargs)

        self._schemasbyresource = schemasbyresource or {}
        self._builders = builders or {}

    def registerbuilder(self, builder, name=None):
        """Register a schema builder with a key name.

        Can be used such as a decorator where the builder can be the name for a
        short use.

        :param SchemaBuilder builder: schema builder.
        :param str name: builder name. Default is builder name or generated.
        """
        if name is None:
            name = uuid()

        self._builders[name] = builder

        return builder

    def unregisterbuilder(self, name):
        """Unregister a builder by its name.

        :param str name: builder name to remove.
        :raises: KeyError if name is not registered.
        """
        del self._builders[name]

    @property
    def builders(self):
        """Get builder names.

        :rtype: list
        """
        return list(self._builders.keys())

    def getbuilder(self, name):
        """Get a builder instance from a name.

        :param str name: builder name to retrieve.
        """
        return self._builders[name]

    def build(self, _resource, _cache=True, **kwargs):
        """Build a schema class from input _resource.

        :param _resource: object from where get the right schema.
        :param bool _cache: use _cache system.
        :rtype: Schema.
        """
        result = None

        if _cache and _resource in self._schemasbyresource:
            result = self._schemasbyresource[_resource]

        else:
            for builder in self._builders.values():
                try:
                    result = builder.build(_resource=_resource, **kwargs)

                except Exception:
                    pass

                else:
                    break

        if result is None:
            raise ValueError('No builder found for {0}'.format(_resource))

        if _cache:
            self._schemasbyresource[_resource] = result

        return result

    def getschemacls(self, resource, besteffort=True):
        """Get schema class related to input resource.

        :param resource: resource from which get schema class.
        :param bool besteffort: if True (default) try a best effort in parsing
            the inheritance tree of resource if resource is a class.
        :rtype: type
        """
        result = None

        resources = (
            resource.mro() if besteffort and isclass(resource) else [resource]
        )

        for _resource in resources:
            if _resource in self._schemasbyresource:
                result = self._schemasbyresource[_resource]

                break

        return result

    def getresource(self, schemacls, name):
        """Get a resource from a builder name.

        :param type schemacls: waited schema class.
        :param str name: builder name to use.
        :return: resource returned by the right builder.getresource(schema).
        """
        return self.builders[name].getresource(schemacls=schemacls)

_SCHEMAFACTORY = SchemaFactory()  #: global schema factory


def registerbuilder(builder, name=None):
    """Register a schema builder.

    :param str name: builder name. Default is builder name or generated.
    :param builder: callable object which takes in parameter a schema resource
        and generate a schema class in return. If the resource is not in the
        right format, the builder must raise a TypeError exception.
    """
    return _SCHEMAFACTORY.registerbuilder(name=name, builder=builder)


def unregisterbuilder(name):
    """Unregister a builder by its name.

    :param str name: builder name to remove.
    :raises: KeyError if name is not registered.
    """
    return _SCHEMAFACTORY.unregisterbuilder(name=name)


def build(_resource, _cache=True, **kwargs):
    """Build a schema from input _resource.

    :param _resource: object from where get the right schema.
    :param bool _cache: use cache system.
    :rtype: Schema.
    """
    return _SCHEMAFACTORY.build(_resource=_resource, _cache=True, **kwargs)


def getbuilder(name):
    """Get a builder instance from a name.

    :param str name: builder name to retrieve.
    """
    return _SCHEMAFACTORY.getbuilder(name)


def getschemacls(resource, besteffort=False):
    """Get schema class related to input resource.

    :param resource: resource from which get schema class.
    :param bool besteffort: if True (default) try a best effort in parsing
            the inheritance tree of resource if resource is a class.
    :rtype: type
    """
    return _SCHEMAFACTORY.getschemacls(
        resource=resource, besteffort=besteffort
    )


def getresource(self, schemacls, name):
    """Get a resource from a builder name.

    :param type schemacls: waited schema class.
    :param str name: builder name to use.
    :return: resource returned by the right builder.getresource(schema).
    """
    return _SCHEMAFACTORY.getresource(schemacls=schemacls, name=name)


class MetaSchemaBuilder(type):

    def __new__(cls, *args, **kwargs):

        result = super(MetaSchemaBuilder, cls).__new__(cls, *args, **kwargs)

        if result.__register__:
            registerbuilder(result(), name=result.__name__ or result.__name__)

        return result


@add_metaclass(MetaSchemaBuilder)
class SchemaBuilder(object):
    """Schema builder interface for building schema from a resource, and
    reciprocally.
    """

    __register__ = True  #: if True (default), automatically register this.
    __name__ = None  #: schema builder name. Default is generated.

    def build(self, _resource, **kwargs):
        """Build a schema class from input resource."""
        raise NotImplementedError()

    def getresource(self, schemacls):
        """Get a schema resource from input schema."""
        raise NotImplementedError()
