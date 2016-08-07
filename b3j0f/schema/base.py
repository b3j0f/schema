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

__all__ = ['MetaSchema', 'BaseSchema']

from six import add_metaclass, string_types

from b3j0f.utils.version import getcallargs
from b3j0f.conf import Configurable

from types import LambdaType

from .registry import register
from .cls import clsschemamaker

from inspect import getmembers, getargspec


class MetaSchema(type):
    """Automatically register schemas."""

    def __call__(cls, *args, **kwargs):

        result = super(MetaSchema, cls).__call__(*args, **kwargs)

        register(result)

        return result


@add_metaclass(MetaSchema)
class BaseSchema(property):
    """Schema description.

    A schema is an object where attributes are properties and implement such
    methods:

    - __init__: takes in parameters schema properties,
    - __call__: takes in parameters schema properties
    -  properties with required name or uid,
    such methods:

    .. csv-table::
        name, description

        __iter__, "iterator on sub schema names".
        __call__, "takes instanciate a new data"

    - the __call__ method which instanciates a new data checking the schema.
    - the
    It has a unique identifier (UID) and instanciates data objects.

    Its name is its class name.

    Once you defined your schema inheriting from this class, your schema will be
    automatically registered in the registry and becomes accessible from the
    `b3j0f.schema.reg.getschemabyuid` function."""

    default = BaseSchema(
        fget=lambda obj: self._value() if isinstance(self._value, LambdaType)
            else self._value
    )

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        """Instance attributes are setted related to arguments or inner schemas.

        :param default: default value. If lambda, called at initialization.
        """

        super(Schema, self).__init__(
            fget=self.getter, fset=self.setter, fdel=self.deleter, doc=doc
        )

        # set all init parameters to related schema properties
        callargs = getcallargs(self.__init__, self, **kwargs)

        for name, schema in self.properties:
            if name in callargs:
                setattr(self, name, val)

        self._fget = fget
        self._fset = fset
        self._fdel = fdel

        # set default value
        self._value = None
        self._value = self.default

    def __eq__(self, other):
        """Compare properties."""

        return other is self or self.properties == other.properties

    @property
    def default(self):
        """Get this default value."""

        return (
            self._default()
            if isinstance(self._default, LambdaType)
            else self._default
        )

    @property
    def properties(self):
        """Get inner properties by name."""

        return getmembers(self, lambda member: isinstance(member, BaseSchema))

    def getter(self, obj):
        """Called when the parent element tries to get this property value.

        :param obj: parent element."""

        result = None

        if self._fget is not None:
            result = self._fget(obj)

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

    def validate(self, data):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :raises: Exception if the data is not validated"""

        if not isinstance(data, self):
            raise TypeError(
                'Wrong type {0}. {1} expected'.format(data, self)
            )

    def dump(self):
        """Get a serialized value of this schema.

        :rtype: dict"""

        result = {}

        for name, prop in self.properties:
            val = prop.dump()

            result[name] = val

        return result

    @classmethod
    def schemas(cls):
        """Get inner schemas by name."""

        return getmembers(cls, lambda member: issubclass(member, Schema))
