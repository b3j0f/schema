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

"""Main package."""

from .version import __version__

from .lang import (
    build, getresource, SchemaFactory, SchemaBuilder, getschemacls,
    XSDSchemaBuilder
)
from .base import Schema, DynamicValue
from .registry import register, registercls, getbyuuid, getbyname
from .utils import (
    validate, dump, updatecontent, ThisSchema, data2schema, AnySchema,
    data2schemacls, RegisteredSchema, RefSchema
)
from .elementary import (
    StringSchema, DateTimeSchema, IntegerSchema, NumberSchema, LongSchema,
    ComplexSchema, FloatSchema, ArraySchema, DictSchema, TypeSchema,
    EnumSchema, BooleanSchema, ElementarySchema, OneOfSchema
)

__all__ = [
    '__version__', 'Schema', 'DynamicValue',
    'register', 'registercls', 'getbyuuid', 'getbyname',
    'StringSchema', 'IntegerSchema',
    'FloatSchema', 'ComplexSchema', 'EnumSchema', 'ArraySchema',
    'DictSchema', 'DateTimeSchema', 'NumberSchema', 'BooleanSchema',
    'TypeSchema', 'AnySchema', 'OneOfSchema',
    'data2schemacls',
    'data2schema', 'validate', 'dump', 'updatecontent', 'ThisSchema',
    'RefSchema', 'AnySchema', 'RegisteredSchema',
    'ElementarySchema', 'LongSchema',
    'SchemaFactory', 'getschemacls', 'getresource', 'SchemaBuilder', 'build',
    'XSDSchemaBuilder'
]
