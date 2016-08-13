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

__all__ = [
    'MetaSchema', 'Schema', 'clsschemamaker', 'DynamicValue', 'DefaultSchema'
]

from b3j0f.utils.version import OrderedDict

from types import FunctionType, MethodType

from inspect import getmembers, isclass

from six import get_unbound_function, add_metaclass, iteritems

from uuid import uuid4

from .registry import register, registercls
from .factory import registermaker, getschemacls
from .utils import obj2schema, DynamicValue


class _Schema(property):
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


class MetaSchema(type):
    """Automatically register schemas."""

    def __new__(mcs, *args, **kwargs):

        result = super(MetaSchema, mcs).__new__(mcs, *args, **kwargs)

        if result.__data_types__:
            registercls(schemacls=result, data_types=result.__data_types__)

        # update all sub schemas related to values
        resolveschema(schemacls=result)

        return result

    def __call__(cls, *args, **kwargs):

        result = super(MetaSchema, cls).__call__(*args, **kwargs)

        if result.__register__:  # register all new schema
            register(schema=result)

        return result


class RefSchema(_Schema):
    """Schema which references another schema."""

    def __init__(self, ref, *args, **kwargs):

        super(RefSchema, self).__init__(*args, **kwargs)

        self.ref = ref

    def _setter(self, obj, value):

        if isinstance(value, DynamicValue):  # execute lambda values.
            value = value()

        self.ref.validate(value)  # delegate validation to owner schema

        setattr(obj, self.attrname, value)


def resolveschema(schemacls):
    """Parse schemacls and all its super classes and transform all values to
    schema if schema classes are associated to simple types.

    :param type schemacls: sub class of schema."""

    for mro in schemacls.mro():

        for name, member in getmembers(
            mro,
            lambda member: not isinstance(member, (FunctionType, MethodType))
        ):

            if name[0] != '_':

                schema = None

                if isinstance(member, _Schema):
                    schema = member

                else:
                    if name == 'default':

                        if isinstance(member, DynamicValue):
                            member = member()

                        schema = RefSchema(ref=self, default=member)

                    else:
                        schema = obj2schema(member)

                if schema is not None:

                    if schema.name is None:
                        schema.name = name

                    setattr(schemacls, name, schema)


# use metaschema such as the schema metaclass
@add_metaclass(MetaSchema)
class Schema(_Schema):

    __register__ = True  #: automatically register it if True.
    __data_types__ = []  #: data types which can be instanciated by this schema.

    name = ''  #: schema name. Default is self name.
    uuid = DynamicValue(lambda: uuid4())  #: schema universal unique identifier.
    doc = ''  #: schema description.
    default = None  #: schema default value.
    required = DynamicValue(lambda: [])  #: required schema names.
    version = '1'  #: schema version.
    nullable = True  #: if True (default), value can be None.

    def __init__(
            self, fget=None, fset=None, fdel=None, doc=None, default=None,
            **kwargs
    ):
        """Instance attributes are setted related to arguments or inner schemas.

        :param default: default value. If lambda, called at initialization.
        """

        super(_Schema, self).__init__(
            fget=self._getter, fset=self._setter, fdel=self._deleter,
            doc=doc
        )

        if doc is not None:
            kwargs['doc'] = doc

        for name, member in getmembers(
            type(self),
            lambda member: not isinstance(member, (FunctionType, MethodType))
        ):

            if name[0] != '_' and name not in [
                    'fget', 'fset', 'fdel', 'setter', 'getter', 'deleter',
                    'default'
            ]:

                if name in kwargs:
                    val = kwargs[name]

                elif isinstance(member, _Schema):
                    val = member.default

                else:
                    val = member

                if isinstance(val, DynamicValue):
                    val = val()

                setattr(self, name, val)

        if default is not None:

            self.default = default

        self._fget = fget
        self._fset = fset
        self._fdel = fdel

    @property
    def attrname(self):
        """Get attribute name to set in order to keep the schema value."""

        return '_{0}'.format(self.name or self.uid)

    def __eq__(self, other):
        """Compare schemas."""

        return other is self or self.getschemas() == other.getschemas()

    def _getter(self, obj, *args, **kwargs):
        """Called when the parent element tries to get this property value.

        :param obj: parent object."""

        result = None

        if self._fget is not None:
            result = self._fget(obj)

        if result is None:
            result = getattr(self, self.attrname)

        return result

    def _setter(self, obj, value):
        """Called when the parent element tries to set this property value.

        :param obj: parent object.
        :param value: new value to use. If lambda, updated with the lambda
            result."""

        if isinstance(value, DynamicValue):  # execute lambda values.
            value = value()

        self.validate(value)

        if self._fset is not None:
            self._fset(obj, value)

        else:
            setattr(obj, self.attrname, value)

    def _deleter(self, obj):
        """Called when the parent element tries to delete this property value.

        :param obj: parent object.
        """

        if self._fdel is not None:
            self._fdel(obj)

        else:
            delattr(self, self.attrname)

    def validate(self, data):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :raises: Exception if the data is not validated"""

        if data is None and not self.nullable:
            raise TypeError('Value can not be null')

        elif data is not None:
            if self.__data_types__:  # data must inherits from this data_types
                if not isinstance(data, tuple(self.__data_types__)):
                    raise TypeError(
                        'Wrong data value: {0}. {1} expected.'.format(
                            data, self.__data_types__
                        )
                    )

            elif not isinstance(data, type(self)):  # or from this
                raise TypeError(
                    'Wrong type {0}. {1} expected'.format(data, type(self))
                )

            for name, schema in iteritems(self.getschemas()):
                print('validate', self, name, schema)
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

        for name, schema in iteritems(self.getschemas()):

            if hasattr(self, name):
                val = getattr(self, name)
                result[name] = val

        return result

    @classmethod
    def getschemas(cls):
        """Get inner schemas by name.

        :return: ordered dict by name.
        :rtype: ordered dict by name"""

        members = getmembers(cls, lambda member: isinstance(member, Schema))

        result = OrderedDict()

        for name, member in members:
            result[name] = member

        return result


Schema.default = RefSchema()
