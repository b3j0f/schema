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

__all__ = ['clsschemamaker', 'FunctionSchema']

from re import compile as re_compile

from b3j0f.utils.version import OrderedDict

from ..factory import registermaker, getschemacls
from ..base import Schema


@registermaker
def clsschemamaker(resource, name=None):
    """Default function which make a schema class from a resource.

    :param type resource: input resource is a class.
    :param str name: schema type name to use. Default is resource name.
    :param type schemacls: sub class of schema to inherit from.
    :rtype: type
    :raise: TypeError if resource is not a class."""

    if not isinstance(resource, type):
        raise TypeError('Wrong type {0}, \'type\' expected'.format(resource))

    if issubclass(resource, Schema):
        result = resource

    else:
        try:
            result = getschemacls(resource)

        except KeyError:
            resname = resource.__name__ if name is None else name
            result = type(resname, (Schema, resource), {})

    return result



class FunctionSchema(ElementarySchema):
    """Function schema.

    Dedicated to describe functions, methods and lambda objects."""

    class ParamSchema(Schema):
        """Function parameter schema."""

        type = object
        hasvalue = False

    PDESC = r':param (?P<ptype1>[\w_]+) (?P<pname1>\w+):'
    PTYPE = r':type (?P<pname2>[\w_]+):(?P<ptype2>[^\n]+)'
    RTYPE = r':rtype:(?P<rtype>[^\n]+)'

    rec = re_compile('{0}|{1}|{2}'.format(PDESC, PTYPE, RTYPE))

    __data_types__ = [FunctionType, MethodType, LambdaType]

    params = ArraySchema(item_type=ParamSchema)
    rtype = TypeSchema(nullable=True, default=None)
    impl = ''
    fget = This()
    fset = This()
    fdel = This()

    def validate(self, data, *args, **kwargs):

        result = super(FunctionSchema, self).validate(
            data=data, *args, **kwargs
        )

        if result:

            args, vargs, kwargs, default = getargspec(data)

            for param in self.params:
                if param.validate(args, )

            params = []

            indexlen = len(args) - (0 if default is None else len(default))

            for index, arg in enumerate(args):

                pkwargs = {name: arg}  # param kwargs
                if index == indexlen:
                    value = default[index - len(default)]
                    pkwargs['default'] = value
                    pkwargs['type'] = type(value)
                    pkwargs['hasvalue'] = True
                    indexlen += 1

                param = FunctionSchema.ParamSchema(**pkwargs)
                params.append(param)

        return result

    def _setvalue(self, schema, value, *args, **kwargs):

        if schema.name == 'default':

            self.params = FunctionSchema._getparams(value)


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

            pkwargs = {name: arg}  # param kwargs

            if index >= indexlen:  # has default value
                value = default[index - indexlen]
                pkwargs['default'] = value
                pkwargs['type'] = type(value)
                pkwargs['hasvalue'] = True

            param = FunctionSchema.ParamSchema(**pkwargs)
            params[arg] = param

        rtype = None

        # parse docstring
        for match in FunctionSchema.rec.findall(function.__dic__):

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
