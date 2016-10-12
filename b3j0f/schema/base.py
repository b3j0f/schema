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

"""Base schema package."""

from b3j0f.utils.version import OrderedDict

from inspect import getmembers

from six import iteritems

from uuid import uuid4

__all__ = ['Schema', 'DynamicValue']


class DynamicValue(object):
    """Handle a function in order to dynamically lead a value while cleaning a
    schema.

    For example, the schema attribute ``uuid`` uses a DynamicValue in order to
    ensure default generation per instanciation.
    """

    __slots__ = ['func']

    def __init__(self, func, *args, **kwargs):
        """:param func: function to execute while cleaning a schema."""
        super(DynamicValue, self).__init__(*args, **kwargs)

        self.func = func

    def __call__(self):

        return self.func()


class Schema(property):
    """Schema description.

    A schema is identified by a string such as an universal unique identifier,
    and optionnally a name.

    Any setted value respect those conditions in this order:
    1. if the value is a lambda expression, the value equals its execution.
    2. the value is validated with this method `validate`.
    3. the value is given to a custom setter (`fget` constructor parameter) if
        given or setted to this attribute `_value`.

    Once you defined your schema inheriting from this class, your schema will
    be automatically registered in the registry and becomes accessible from the
    `b3j0f.schema.reg.getschemabyuid` function.
    """

    name = ''  #: schema name. Default is self name.
    #: schema universal unique identifier.
    uuid = DynamicValue(lambda: str(uuid4()))
    doc = ''  #: schema description.
    default = None  #: schema default value.
    required = []  #: required schema names.
    version = '1'  #: schema version.
    nullable = True  #: if True (default), value can be None.

    def __init__(
            self, fget=None, fset=None, fdel=None, doc=None, **kwargs
    ):
        """Instance attributes are setted related to arguments or inner schemas.

        :param default: default value. If lambda, called at initialization.
        """
        super(Schema, self).__init__(
            fget=self._getter, fset=self._setter, fdel=self._deleter,
            doc=doc
        )

        # set custom getter/setter/deleter
        if fget or not hasattr(self, '_fget_'):
            self._fget_ = fget

        if fset or not hasattr(self, '_fset_'):
            self._fset_ = fset

        if fdel or not hasattr(self, '_fdel_'):
            self._fdel_ = fdel

        if doc is not None:
            kwargs['doc'] = doc

        cls = type(self)

        # set inner schema values
        for name, member in getmembers(cls):

            if name[0] != '_' and name not in [
                    'fget', 'fset', 'fdel', 'setter', 'getter', 'deleter',
                    'default'
            ]:

                if name in kwargs:
                    val = kwargs[name]

                else:
                    val = member

                    if isinstance(val, DynamicValue):
                        val = val()

                    if isinstance(val, Schema):
                        val = val.default

                if isinstance(val, DynamicValue):
                    val = val()

                setattr(self, self._attrname(name=name), val)
                if member != val:
                    setattr(self, name, val)

        default = kwargs.get('default', self.default)

        self._default_ = default

        if default is not None:
            self.default = default

    def _attrname(self, name=None):
        """Get attribute name to set in order to keep the schema value.

        :param str name: attribute name. Default is this name or uuid.
        :return:
        :rtype: str
        """
        return '_{0}_'.format(name or self._name_ or self._uuid_)

    def __repr__(self):

        return '{0}({1}/{2})'.format(type(self).__name__, self.uuid, self.name)

    def __hash__(self):

        return hash(self.uuid)

    def _getter(self, obj):
        """Called when the parent element tries to get this property value.

        :param obj: parent object.
        """
        result = None

        if self._fget_ is not None:
            result = self._fget_(obj)

        if result is None:
            result = getattr(obj, self._attrname(), self._default_)

        # notify parent schema about returned value
        if isinstance(obj, Schema):
            obj._getvalue(self, result)

        return result

    def _getvalue(self, schema, value):
        """Fired when inner schema returns a value.

        :param Schema schema: inner schema.
        :param value: returned value.
        """

    def _setter(self, obj, value):
        """Called when the parent element tries to set this property value.

        :param obj: parent object.
        :param value: new value to use. If lambda, updated with the lambda
            result.
        """
        if isinstance(value, DynamicValue):  # execute lambda values.
            fvalue = value()

        else:
            fvalue = value

        self._validate(data=fvalue, owner=obj)

        if self._fset_ is not None:
            self._fset_(obj, fvalue)

        else:
            setattr(obj, self._attrname(), value)

        # notify obj about the new value.
        if isinstance(obj, Schema):
            obj._setvalue(self, fvalue)

    def _setvalue(self, schema, value):
        """Fired when inner schema change of value.

        :param Schema schema: inner schema.
        :param value: new value.
        """

    def _deleter(self, obj):
        """Called when the parent element tries to delete this property value.

        :param obj: parent object.
        """
        if self._fdel_ is not None:
            self._fdel_(obj)

        else:
            delattr(obj, self._attrname())

        # notify parent schema about value deletion.
        if isinstance(obj, Schema):
            obj._delvalue(self)

    def _delvalue(self, schema):
        """Fired when inner schema delete its value.

        :param Schema schema: inner schema.
        """

    def _validate(self, data, owner=None):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :param Schema owner: schema owner.
        :raises: Exception if the data is not validated.
        """
        if isinstance(data, DynamicValue):
            data = data()

        if data is None and not self.nullable:
            raise ValueError('Value can not be null')

        elif data is not None:

            isdict = isinstance(data, dict)

            for name, schema in iteritems(self.getschemas()):

                if name == 'default':
                    continue

                if name in self.required:
                    if (
                        (isdict and name not in data) or
                        (not isdict and not hasattr(data, name))
                    ):
                        part1 = (
                            'Mandatory property {0} by {1} is missing in {2}.'.
                            format(name, self, data)
                        )
                        part2 = '{0} expected.'.format(schema)
                        error = '{0} {1}'.format(part1, part2)

                        raise ValueError(error)

                elif (isdict and name in data) or hasattr(data, name):

                    value = data[name] if isdict else getattr(data, name)
                    schema._validate(data=value, owner=self)

    @classmethod
    def getschemas(cls):
        """Get inner schemas by name.

        :return: ordered dict by name.
        :rtype: OrderedDict
        """
        members = getmembers(cls, lambda member: isinstance(member, Schema))

        result = OrderedDict()

        for name, member in members:
            result[name] = member

        return result

    @classmethod
    def apply(cls, *args, **kwargs):
        """Decorator for schema application with parameters."""
        return lambda fget: cls(fget, *args, **kwargs)
