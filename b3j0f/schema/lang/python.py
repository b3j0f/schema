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

"""Python language schema package."""

__all__ = ['clsschemamaker', 'functionschemamaker']

from inspect import getargspec, isroutine, isclass, getsourcelines

from b3j0f.utils.path import getpath

from .base import Schema
from .elementary import FunctionSchema
from .registry import fromobj


class PythonFunctionProperty(FunctionProperty):
    """Python function property class."""

    def __init__(self, func, *args, **kwargs):

        super(PythonFunctionProperty, self).__init__(*args, **kwargs)

        self.func = func

        try:
            self.args, self.vargs, self.kwargs, self.default = getargspec(func)

        except TypeError:
            self.args, self.vargs, self.kwargs, self.default = (), (), {}, ()

    def __call__(self, instance=None, args=None, kwargs=None):
        """Execute this function property.

        :param instance: func instance if func is a method.
        :param tuple args: func args.
        :param dict kwargs: func kwargs."""

        if args is None:
            args = ()

        if kwargs is None:
            kwargs = {}

        if instance is None:
            result = self.func(*args, **kwargs)

        else:
            result = self.func(instance, *args, **kwargs)

        return result


@registermaker
def clsschemamaker(resource, inline=False, name=None):
    """Default function which make a schema class from a resource.

    :param type resource: input resource is a class.
    :param bool inline: update the resource with schemas.
    :param str name: schema type name to use. Default is resource name.
    :return: if inline, return the updated resource, otherwise return a new
        class.
    :rtype: type
    :raise: TypeError if resource is not a class."""

    result = resource if inline else None

    if not isinstance(resource, type):
        raise TypeError('Wrong type {0}, \'type\' expected'.format(resource))

    if not inline:
        resname = resource.__name__ if name is None else name
        bases = resource.mro()
        if Schema not in bases:
            bases.append(Schema)

        _dict = {}

    for name, member in getmembers(resource):

        if isinstance(member, Schema):
            schema = member

        else:
            try:
                schema = fromobj(member, force=True)

            except TypeError:
                continue

            else:
                if inline:
                    setattr(resource, name, schema)

        if not inline:
            _dict[name] = schema

    if not inline:
        result = type(resname, bases, _dict)

    return result

clsschemamaker(Schema, inline=True)


@registermaker
def functionschemamaker(resource):

    if not isinstance(resource, Callable):
        raise TypeError('Wrong type {0}. Callable expected'.format())

    args, vargs, keywords, default = getargspec(resource)

    params = []

    rargs = args[:-len(default)]
    dargs = map((arg[pos + len(rargs)], default[pos]) for pos in range(len(default)))

    params = map(Schema, rargs) + map(lambda item: Schema(default=val) for arg, val in dargs)

    FunctionSchema(args=None, impl=getsourcelines(resource))
