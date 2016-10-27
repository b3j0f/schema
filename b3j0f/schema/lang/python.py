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

from ..base import Schema, DynamicValue
from .factory import SchemaBuilder, build
from ..elementary import ElementarySchema, ArraySchema, OneOfSchema, TypeSchema
from ..utils import updatecontent, data2schema, datatype2schemacls, RefSchema

from types import (
    FunctionType, MethodType, LambdaType, BuiltinFunctionType,
    BuiltinMethodType, MemberDescriptorType
)

from six import get_function_globals

from inspect import getargspec, getsourcelines, isclass, isbuiltin

from functools import wraps

__all__ = [
    'PythonSchemaBuilder', 'FunctionSchema', 'buildschema', 'ParamSchema'
]


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

                for attrname in dir(_resource):
                    if (
                        attrname and attrname[0] != '_' and
                        attrname not in kwargs and
                        not hasattr(Schema, attrname)
                    ):
                        attr = getattr(_resource, attrname)

                        if not isinstance(attr, MemberDescriptorType):
                            kwargs[attrname] = attr

                result = type(resname, (Schema,), kwargs)

        return result

    def getresource(self, schemacls):

        result = None

        if hasattr(schemacls, 'mro'):
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


class ParamTypeSchema(Schema):
    """In charge of embedding a parameter type which met a problem while
    generating a schema."""

    type = TypeSchema()

    def _validate(self, data, *args, **kwargs):

        super(ParamTypeSchema, self)._validate(data=data, *args, **kwargs)

        if not isinstance(data, self.type):
            raise TypeError(
                'Wrong type of {0}. {1} expected.'.format(data, self.type)
            )


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

    _PDESC = r':param (?P<ptype1>[\w_,]+) (?P<pname1>\w+):'
    _PTYPE = r':type (?P<pname2>[\w_]+):(?P<ptype2>[^\n]+)'
    _RTYPE = r':rtype:(?P<rtype>[^\n]+)'

    _REC = re_compile('{0}|{1}|{2}'.format(_PDESC, _PTYPE, _RTYPE))

    __data_types__ = [
        FunctionType, MethodType, LambdaType, BuiltinFunctionType,
        BuiltinMethodType
    ]

    params = ArraySchema(itemtype=ParamSchema())
    rtype = Schema()
    impl = ''
    impltype = ''
    safe = False
    varargs = False

    def _validate(self, data, owner, *args, **kwargs):

        ElementarySchema._validate(self, data=data, *args, **kwargs)

        if data != self.default or data is not self.default:

            errormsg = 'Error while validating {0} with {1}'.format(data, self)

            if data.__name__ != self.name:

                raise TypeError(
                    '{0}. Wrong function name {1}. {2} expected.'.format(
                        errormsg, data.__name__, self.name
                    )
                )

            params, rtype, vargs, kwargs = self._getparams_rtype(function=data)

            var = self.varargs or vargs or kwargs

            if (not var) and len(params) != len(self.params):
                raise TypeError(
                    '{0}. Wrong param length: {1}. {2} expected.'.format(
                        errormsg, len(params), len(self.params)
                    )
                )

            if self.rtype is not None and type(self.rtype) != type(rtype):
                raise TypeError(
                    '{0}. Wrong rtype {1}. {2} expected.'.format(
                        rtype, self.rtype
                    )
                )

            for index, pkwargs in enumerate(params.values()):
                name = pkwargs['name']
                default = pkwargs.get('default')
                param = self.params[index]

                if param.name != name:
                    raise TypeError(
                        '{0}. Wrong param {1} at {2}. {3} expected.'.format(
                            errormsg, name, index, param.name
                        )
                    )

                val = param.default
                if isinstance(val, DynamicValue):
                    val = val()

                if (
                    val is not None and default is not None and val != default
                ):
                    raise TypeError(
                        '{0}. Wrong val {1}/{2} at {3}. Expected {4}.'.format(
                            errormsg, name, default, index, val
                        )
                    )

    def _setvalue(self, schema, value):

        if schema.name == 'default':
            self._setter(obj=self, value=value)

    def _setter(self, obj, value, *args, **kwargs):

        if hasattr(self, 'olddefault'):
            if self.olddefault is value:
                return

        self.olddefault = value

        ElementarySchema._setter(self, obj, value, *args, **kwargs)

        pkwargs, self.rtype, vargs, kwargs = self._getparams_rtype(value)

        self.vargs = vargs or kwargs

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

        :return: OrderedDict, rtype, vargs and kwargs.
        :rtype: tuple
        """
        try:
            args, vargs, kwargs, default = getargspec(function)

        except TypeError:
            args, vargs, kwargs, default = (), (), (), ()

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
        if function.__doc__ is not None and not isbuiltin(function):

            scope = get_function_globals(function)

            for match in cls._REC.findall(function.__doc__):
                if rtype is None:
                    rrtype = match[4].strip() or None

                    if rrtype:

                        rtypes = rrtype.split(',')

                        schemas = []
                        for rtype_ in rtypes:

                            rtype_ = rtype_.strip()
                            islist = False

                            try:
                                lkrtype = lookup(rtype_, scope=scope)

                            except ImportError:
                                islist = True

                                try:
                                    if rtype_[-1] == 's':
                                        lkrtype = lookup(
                                            rtype_[:-1], scope=scope
                                        )

                                    elif rtype_.startswith('list of '):
                                        lkrtype = lookup(
                                            rtype_[8:], scope=scope
                                        )

                                    else:
                                        raise

                                except ImportError:
                                    msg = 'rtype "{0}" ({1}) from {2} not found.'
                                    raise ImportError(
                                        msg.format(rtype_, rrtype, function)
                                    )

                            try:
                                schemacls = datatype2schemacls(lkrtype)

                            except TypeError:
                                schemacls = ParamTypeSchema(type=lkrtype)

                            rschema = schemacls()

                            if islist:
                                rschema = ArraySchema(itemtype=rschema)

                            schemas.append(rschema)

                        if len(rtypes) > 1:
                            rtype = OneOfSchema(schemas=schemas, nullable=True)

                        else:
                            rtype = schemas[0]

                        continue

                pname = (match[1] or match[2]).strip()

                if pname and pname in params:

                    ptype = (match[0] or match[3]).strip()

                    ptypes = ptype.split(',')

                    schemas = []

                    for ptype in ptypes:

                        ptype = ptype.strip()

                        islist = False

                        try:
                            lkptype = lookup(ptype, scope=scope)

                        except ImportError:
                            islist = True

                            try:
                                if ptype[-1] == 's':
                                    lkptype = lookup(ptype[:-1], scope=scope)

                                elif ptype.startswith('list of '):
                                    lkptype = lookup(ptype[8:], scope=scope)

                                else:
                                    raise

                            except ImportError:

                                msg = 'Error on ptype "{0}" ({1}) from {2} not found.'
                                raise ImportError(
                                    msg.format(pname, ptype, function)
                                )

                        try:
                            schemacls = datatype2schemacls(lkptype)

                        except TypeError:
                            schemacls = ParamTypeSchema(type=lkptype)

                        pschema = schemacls()

                        if islist:
                            pschema = ArraySchema(itemtype=pschema)

                        schemas.append(pschema)

                    if len(ptypes) > 1:
                        pschema = OneOfSchema(schemas=schemas, nullable=True)

                    else:
                        pschema = schemas[0]

                    params[pname]['ref'] = pschema

        return params, rtype, vargs, kwargs

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

        result.source = func

        return result


def funcschema(default=None, *args, **kwargs):
    """Decorator to use in order to transform a function into a schema."""
    if default is None:
        return lambda default: funcschema(default=default, *args, **kwargs)

    return FunctionSchema(default=default, *args, **kwargs)
