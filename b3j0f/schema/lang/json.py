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

__all__ = ['JSONSchemaBuilder']

from copy import deepcopy

from ..base import Schema
from .python import FunctionSchema
from .factory import SchemaBuilder
from ..elementary import (
    ElementarySchema,
    NoneSchema,
    NumberSchema, IntegerSchema, FloatSchema, LongSchema, ComplexSchema,
    BooleanSchema,
    ArraySchema, DictSchema,
    EnumSchema,
    StringSchema,
    DateTimeSchema
)

from json import loads, dump

from jsonschema import validate


_SCHEMASBYJSONNAME = {
    'null': NoneSchema,
    'integer': IntegerSchema,
    'number': FloatSchema,
    'long': LongSchema,
    'complex': ComplexSchema,
    'float': FloatSchema,
    'string': StringSchema,
    'array': ArraySchema,
    'dict': DictSchema,
    'boolean': BooleanSchema,
    'function': FunctionSchema,
    'datetime': DateTimeSchema,
    'enum': EnumSchema,
    'object': Schema,
    'datetime': DateTimeSchema
}

_PARAMSBYNAME = {
    'defaultValue': 'default',
    'title': 'name',
    'id': 'uuid'
    'items': 'items'
}


class JSONSchemaBuilder(SchemaBuilder):

    __name__ = 'json'

    def build(self, resource):

        if isinstance(resource, string_types):
            fresource = loads(resource)

        _resource = deepcopy(resource)

        def _fill(resource):

            name = resource.pop('title')

            _type = _resource.pop('type')

            schemacls = _SCHEMASBYJSONNAME[_type]

            properties = _resource.pop('properties', {})

            kwargs = {}

            for name, prop in properties.items():

                if name in _PARAMSBYNAME:
                    name = _PARAMSBYNAME[name]

                kwargs[name] = _fill(prop)

            return schemacls(**kwargs)

        schema = _fill(_resource)

        return type(schema)

    def getresource(self, schemacls):

        def _getdict(schema):

            result = {}

            for innerschema in schema.getschemas():

                if isinstance(innerschema, ElementarySchema):
                    val = getattr(schema, innerschema.name)

                else:
                    val = _getdict(innerschema)

                result[innerschema.name] = val

            return result

        json = _getdict(schemacls)

        dump = dumps(json)

        return dump
