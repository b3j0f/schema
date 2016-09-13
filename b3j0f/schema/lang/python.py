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

"""Python language schemas utilities"""

__all__ = ['PythonSchemaBuilder', 'FunctionSchema']

from re import compile as re_compile

from b3j0f.utils.version import OrderedDict
from b3j0f.utils.path import lookup

from .factory import SchemaBuilder, getschemacls, build
from ..registry import getbyuuid, getbydatatype
from ..utils import This, updatecontent, data2schema, getschemafromdatatype
from ..base import Schema, RefSchema
from ..elementary import ElementarySchema, ArraySchema, TypeSchema, StringSchema

from types import FunctionType, MethodType, LambdaType

from six import iteritems

from inspect import getargspec, getsourcelines


class PythonSchemaBuilder(SchemaBuilder):

    __name__ = 'python'

    def build(self, _resource, **kwargs):

        if not isinstance(_resource, type):
            raise TypeError(
                'Wrong type {0}, \'type\' expected'.format(_resource)
            )

        if issubclass(_resource, Schema):
            result = _resource

        else:
            result = getschemafromdatatype(_datatype=_resource, _force=False)

            if result is None:

                resname = _resource.__name__
                if 'name' not in kwargs:
                    kwargs['name'] = resname

                result = type(resname, (Schema, _resource), kwargs)
                updatecontent(result)

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


class ParamSchema(RefSchema):
    """Function parameter schema."""

    hasvalue = False


class FunctionSchema(ElementarySchema):
    """Function schema.

    Dedicated to describe functions, methods and lambda objects."""

    _PDESC = r':param (?P<ptype1>[\w_]+) (?P<pname1>\w+):'
    _PTYPE = r':type (?P<pname2>[\w_]+):(?P<ptype2>[^\n]+)'
    _RTYPE = r':rtype:(?P<rtype>[^\n]+)'

    _REC = re_compile('{0}|{1}|{2}'.format(_PDESC, _PTYPE, _RTYPE))

    __data_types__ = [FunctionType, MethodType, LambdaType]

    params = ArraySchema(itemtype=ParamSchema)
    rtype = ''
    impl = ''
    impltype = ''

    def _validate(self, data, owner, *args, **kwargs):

        ElementarySchema._validate(self, data=data, *args, **kwargs)

        if data != self._default or data is not self._default:

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

            self.rtype._validate(data=rtype)

            for index, pkwargs in enumerate(params.values()):
                name = pkwargs['name']
                default = pkwargs['default']
                ptype = pkwargs['type']
                selfparam = self.params[index]

                if selfparam.name != name:
                    raise TypeError(
                        'Wrong parameter name {0} at {1}. {2} expected.'.format(
                            name, index, selfparam.name
                        )
                    )

                if selfparam.default != default:
                    raise TypeError(
                        'Wrong default value {0} at {1}. Expected {2}.'.format(
                            default, index, selfparam.default
                        )
                    )

                if not issubclass(ptype, selfparam.type):
                    raise TypeError(
                        'Wrong param type {0} at {1}. Expected {2}.'.format(
                            ptype, index, selfparam.type
                        )
                    )

    def _setvalue(self, schema, value):

        if schema.name == 'default':

            self._setter(obj=self, value=value)

    def _setter(self, obj, value, *args, **kwargs):

        ElementarySchema._setter(self, obj, value, *args, **kwargs)

        pkwargs, self.rtype = self._getparams_rtype(value)

        index = 0

        for index, pkwarg in enumerate(pkwargs.values()):

            try:
                selfparam = self.params[index]

            except IndexError:
                selfparam = None

            if selfparam is None:
                selfparam = ParamSchema(**pkwarg)
                self.params.insert(index, selfparam)

            else:
                selfparam.name = pkwarg['name']
                selfparam.ref = pkwarg['ref']
                selfparam.default = pkwarg['default']
                selfparam.hasvalue = pkwarg['hasvalue']

        self.params = self.params[:index]

        self.impltype = 'python'
        self.impl = str(getsourcelines(value))

    @classmethod
    def _getparams_rtype(cls, function):
        """Get function params from input function and rtype.

        :return: OrderedDict or param schema by name and rtype.
        :rtype: tuple"""

        result = []

        args, vargs, _, default = getargspec(function)

        indexlen = len(args) - (0 if default is None else len(default))

        params = OrderedDict()

        for index, arg in enumerate(args):

            pkwargs = {
                'name': arg,
                'default': None,
                'type': None,
                'hasvalue': False
            }  # param kwargs

            if index >= indexlen:  # has default value
                value = default[index - indexlen]
                pkwargs['default'] = value
                pkwargs['ref'] = data2schema(value)
                pkwargs['hasvalue'] = True

            params[arg] = pkwargs

        rtype = None

        # parse docstring
        if function.__doc__ is not None:

            for match in cls._REC.findall(function.__doc__):

                if rtype is None:
                    rtype = match[4] or None

                    if rtype:
                        continue

                pname = match[1] or match[3]

                if pname:
                    ptype = match[0] or match[2]

                    lkptype = lookup(ptype)

                    ref = getschemafromdatatype(lkptype)
                    params[pname]['ref'] = ref

        return params, (rtype or '')

    def __call__(self, *args, **kwargs):

        return self.default(*args, **kwargs)

    def _getter(self, obj, *args, **kwargs):

        func = ElementarySchema._getter(self, obj, *args, **kwargs)

        def result(*args, **kwargs):

            try:
                result = func(obj, *args, **kwargs)

            except TypeError as te:
                result = func(*args, **kwargs)

            return result

        return result
