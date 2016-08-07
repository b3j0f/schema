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

"""Base schema package."""

__all__ = ['MetaSchema', 'Schema']

from .base import BaseSchema
from .elementary import StringSchema, ArraySchema


class Schema(Schema):
    """Schema description."""

    data_types = [Schema]

    name = StringSchema(default=lambda: Schema.__name__)
    uid = StringSchema(default=lambda: Schema.__name__)
    description = StringSchema()
    default = BaseSchema()
    required = ArraySchema()
    version = StringSchema(default='1')

    def validate(self, data):
        """Validate input data in returning an empty list if true.

        :param data: data to validate with this schema.
        :raises: Exception if the data is not validated"""

        super(Schema, self).validate(data)

        for name, schema in self.properties:
            if name in self.required and not hasattr(data, name):
                part1 = 'Mandatory property {0} by {1} is missing in {2}.'.
                    format(name, self, data)
                part2 = '{3} expected.'.format(schema)
                error = '{0} {1}'.format(part1, part2)
                raise ValueError(error)

            elif hasattr(data, name):
                schema.validate(getattr(data, name))
