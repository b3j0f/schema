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
from .cls import clsschemamaker

from inspect import getmembers, getargspec


class MetaSchema(type):
    """Automatically register schemas."""

    def __new__(mcs, *args, **kwargs):

        result = super(MetaSchema, mcs).__new__(mcs, *args, **kwargs)

        register(result, data_type=getattr(result, 'data_type', None))

        return result


@add_metaclass(MetaSchema)
class Schema(property):
    """Schema description.

    It has a unique identifier (UID) and instanciates data objects.

    Its name is its class name.

    Once you defined your schema inheriting from this class, your schema will be
    automatically registered in the registry and becomes accessible from the
    `b3j0f.schema.reg.getschemabyuid` function."""

    def __init__(self, title=None, name=None, uid=None, description=None, **kwargs):
        """Instance attributes are setted related to arguments or inner schemas.
        """

        super(Schema, self).__init__(
            fget=self.getter, fset=self.setter, fdel=self.deleter,
            doc=kwargs.get('description', type(self).description)
        )

        self._fget = kwargs.get('fget')
        self._fset = kwargs.get('fset')
        self._fdel = kwargs.get('fdel')

        self._value = None  # this value for parent schema.

        callargs = getcallargs(self.__init__, self, *args, **kwargs)

        for name, schema in getmembers(
            type(self), lambda member: issubclass(member, Schema)
        ):

            val = callargs.get(name, schema())

            setattr(self, name, val)

    def getter(self, obj):
        """Called when the parent element tries to get this property value.

        :param obj: parent element."""

        result = None

        if self._fget is not None:
            result = self._fget(obj, cls)

        if result is None:
            result = self._value

        return result

    def setter(self, obj, value):
        """Called when the parent element tries to set this property value.

        :param obj: parent element.
        :param value: new value to use."""

        if self.validate(value):

            if self._fset is not None:
                self._fset(obj, value)

            else:
                self._value = value

        else:
            raise ValueError('{0} does not match with {1}'.format(value, self))

    def deleter(self, obj):
        """Called when the parent element tries to delete this property value.

        :param obj: parent element."""

        if self._fdel is not None:
            self._fdel(obj)

        else:
            del self._value

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

            if name in cls.required and not hasattr(data, name):
                error = 'Mandatory property {0} by {1} is missing in {2}. {3} expected.'.format(
                    name, cls, data, schema
                )
                raise ValueError(error)

            elif hasattr(data, name):
                schema.validate(getattr(data, name))

        return result

    @classmethod
    def schemas(cls):
        """Get all inner schemas."""

        return getmembers(cls, lambda member: issubclass(Schema))

    def properties(self):
        """Get all inner properties."""

        return getmembers(self, lambda member: isinstance(Schema))

    @classmethod
    def apply(cls, fget=None, **kwargs):
        """Property decorator to use in order to decorate schema attributes."""

        callargs = getcallargs(cls.apply, fget=fget, **kwargs)

        # decorator without parameters.
        if fget is not None:
            return cls(fget=fget, **kwargs)

        else:  # decorator with parameters.
            def _schema(fget):
                """result function if apply has arguments."""

                return cls(fget=fget, **kwargs)

            return _schema


register(clsschemamaker(Schema), data_types=[Schema])
