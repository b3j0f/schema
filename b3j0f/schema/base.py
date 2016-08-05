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

"""Base schema package."""

__all__ = ['MetaSchema', 'Schema']

from six import add_metaclass, string_types

from b3j0f.utils.version import getcallargs
from b3j0f.conf import Configurable

from .registry import register
from .factory import
from .prop import Property

from inspect import getmembers, getargspec

from numbers import Number


class MetaSchema(type):
    """Automatically register schemas."""

    def __call__(mcs, *args, **kwargs):

        result = super(MetaSchema, mcs).__call__(*args, **kwargs)

        register(result)

        return result


@add_metaclass(MetaSchema)
class Schema(object):
    """Base class for schema.

    It has a unique identifier (UID) and instanciates data objects.

    Its name is its class name.

    Once you defined your schema inheriting from this class, your schema will be
    automatically registered in the registry and becomes accessible from the
    `b3j0f.schema.reg.getschemabyuid` function."""

    uid = '/schema'  #: unique schema identifier.
    required = []  #: required innerschema names.
    default = None  #: default value for this schema.

    def __init__(self, *args, **kwargs):
        """Instance attributes are setted related to arguments or inner schemas.
        """

        callargs = getcallargs(self.__init__, self, *args, **kwargs)

        for name, schema in getmembers(
            type(self), lambda member: issubclass(member, Schema)
        ):

            val = callargs.get(name, schema())

            setattr(self, name, val)

    @classmethod
    def validate(cls, data):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :raises: Exception if the data is not validated"""

        if not isinstance(data, self):
            raise TypeError(
                'Wrong type {0}. {1} expected'.format(data, self)
            )

        for name, schema in getmembers(
            cls, lambda member: issubclass(member, Schema)
        ):

            if name in cls.REQUIRED and not hasattr(data, name):
                error = 'Mandatory property {0} by {1} is missing in {2}. {3} expected.'.format(
                    name, cls, data, schema
                )
                raise ValueError(error)

            elif hasattr(data, name):
                schema.validate(getattr(data, name))

        return result

    @classmethod
    def innerschemas(cls):
        """Get all inner schemas."""

        return getmembers(cls, lambda member: issubclass(Schema))


baseschema = classschemamaker(Schema)
register(baseschema)
