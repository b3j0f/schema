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

__all__ = ['registermaker', 'getschema', 'schemamaker']

from inspect import getmembers, isroutine


_SCHEMASBYRESOURCE = {}

_MAKERS = []


def registermaker(maker):
    """Register a schema maker.

    :param maker: callable object which takes in parameter a schema resource
        and generate a schema class in return. If the resource is not in the
        right format, the maker must raise a TypeError exception."""

    _MAKERS.append(maker)


def getschema(resource, cache=True):
    """Get a schema from input resource.

    :param resource: object from where get the right schema."""

    if cache and resource in _SCHEMASBYRESOURCE:
        result = _SCHEMASBYRESOURCE[resource]

    else:

        for maker in _MAKERS:
            try:
                result = maker(resource)

            except TypeError:
                pass

    if cache:
        _SCHEMASBYRESOURCE[resource] = result

    return result


@registermaker
def clsschemamaker(resource):
    """Default function which make a schema class from a resource.

    :param type resource: input resource is a class.
    :raise: TypeError if resource is not a class."""

    if not isinstance(resource, type):
        raise TypeError('Wrong type {0}, \'type\' expected'.format(resource))

    name = resource.__name__
    bases = resource.mro() + [Schema]
    _dict = {}

    for name, member in getmembers(resource):

        if isroutine(member):
            _dict[name] = FunctionProperty(member)

        else:
            _dict[name] = Property(member)

    return type(name, bases, _dict)


def objectschemamaker(resource):
    """Make a schema from an object."""

    return clsschemamaker(type(object))


def functionmaker(resource):

    return objectschemamaker()


schemamaker(type(schemamaker))  # auto
