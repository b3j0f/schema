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
from .utils import obj2schema, DynamicValue, This


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
            self, fget=None, fset=None, fdel=None, doc=None, **kwargs
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

        cls = type(self)

        for name, member in getmembers(
            cls,
            #lambda member: not isinstance(member, (FunctionType, MethodType))
        ):

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

                    if isinstance(val, _Schema):
                        val = val.default

                if isinstance(val, DynamicValue):
                    val = val()

                setattr(self, self._attrname(name=name), val)
                if member != val:
                    setattr(self, name, val)

        self._default = kwargs.get('default', self.default)

        if fget or not hasattr(self, '_fget'):
            self._fget = fget

        if fset or not hasattr(self, '_fset'):
            self._fset = fset

        if fdel or not hasattr(self, '_fdel'):
            self._fdel = fdel

    def _attrname(self, name=None):
        """Get attribute name to set in order to keep the schema value.

        :param str name: attribute name. Default is this name or uuid.
        :return:
        :rtype: str"""

        return '_{0}'.format(name or self._name or self._uuid)

    def __eq__(self, other):

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
            result = getattr(obj, self._attrname(), self._default)

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

        self._validate(data=value, owner=obj)

        if self._fset is not None:
            self._fset(obj, value)

        else:
            setattr(obj, self._attrname(), value)

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
            delattr(obj, self._attrname())

        # notify parent schema about value deletion.
        if isinstance(obj, _Schema):
            obj._delvalue(self)

    def _delvalue(self, schema):
        """Fired when inner schema delete its value.

        :param Schema schema: inner schema."""

    def _validate(self, data, owner=None):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :param Schema owner: schema owner.
        :raises: Exception if the data is not validated"""

        if isinstance(data, DynamicValue):
            data = data()

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
                        schema._validate(getattr(data, name))

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

    def _validate(self, data, owner=None, *args, **kwargs):

        ref = owner if self.ref is None else self.ref

        ref._validate(data=data, owner=owner)


def updatecontent(schemacls=None, updateparents=True, exclude=None):
    """Transform all schema class attributes to schemas.

    It can be used such as a decorator in order to ensure to update attributes
    with the decorated schema but take care to the limitation to use old style
    method call for overidden methods.

    .. example:
        @updatecontent  # update content at the end of its definition.
        class Test(Schema):
            this = This()  # instance of Test.
            def __init__(self, *args, **kwargs):
                Test.__init__(self, *args, **kwargs)  # old style method call.

    :param type schemacls: sub class of _Schema.
    :param bool updateparents: if True (default), update parent content.
    :param list exclude: attribute names to exclude from updating.
    :return: schemacls"""

    if schemacls is None:
        return updatecontent

    if updateparents:
        schemaclasses = reversed(list(schemacls.mro()))

    else:
        schemaclasses = [schemacls]

    for schemaclass in schemaclasses:

        for name, member in getattr(schemaclass, '__dict__', {}).items():

            # transform only public members
            if name[0] != '_' and (exclude is None or name not in exclude):

                toset = False  # flag for setting schemas

                fmember = member

                if isinstance(fmember, DynamicValue):
                    fmember = fmember()
                    toset = True

                if isinstance(fmember, _Schema):
                    schema = fmember

                    if not schema.name:
                        schema.name = name

                else:
                    toset = True

                    if name == 'default':
                        schema = RefSchema(default=member, name=name)

                    elif isinstance(fmember, This):
                        schema = schemaclass(*fmember.args, **fmember.kwargs)

                    else:
                        schema = obj2schema(obj=member, name=name)

                if schema is not None and toset:

                    try:
                        setattr(schemaclass, name, schema)

                    except (AttributeError, TypeError):
                        break

    return schemacls

updatecontent(RefSchema)  #: update content of RefSchema.


class MetaSchema(type):
    """Automatically register schemas."""

    def __new__(mcs, *args, **kwargs):

        result = super(MetaSchema, mcs).__new__(mcs, *args, **kwargs)

        if result.__data_types__:
            registercls(schemacls=result, data_types=result.__data_types__)

        # update all sub schemas related to values
        if result.__update_content__:
            updatecontent(schemacls=result)

        return result

    def __call__(cls, *args, **kwargs):

        result = super(MetaSchema, cls).__call__(*args, **kwargs)

        if result.__register__:  # register all new schema
            register(schema=result)

        return result

    def __instancecheck__(mcs, obj, *args, **kwargs):

        return isinstance(obj, _Schema)

    def __subclasscheck__(mcs, cls, *args, **kwargs):

        return issubclass(cls, _Schema)


# use metaschema such as the schema metaclass
@add_metaclass(MetaSchema)
class Schema(_Schema):

    #: Register instances in the registry if True (default).
    __register__ = True

    """update automatically the content if True (default).

    If True, take care to not having called the class in overidden methods.
    In such case, take a look to the using of the class This which recommands to
    use old style method call for overriden methods.

    ..example:
        class Test(Schema):
            __udpate_content__ = True  # set update content to True
            test = This()
            def __init__(self, *args, **kwargs):
                Schema.__init__(self, *args, **kwargs)  # old style call.
        """
    __update_content__ = True


def validate(schema, data):
    """Validate input data with input schema.

    :param Schema schema: schema able to validate input data.
    :param data: data to validate.
    """

    schema._validate(data=data)

def dump(schema):
    """Get a serialized value of input schema.

    :param Schema schema: schema to serialize.
    :rtype: dict"""

    result = {}

    for name, _ in iteritems(schema.getschemas()):

        if hasattr(schema, name):
            val = getattr(schema, name)

            if isinstance(val, DynamicValue):
                val = val()

            if isinstance(val, Schema):
                val = dump(val)

            result[name] = val

    return result
