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

from numbers import Number

from six import string_types

from collections import Iterable


class Property(object):
    """Schema property"""

    def __init__(
            self, name, ptype=object, default=None, mandatory=True,
            *args, **kwargs
    ):
        """
        :param str name: property name.
        :param type ptype: property type.
        :param default: default value.
        :param bool mandatory: mandatory property characteristic.
        """

        super(Property, self).__init__(*args, **kwargs)

        self.name = name
        self.ptype = ptype
        self.default = default
        self.mandatory = mandatory

    def validate(self, data):
        """Validate input data."""

        return isinstance(data, self.ptype)


class ArrayProperty(Property):
    """Array property type"""

    PTYPE = 'array'

    def __init__(
            self, cardinality=None, itemtype=None, ptype=Iterable,
            *args, **kwargs
    ):
        """
        :param int(s) cardinality: (min and) max number of items.
        :param type itemtype: type of items.

        """

        super(ArrayProperty, self).__init__(ptype=ptype, *args, **kwargs)

        self.cardinality = cardinality
        self.itemtype = itemtype
        self.ptype = ptype

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

                if result and self.itemtype is not None:

                    itemtype = self.itemtype

                    for item in data:
                        result = isinstance(item, itemtype)

                        if not result:
                            break

        return result


class FunctionProperty(Property):
    """Function property type."""

    def __init__(self, args=None, rtype=None, *vargs, **kwargs):
        """
        :param list args: argument names.
        :param type rtype: function result type.
        """

        super(FunctionProperty, self).__init__(*vargs, **kwargs)

        self.args = args
        self.rtype = rtype


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
