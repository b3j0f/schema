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

"""Python language schemas utilities."""

from re import compile as re_compile

from b3j0f.utils.version import OrderedDict
from b3j0f.utils.path import lookup

from ..base import Schema
from .factory import SchemaBuilder, build
from ..elementary import ElementarySchema, ArraySchema
from ..utils import (
    updatecontent, data2schema, datatype2schemacls, RefSchema
)

from types import (
    FunctionType, MethodType, LambdaType, BuiltinFunctionType,
    BuiltinMethodType
)

from six import get_function_globals

from inspect import getargspec, getsourcelines, isclass

from functools import wraps

__all__ = ['PythonSchemaBuilder', 'FunctionSchema', 'buildschema']


class PythonSchemaBuilder(SchemaBuilder):
    """In charge of building python classes."""

    __name__ = 'python'

    def build(self, _resource, **kwargs):

        if not isclass(_resource):
            raise TypeError(
                'Wrong type {0}, \'type\' expected'.format(_resource)
            )

        if issubclass(_resource, Schema):
            result = _resource

        else:
            result = datatype2schemacls(_datatype=_resource, _force=False)

            if result is None:
                resname = _resource.__name__

                if 'name' not in kwargs:
                    kwargs['name'] = resname

                """
                for attrname in dir(_resource):
                    if (
                        attrname[0] != '_' and
                        attrname not in kwargs and
                        not hasattr(Schema, attrname)
                    ):

                        attr = getattr(_resource, attrname)

                        if not isinstance(attr, MemberDescriptorType):
                            kwargs[attrname] = getattr(_resource, attrname)
                """

                result = type(resname, (Schema, _resource), kwargs)
                updatecontent(result, updateparents=False)

        return result

    def getresource(self, schemacls):

        result = None

        for mro in schemacls.mro():

            if issubclass(mro, Schema):
                result = mro
                break

        return result


def buildschema(_cls=None, **kwargs):
    """Class decorator used to build a schema from the decorate class.

    :param type _cls: class to decorate.
    :param kwargs: schema attributes to set.
    :rtype: type
    :return: schema class.
    """
    if _cls is None:
        return lambda _cls: buildschema(_cls=_cls, **kwargs)

    result = build(_cls, **kwargs)

    return result


@updatecontent
class ParamSchema(RefSchema):
    """Function parameter schema."""

    #: if true (default), update self ref when default is given.
    autotype = True
    mandatory = True  #: if true (default), parameter value is mandatory.

    def _setvalue(self, schema, value, *args, **kwargs):

        super(ParamSchema, self)._setvalue(schema, value, *args, **kwargs)

        if schema.name == 'default':

            if self.autotype and self.ref is None:
                self.ref = None if value is None else data2schema(value)

            if value is not None:
                self.mandatory = False


class FunctionSchema(ElementarySchema):
    """Function schema.

    Dedicated to describe functions, methods and lambda objects.
    """

    _PDESC = r':param (?P<ptype1>[\w_]+) (?P<pname1>\w+):'
    _PTYPE = r':type (?P<pname2>[\w_]+):(?P<ptype2>[^\n]+)'
    _RTYPE = r':rtype:(?P<rtype>[^\n]+)'

    _REC = re_compile('{0}|{1}|{2}'.format(_PDESC, _PTYPE, _RTYPE))

    __data_types__ = [
        FunctionType, MethodType, LambdaType, BuiltinFunctionType,
        BuiltinMethodType
    ]

    params = ArraySchema(itemtype=ParamSchema)
    rtype = Schema()
    impl = ''
    impltype = ''

    def _validate(self, data, owner, *args, **kwargs):

        ElementarySchema._validate(self, data=data, *args, **kwargs)

        if data != self._default_ or data is not self._default_:

            if data.__name__ != self.name:

                raise TypeError(
                    'Wrong function name {0}. {1} expected.'.format(
                        data.__name__, self.name
                    )
                )

            params, rtype = self._getparams_rtype(function=data)

            if len(params) != len(self.params):
                raise TypeError(
                    'Wrong param length: {0}. {1} expected.'.format(
                        len(params), len(self.params)
                    )
                )

            if self.rtype is not None:
                self.rtype._validate(data=rtype)

            for index, pkwargs in enumerate(params.values()):
                name = pkwargs['name']
                default = pkwargs.get('default')
                selfparam = self.params[index]

                if selfparam.name != name:
                    raise TypeError(
                        'Wrong parameter {0} at {1}. {2} expected.'.format(
                            name, index, selfparam.name
                        )
                    )

                if selfparam.default != default:
                    raise TypeError(
                        'Wrong default value {0} at {1}. Expected {2}.'.format(
                            default, index, selfparam.default
                        )
                    )

    def _setvalue(self, schema, value):

        if schema.name == 'default':

            self._setter(obj=self, value=value)

    def _setter(self, obj, value, *args, **kwargs):

        ElementarySchema._setter(self, obj, value, *args, **kwargs)

        pkwargs, self.rtype = self._getparams_rtype(value)

        params = []

        selfparams = {}

        for selfparam in self.params:
            selfparams[selfparam.name] = selfparam

        index = 0

        for index, pkwarg in enumerate(pkwargs.values()):

            name = pkwarg['name']

            selfparam = None  # old self param

            if name in selfparams:
                selfparam = selfparams[name]

            if selfparam is None:
                selfparam = ParamSchema(**pkwarg)

            else:
                for key in pkwarg:
                    val = pkwarg[key]
                    if val is not None:
                        setattr(selfparam, key, val)

            params.append(selfparam)

        self.params = params

        self.impltype = 'python'
        try:
            self.impl = str(getsourcelines(value))

        except TypeError:
            self.impl = ''

    @classmethod
    def _getparams_rtype(cls, function):
        """Get function params from input function and rtype.

        :return: OrderedDict or param schema by name and rtype.
        :rtype: tuple
        """
        try:
            args, _, _, default = getargspec(function)

        except TypeError:
            args, _, _, default = (), (), (), ()

        indexlen = len(args) - (0 if default is None else len(default))

        params = OrderedDict()

        for index, arg in enumerate(args):

            pkwargs = {
                'name': arg,
                'mandatory': True
            }  # param kwargs

            if index >= indexlen:  # has default value
                value = default[index - indexlen]
                pkwargs['default'] = value
                pkwargs['ref'] = None if value is None else data2schema(value)
                pkwargs['mandatory'] = False

            params[arg] = pkwargs

        rtype = None

        # parse docstring
        if function.__doc__ is not None:

            for match in cls._REC.findall(function.__doc__):

                if rtype is None:
                    rrtype = match[4].strip() or None

                    if rrtype:

                        try:
                            lkrtype = lookup(
                                rrtype, scope=get_function_globals(function)
                            )

                        except ImportError:
                            continue

                        else:
                            schemacls = datatype2schemacls(lkrtype)
                            rtype = schemacls()
                            continue

                pname = (match[1] or match[2]).strip()

                if pname and pname in params:
                    ptype = (match[0] or match[3]).strip()

                    try:
                        lkptype = lookup(
                            ptype, scope=get_function_globals(function)
                        )

                    except ImportError:
                        continue

                    else:
                        schemacls = datatype2schemacls(lkptype)
                        params[pname]['ref'] = schemacls()

        return params, rtype

    def __call__(self, *args, **kwargs):

        return self.default(*args, **kwargs)

    def _getter(self, obj, *args, **kwargs):

        func = ElementarySchema._getter(self, obj, *args, **kwargs)

        @wraps(func)
        def result(*args, **kwargs):

            try:
                result = func(obj, *args, **kwargs)

            except TypeError:
                result = func(*args, **kwargs)

            return result

        return result


def funcschema(default=None, *args, **kwargs):
    """Decorator to use in order to transform a function into a schema."""
    if default is None:
        return lambda default: funcschema(default=default, *args, **kwargs)

    return FunctionSchema(default=default, *args, **kwargs)
