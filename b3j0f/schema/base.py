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

__all__ = ['Schema', 'getschema']

"""Base schema package."""

from six import add_metaclass, string_types

from b3j0f.conf import Configurable

_SCHEMACLS = []


class MetaSchema(type):
    """Automatically register schemas."""

    def __new__(mcs, name, bases, _dict):

        result = super(MetaSchema, mcs).__new__(mcs, name, bases, _dict)

        if bases != (dict,):
            _SCHEMACLS.append(result)

        return result

@Configurable(paths='schema.conf')
@add_metaclass(MetaSchema)
class Schema(dict):
    """Base class for schema.

    Couple of (key, value) are (Property name and value).
    Referenced schema are instance of Schema.

    other attributes are:

    - name: schema name.
    - uid: schema unique id.
    - resource: schema resource from where it has been loaded.
    - _schema : specific schema object."""

    def __init__(self, resource, properties=None, *args, **kwargs):
        """
        :param resource: resource from where get schema content.
        :param Properties properties: list of Property.
        """

        super(Schema, self).__init__(*args, **kwargs)

        self.resource = resource

        if properties is not None:
            for prop in properties:
                self[prop.name] = prop

    def validate(self, data):
        """Validate input data.

        :param dict data: data to validate with this schema."""

        result = True

        names = set(data)

        for name in self:
            prop = self[name]

            if name not in data and prop.mandatory:
                result = False

            else:
                value = data[name]
                result = prop.validate(value)

            names.remove(name)

            if not result:
                break

        else:
            result = not names

        return result

    def newdata(self, **properties):
        """Instanciate a new data with input properties."""

        result = properties.copy()

        for name in self:

            if name not in properties:

                prop = self[name]

                if prop.mandatory:
                    result[name] = prop

        return result

    def save(self, resource=None):
        """Save this schema in the input resource.

        :param resource: default is this resource.
        """

        if resource is None:
            resource = self.resource

        self._save(resource=resource)

    def _save(self, resource):
        """Method to override in order to save this schema in the input resource
        media.

        :param resource: resource to write this schema.
        """

        raise NotImplementedError()


def getschema(resource, *args, **kwargs):
    """Schema factory.

    Find the right schema class to load input resource.

    :param resource: resource from where load schema.
    :param args: schema args.
    :param kwargs: schema kwargs"""

    for schemacls in _SCHEMACLS:

        try:
            result = schemacls(resource=resource, *args, **kwargs)

        except Exception:
            continue

        break

    else:
        raise ValueError('No parser found for {0}.'.format(resource))

    return result
