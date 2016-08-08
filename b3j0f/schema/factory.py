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
"""Schema factory module."""

__all__ = ['SchemaFactory', 'registermaker', 'unregistermaker', 'getschema']

from uuid import uuid4 as uuid

from six import string_types


class SchemaFactory(object):
    """Factory dedicated to generate schemas.

    Keys are schema maker names, and values are schema makers."""

    def __init__(self, makers=None, schemasbyresource=None, *args, **kwargs):

        super(SchemaFactory, self).__init__(*args, **kwargs)

        self._schemasbyresource = schemasbyresource or {}
        self._makers = makers or {}

    def registermaker(self, maker=None, name=None):
        """Register a schema maker with a key name.

        :param str name: maker name. Default is maker name or generated.
        :param maker: callable object which takes in parameter a schema resource
            and generate a schema class in return. If the resource is not in the
            right format, the maker must raise a TypeError exception."""

        def _register(
                maker, name=maker if isinstance(maker, string_types) else name
        ):

            if name is None:
                name = getattr(maker, '__name__', uuid())

            self._makers[name] = maker

            return maker

        if maker is None:
            return _register

        elif isinstance(maker, string_types):
            return _register

        else:
            return _register(maker)

    def unregistermaker(self, name):
        """Unregister a maker by its name.

        :param str name: maker name to remove.
        :raises: KeyError if name is not registered."""

        del self._makers[name]

    @property
    def makers(self):
        """Get maker names.

        :rtype: list"""

        return list(self._makers.keys())

    def getschema(self, resource, cache=True):
        """Get a schema from input resource.

        :param resource: object from where get the right schema.
        :param bool cache: use cache system.
        :rtype: Schema."""

        result = None

        if cache and resource in self._schemasbyresource:
            result = self._schemasbyresource[resource]

        else:
            for maker in self._makers.values():
                try:
                    result = maker(resource)

                except TypeError:
                    pass

        if result is None:
            raise TypeError('No maker found for {0}'.format(resource))

        if cache:
            self._schemasbyresource[resource] = result

        return result

_SCHEMAFACTORY = SchemaFactory()  #: global schema factory


def registermaker(maker, name=None):
    """Register a schema maker.

    :param str name: maker name. Default is maker name or generated.
    :param maker: callable object which takes in parameter a schema resource
        and generate a schema class in return. If the resource is not in the
        right format, the maker must raise a TypeError exception."""

    return _SCHEMAFACTORY.registermaker(name=name, maker=maker)


def unregistermaker(name):
    """Unregister a maker by its name.

    :param str name: maker name to remove.
    :raises: KeyError if name is not registered."""

    return _SCHEMAFACTORY.unregistermaker(name=name)

def getschema(resource, cache=True):
    """Get a schema from input resource.

    :param resource: object from where get the right schema.
    :param bool cache: use cache system.
    :rtype: Schema."""

    return _SCHEMAFACTORY.getschema(resource=resource, cache=True)
