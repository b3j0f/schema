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

__all__ = ['MetaSchema', 'Schema', 'DynamicValue', 'RefSchema', 'This']

from b3j0f.utils.version import OrderedDict

from types import FunctionType, MethodType

from inspect import getmembers, isclass

from six import get_unbound_function, add_metaclass, iteritems

from uuid import uuid4

from .registry import register, registercls
from .factory import registermaker, getschemacls
from .utils import obj2schema, DynamicValue


class This(object):
    """Tool Used to set inner schemas with the same type with specific arguments
    .

    ..example::

        class Test(Schema):
            # contain an inner schema nullable 'test' of type Test.
            test = This(nullable=False)

    :param args: schema class vargs to use.
    :param kwargs: schema class kwargs to use.

    :return: input args and kwargs.
    :rtype: tuple"""

    def __init__(self, *args, **kwargs):

        super(This, self).__init__()

        self.args = args
        self.kwargs = kwargs


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

    __data_types__ = []  #: data types which can be instanciated by this schema.

    name = ''  #: schema name. Default is self name.
    uuid = DynamicValue(lambda: str(uuid4()))  #: schema universal unique identifier.
    doc = ''  #: schema description.
    default = None  #: schema default value.
    required = []  #: required schema names.
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
                    'default', 'attrname'
            ]:

                if name in kwargs:
                    val = kwargs[name]

                else:
                    val = member

                    if isinstance(val, DynamicValue):
                        val = val()

                    if isinstance(val, _Schema):
                        val = getattr(self, name)
                        #val = val._default

                if isinstance(val, DynamicValue):
                    val = val()

                setattr(self, self.attrname(name=name), val)
                setattr(self, name, val)

        if default is None:
            default = self.default

        self._default = default

        self._fget = fget
        self._fset = fset
        self._fdel = fdel

    def attrname(self, name=None):
        """Get attribute name to set in order to keep the schema value.

        :param str name: attribute name. Default is this name or uuid.
        :return:
        :rtype: str"""

        return '_{0}'.format(name or self._name or self._uuid)

    def __eq__(self, other):
        """Compare schemas."""

        return other is self or self.getschemas() == other.getschemas()

    def __repr__(self):

        return '{0}({1}/{2})'.format(type(self).__name__, self.uuid, self.name)

    def _getter(self, obj):
        """Called when the parent element tries to get this property value.

        :param obj: parent object."""

        result = None

        if self._fget is not None:
            result = self._fget(obj)

        if result is None:
            result = getattr(obj, self.attrname(), self._default)

        # notify parent schema about returned value
        if isinstance(obj, _Schema):
            obj._getvalue(self, result)

        return result

    def _getvalue(self, schema, value):
        """Fired when inner schema returns a value.

        :param Schema schema: inner schema.
        :param value: returned value."""

    def _setter(self, obj, value):
        """Called when the parent element tries to set this property value.

        :param obj: parent object.
        :param value: new value to use. If lambda, updated with the lambda
            result."""

        if isinstance(value, DynamicValue):  # execute lambda values.
            value = value()

        self.validate(data=value, owner=obj)

        if self._fset is not None:
            self._fset(obj, value)

        else:
            setattr(obj, self.attrname(), value)

        # notify obj about the new value.
        if isinstance(obj, _Schema):
            obj._setvalue(self, value)

    def _setvalue(self, schema, value):
        """Fired when inner schema change of value.

        :param Schema schema: inner schema.
        :param value: new value."""

    def _deleter(self, obj):
        """Called when the parent element tries to delete this property value.

        :param obj: parent object.
        """

        if self._fdel is not None:
            self._fdel(obj)

        else:
            delattr(obj, self.attrname())

        # notify parent schema about value deletion.
        if isinstance(obj, _Schema):
            obj._delvalue(self)

    def _delvalue(self, schema):
        """Fired when inner schema delete its value.

        :param Schema schema: inner schema."""

    def validate(self, data, owner=None):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :param Schema owner: schema owner.
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

        members = getmembers(cls, lambda member: isinstance(member, _Schema))

        result = OrderedDict()

        for name, member in members:
            result[name] = member

        return result


class RefSchema(_Schema):
    """Schema which references another schema."""

    ref = _Schema()  #: the reference must be a schema.

    def validate(self, data, owner=None, *args, **kwargs):

        ref = owner if self.ref is None else self.ref

        return ref.validate(data=data, owner=owner)


def updatecontent(schemacls, updateparents=True):
    """Transform all schema class attributes to schemas.

    :param type schemacls: sub class of _Schema.
    :param bool updateparents: if True (default), update parent content."""

    if updateparents:
        schemaclasses = reversed(list(schemacls.mro()))

    else:
        schemaclasses = [schemacls]

    for schemaclass in schemaclasses:

        for name, member in getattr(schemaclass, '__dict__', {}).items():

            if name[0] != '_':  # transform only public members

                toset = False  # flag for setting schemas

                if isinstance(member, DynamicValue):
                    member = member()
                    toset = True

                if isinstance(member, _Schema):
                    schema = member

                    if not schema.name:
                        schema.name = name

                else:
                    toset = True

                    if name == 'default':
                        schema = RefSchema(default=member, name=name)

                    elif isinstance(member, This):
                        schema = schemaclass(*member.args, **member.kwargs)

                    else:
                        schema = obj2schema(obj=member, name=name)

                if schema is not None and toset:

                    try:
                        setattr(schemaclass, name, schema)

                    except (AttributeError, TypeError):
                        break

updatecontent(RefSchema)  #: update content of RefSchema.


class MetaSchema(type):
    """Automatically register schemas."""

    def __new__(mcs, *args, **kwargs):

        result = super(MetaSchema, mcs).__new__(mcs, *args, **kwargs)

        if result.__data_types__:
            registercls(schemacls=result, data_types=result.__data_types__)

        # update all sub schemas related to values
        updatecontent(schemacls=result)

        return result

    def __call__(cls, *args, **kwargs):

        result = super(MetaSchema, cls).__call__(*args, **kwargs)

        if result.__register__:  # register all new schema
            register(schema=result)

        return result


# use metaschema such as the schema metaclass
@add_metaclass(MetaSchema)
class Schema(_Schema):

    #: Register instances in the registry if True (False by default).
    __register__ = False
