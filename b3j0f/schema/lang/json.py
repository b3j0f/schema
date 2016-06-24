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

"""json schema module."""

from __future__ import absolute_import

__all__ = ['JSONProperty', 'JSONSchema']

from ..base import Schema
from ..prop import Property

from json import loads, load, dump

from jsonschema import validate


class JSONProperty(Property):

    def __init__(self, jsonproperty, *args, **kwargs):

        super(JSONProperty, self).__init__(*args, **kwargs)

        self.jsonproperty = jsonproperty


class JSONSchema(Schema):
    """Schema for json resources."""

    def __init__(self, *args, **kwargs):

        super(JSONSchema, self).__init__(*args, **kwargs)

        try:
            self._schema = loads(self.resource)

        except TypeError:
            with open(self.resource) as jsonfile:
                self._schema = load(jsonfile)

        self.uid = self._schema['id']

        for name in self._schema['property']:

            jsonproperty = self._schema['property'][name]

            self[name] = JSONProperty(name=name, jsonproperty=jsonproperty)

    def validate(self, data):

        return validate(data, self._schema)

    def save(self, resource):

        with open(resource, "w") as rstream:
            dump(self._schema, rstream)
