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

from .factory import SchemaBuilder, getschemacls, build
from ..utils import This
from ..base import _Schema, Schema
from ..elementary import ElementarySchema, ArraySchema, TypeSchema

from types import FunctionType, MethodType, LambdaType

from inspect import getargspec


class PythonSchemaBuilder(SchemaBuilder):

    __name__ = 'python'

    def build(self, resource):

        if not isinstance(resource, type):
            raise TypeError('Wrong type {0}, \'type\' expected'.format(resource))

        if issubclass(resource, _Schema):
            result = resource

        else:
            try:
                result = getschemacls(resource)

            except KeyError:
                resname = resource.__name__ if name is None else name
                result = type(resname, (Schema, resource), {})

        return result

    def getresource(self, schemacls):

        result = None

        for mro in schemacls.mro():
            if issubclass(mro, Schema):
                result = mro
                break

        return result


def buildschema(_cls=None, **kwars):
    """Class decorator used to build a schema from the decorate class.

    :param type _cls: class to decorate.
    :param kwargs: schema attributes to set.
    :rtype: type
    :return: schema class.
    """

    def _buildschema(cls, **kwargs):

        result = build(cls)

        for name, arg in iteritems(kwargs):
            setattr(result, name, arg)

        return result

    if _cls is None:
        result = lambda cls: _buildschema(_cls, **kwargs)

    else:
        result = _buildschema(cls=_cls, **kwargs)

    return result


class ParamSchema(Schema):
        """Function parameter schema."""

        type = object
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
    rtype = TypeSchema(nullable=True, default=None)
    impl = ''
    impltype = 'python'
    fget = This()
    fset = This()
    fdel = This()

    def validate(self, data, owner, *args, **kwargs):

        ElementarySchema.validate(self, data=data, *args, **kwargs)

        if data != self.default:

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

            self.rtype.validate(data=rtype)

            for index, item in enumerate(params.items()):
                name, param = item
                selfparam = self.params[index]

                if selfparam.name != name:
                    raise TypeError(
                        'Wrong parameter name {0} at {1}. {2} expected.'.format(
                            name, index, selfparam.name
                        )
                    )

                if selfparam.default != param.default:
                    raise TypeError(
                        'Wrong default value {0} at {1}. Expected {2}.'.format(
                            param.default, index, selfparam.default
                        )
                    )

                if not issubclass(param.type, selfparam.type):
                    raise TypeError(
                        'Wrong param type {0} at {1}. Expected {2}.'.format(
                            param.type, index, selfparam.type
                        )
                    )

    def _setvalue(self, schema, value, *args, **kwargs):

        if schema.name == 'default':
            self.params, self.rtype = FunctionSchema._getparams_rtype(value)

    @staticmethod
    def _getparams_rtype(function):
        """Get function params from input function and rtype.

        :return: OrderedDict or param schema by name and rtype.
        :rtype: tuple"""

        result = []

        args, vargs, _, default = getargspec(function)

        indexlen = len(args) - (0 if default is None else len(default))

        params = OrderedDict()

        for index, arg in enumerate(args):

            pkwargs = {'name': arg}  # param kwargs

            if index >= indexlen:  # has default value
                value = default[index - indexlen]
                pkwargs['default'] = value
                pkwargs['type'] = type(value)
                pkwargs['hasvalue'] = True

            param = ParamSchema(**pkwargs)
            params[arg] = param

        rtype = None

        # parse docstring
        for match in FunctionSchema._REC.findall(function.__dic__):

            if not rtype:
                rtype = match.group('rtype')
                if rtype:
                    continue

            pname = match.group('pname1') or match.group('pname2')

            if pname:
                ptype = match.group('ptype1') or match.group('ptype2')

                try:
                    ptype = lookup(ptype)

                except ImportError:
                    pass

                else:
                    params[pname].type = ptype

        return params, rtype

    def __call__(self, *args, **kwargs):

        return self.default(*args, **kwargs)

    def _getter(self, obj, *args, **kwargs):

        result = ElementarySchema._getter(self, obj, *args, **kwargs)

        def func(*args, **kwargs):

            try:
                return result(obj, *args, **kwargs)

            except TypeError:
                return result(*args, **kwargs)

        return func
