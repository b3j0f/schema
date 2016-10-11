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

"""json schema module."""

from __future__ import absolute_import, unicode_literals

from copy import deepcopy

from six import string_types

from ..base import Schema
from .python import FunctionSchema
from .factory import SchemaBuilder
from ..utils import updatecontent
from ..elementary import (
    ElementarySchema,
    IntegerSchema, FloatSchema, ComplexSchema, LongSchema,
    BooleanSchema,
    ArraySchema, DictSchema,
    EnumSchema,
    StringSchema,
    DateTimeSchema
)

from json import loads, load, dumps

from os.path import exists

__all__ = ['JSONSchemaBuilder']

_SCHEMASBYJSONNAME = {
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
    'id': 'uuid',
    'items': 'items'
}


def json2schema(resource, name=None):

    name = resource.pop('title', name)

    uuid = resource.pop('id', None)

    stype = resource.pop('type', 'object')

    properties = resource.pop(
        'properties', resource.pop('property', {})
    )

    content = {'name': StringSchema(default=name)}

    if uuid:
        content['uuid'] = StringSchema(default=uuid)

    for name, prop in properties.items():

        if name in _PARAMSBYNAME:
            name = _PARAMSBYNAME[name]

        innerschemacls = json2schema(prop, name=name)

        content[name] = innerschemacls()

    result = type(str(name), (_SCHEMASBYJSONNAME[stype],), content)

    updatecontent(result)

    return result


class JSONSchemaBuilder(SchemaBuilder):
    """In charge of build json schemas."""

    __name__ = 'json'

    def build(self, _resource, **kwargs):

        if isinstance(_resource, string_types):

            if exists(_resource):
                fresource = load(_resource)

            else:
                fresource = loads(_resource)

        elif isinstance(_resource, dict):
            fresource = deepcopy(_resource)

        else:
            raise TypeError('Wrong type for resource {0}'.format(_resource))

        result = json2schema(fresource)

        updatecontent(result)

        return result

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
