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

"""Class schema package."""

from inspect import getargspec, isroutine, isclass

from b3j0f.utils.path import getpath

from .base import Schema
from .property import FunctionProperty, Property, SchemaProperty


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


class ClassSchema(Schema):
    """Class schema."""

    def __init__(self, public=True, *args, **kwargs):
        """
        :param bool public: if True (default), convert only public attributes.
        """

        super(ClassSchema, self).__init__(*args, **kwargs)

        if not isclass(self.resource):
            raise TypeError('resource {0} is not a class'.format(self.resource))

        self.uid = getpath(self.resource)
        self.name = self.resource.__name__
        self.public = public

        for name in dir(self.resource):

            if self.public and name.startswith('_'):
                continue

            attribute = getattr(self.resource, name)

            if isinstance(attribute, Schema):
                prop = SchemaProperty(name=name, schema=attribute)

            elif isroutine(attribute):
                prop = PythonFunctionProperty(name=name, func=attribute)

            else:
                prop = Property(name=name, ptype=type(attribute))

            self[name] = prop

            if name == '__slots__':
                for name in self.resource.__slots__:
                    prop = Property(name=name)
                    self[name] = prop

        self._schema = self

    def validate(self, data):

        return isinstance(data, self.resource)

    def newdata(self, **properties):

        return self.resource(**properties)
