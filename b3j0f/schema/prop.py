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

"""Schema property package."""

__all__ = ['Property', 'ArrayProperty', 'FunctionProperty', 'SchemaProperty']


from numbers import Number

from six import string_types, exec_

from collections import Iterable

from functools import wraps

from inspect import getvarargs

from random import randint

from sys import maxsize

from .factory import getschema


def schema(fget=None, *args, **kwargs):
    """Decorator to use in order to decorate schema classes.

    :param fget: Property fget argument.
    :param args: Property args.
    :param kwargs: Property kwargs."""

    if (not args) and (not kwargs):  # decorator without parameters.
        return Property(fget=fget)

    else:  # decorator with parameters.
        def _sproperty(fget):
            return Property(fget=fget, *args, **kwargs)

        return _sproperty


class Property(property):
    """Schema property"""

    def __init__(
            self, fget=None, fset=None, fdel=None,
            schema=None, default=None,
            *args, **kwargs
    ):
        """
        :param str name: property name.
        :param type ptype: property type.
        :param type schema: schema.
        :param default: default value.
        :param bool mandatory: mandatory property characteristic.
        """

        super(Property, self).__init__(
            fget=self._get, fset=self._set, fdel=self._del, *args, **kwargs
        )

        self._fget = fget
        self._fset = fset
        self._fdel = fdel

        self.default = default
        self.mandatory = mandatory
        self.schema = schema

        self.name = getattr(
            fget, '__name__', '_{0}'.format(str(randint(-maxsize, maxsize)))
        )

    @property
    def attrname(self):
        return '_{0}'.format(self.name)

    def _get(self, obj, cls):

        result = None

        if self._fget is not None:
            result = self._fget(obj, cls)

        if result is None:
            result = getattr(obj, self.attrname)

        return result

    def _set(self, obj, value):

        if self.validate(value):

            if self._fset is not None:
                self._fset(obj, value)

            else:
                setattr(obj, self.attrname, value)

        else:
            raise ValueError('{0} does not match with {1}'.format(value, self))

    def _del(self, obj):

        if self._fdel is not None:
            self._fdel(obj)

        else:
            delattr(obj, self.attrname)

    def validate(self, data):
        """Validate input data."""

        return self.schema.validate(data)


class ArrayProperty(Property):
    """Array property type"""

    PTYPE = 'array'

    def __init__(
            self, cardinality=None, itemtype=None, schema=ArraySchema, unique=True,
            *args, **kwargs
    ):
        """
        :param int(s) cardinality: (min and) max number of items.
        :param type itemtype: type of items.

        """

        super(ArrayProperty, self).__init__(ptype=ptype, *args, **kwargs)

        self.cardinality = cardinality
        self.itemtype = itemtype
        self.unique = unique

    def validate(self, data, *args, **kwargs):

        result = super(ArrayProperty, self).validate(data=data, *args, **kwargs)

        if result:
            result = not isinstance(data, string_types)

            if result:
                if self.cardinality is not None:
                    if isinstance(self.cardinality, Number):
                        result = len(data) <= self.cardinality

                    else:
                        result = (
                            self.cardinality[0] <= len(data) <=
                            self.cardinality[1]
                        )

                if result and self.unique:
                    result = len(set(data)) == len(data)

                if result and self.itemtype is not None:

                    itemtype = self.itemtype

                    for item in data:
                        result = isinstance(item, itemtype)

                        if not result:
                            break

        return result


class NumberProperty(Property):

    def __init__(
        self, fget=None, minimum=-maxsize, maximum=maxsize, ptype=Number,
        *args, **kwargs
    ):

        super(NumberProperty, self).__init__(fget=fget, *args, **kwargs)

        self.minimum = minimum
        self.maximum = maximum

    def validate(self, data):

        result = super(NumberProperty, self).validate(data)

        return result and (self.minimum <= data <= self.maximum)


class FunctionProperty(Property):
    """Function property type."""

    def __init__(self, fget=None, args=None, rtype=None, *vargs, **kwargs):
        """
        :param list args: list argument name with default value if exist such as
            [name, (name, value), ...]
        :param type rtype: function result type.
        """

        super(FunctionProperty, self).__init__(*vargs, **kwargs)

        self.args = args or []
        self.rtype = rtype

        self._fget = fget or self._getfget()

    def _getfget(self):
        """Get f get in generating it from args and doc."""

        argcount = len(self.args)
        nlocals = 0
        stacksize = 0
        flags = 0

        args = []  # arg without default value
        vargs = []  # arg with default value

        for name in self.args:

            if isinstance(name, string_types):
                args.append(name)

            else:
                name, value = name
                vargs.append((name, value, str(randint(-maxsize, maxsize))))

        kwargs = vargs or map(
            lambda item: '{0}={1}'.format(item[0], item[1]), vargs
        )

        args = ', '.join(args)
        kwargs = ', '.join(vargs)
        if args and kwargs:
            args = args + ', ' + kwargs

        doc = '"""{0}\n\t{1}"""'.format(
            self.doc, ':rtype: {0}'.format(self.rtype) if self.rtype else ''
        )

        exec_(
            'def result({0}):\n\t{1}\n\traise NotImplementedError()'.format(
                args, doc
            )
        )

        return result

    def _get(self, obj):

        @wraps(self._fget)
        def result(*args, **kwargs):

            return self._fget(obj, *args, **kwargs)

        return result


class SchemaProperty(Property):
    """Schema property."""

    def __init__(self, schema, *args, **kwargs):
        """
        :param type schema: schema type.
        """

        super(SchemaProperty, self).__init__(*args, **kwargs)

        self.schema = schema

    def validate(self, data):

        result = super(SchemaProperty, self).validate(data)

        if result:
            result = self.schema.validate(data)

        return result
