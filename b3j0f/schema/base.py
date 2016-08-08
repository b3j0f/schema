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

from b3j0f.utils.version import getcallargs

from types import LambdaType

from inspect import getmembers, isclass

from six import get_unbound_function, add_metaclass

from uuid import uuid4

from .registry import register


class MetaSchema(type):
    """Automatically register schemas."""

    def __call__(cls, *args, **kwargs):

        result = super(MetaSchema, cls).__call__(*args, **kwargs)

        register(result)

        return result


@add_metaclass(MetaSchema)
class Schema(property):
    """Schema description.

    A schema is identified by a string such as an universal unique identifier,
    and optionnally a name.

    Any setted value respect those conditions in this order:
    1. if the value is a lambda expression, the value equals its execution.
    2. the value is validated with this method `validate`.
    3. the value is given to a custom setter (`fget` constructor parameter) if
        given or setted to this attribute `_value`.

    Once you defined your schema inheriting from this class, your schema will be
    automatically registered in the registry and becomes accessible from the
    `b3j0f.schema.reg.getschemabyuid` function."""

    name = ''  #: schema name. Default is self name.
    uuid = lambda: uuid4()  #: schema universal unique identifier.
    description = ''  #: schema description.
    default = None  #: schema default value.
    required = lambda: []  #: required schema names.
    version = '1'  #: schema version.

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        """Instance attributes are setted related to arguments or inner schemas.

        :param default: default value. If lambda, called at initialization.
        """

        super(Schema, self).__init__(
            fget=self._getter, fset=self._setter, fdel=self._deleter, doc=doc
        )

        # set all init parameters to related inner schema
        callargs = getcallargs(self.__init__, self, **kwargs)

        for name, schema in self.schemas():
            if name in callargs:
                val = callargs[name]
                setattr(self, name, val)

        self._fget = fget
        self._fset = fset
        self._fdel = fdel

        # set default value
        self._value = None

    def __eq__(self, other):
        """Compare schemas."""

        return other is self or self.schemas() == other.schemas()

    def _getter(self, obj, *args, **kwargs):
        """Called when the parent element tries to get this property value."""

        result = None

        if self._fget is not None:
            result = self._fget(obj)

        if result is None:
            result = self._value

        return result

    def _setter(self, obj, value):
        """Called when the parent element tries to set this property value.

        :param value: new value to use. If lambda, updated with the lambda
            result."""

        if isinstance(value, LambdaType):  # execute lambda values.
            value = value()

        self.validate(value)

        if self._fset is not None:
            self._fset(obj, value)

        else:
            self._value = value

    def _deleter(self, obj):
        """Called when the parent element tries to delete this property value.
        """

        if self._fdel is not None:
            self._fdel(obj)

        else:
            del self._value

    def validate(self, data):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :raises: Exception if the data is not validated"""

        if not isinstance(data, type(self)):
            raise TypeError(
                'Wrong type {0}. {1} expected'.format(data, self)
            )

        for name, schema in self.schemas():
            if name in self.required and not hasattr(data, name):
                part1 = ('Mandatory schema {0} by {1} is missing in {2}.'.
                    format(name, self, data)
                )
                part2 = '{3} expected.'.format(schema)
                error = '{0} {1}'.format(part1, part2)
                raise ValueError(error)

            elif hasattr(data, name):
                schema.validate(getattr(data, name))

    def dump(self):
        """Get a serialized value of this schema.

        :rtype: dict"""

        result = {}

        for name, schema in self.schemas():
            val = schema.dump()

            result[name] = val

        return result

    @classmethod
    def schemas(cls):
        """Get inner schemas by name."""

        return getmembers(cls, lambda member: isinstance(member, Schema))
