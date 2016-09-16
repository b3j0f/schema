Description
-----------

Python schema library agnostic from languages.

.. image:: https://img.shields.io/pypi/l/b3j0f.schema.svg
   :target: https://pypi.python.org/pypi/b3j0f.schema/
   :alt: License

.. image:: https://img.shields.io/pypi/status/b3j0f.schema.svg
   :target: https://pypi.python.org/pypi/b3j0f.schema/
   :alt: Development Status

.. image:: https://img.shields.io/pypi/v/b3j0f.schema.svg
   :target: https://pypi.python.org/pypi/b3j0f.schema/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/b3j0f.schema.svg
   :target: https://pypi.python.org/pypi/b3j0f.schema/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/b3j0f.schema.svg
   :target: https://pypi.python.org/pypi/b3j0f.schema/
   :alt: Supported Python implementations

.. image:: https://img.shields.io/pypi/wheel/b3j0f.schema.svg
   :target: https://travis-ci.org/b3j0f/schema
   :alt: Download format

.. image:: https://travis-ci.org/b3j0f/schema.svg?branch=master
   :target: https://travis-ci.org/b3j0f/schema
   :alt: Build status

.. image:: https://coveralls.io/repos/b3j0f/schema/badge.png
   :target: https://coveralls.io/r/b3j0f/schema
   :alt: Code test coverage

.. image:: https://img.shields.io/pypi/dm/b3j0f.schema.svg
   :target: https://pypi.python.org/pypi/b3j0f.schema/
   :alt: Downloads

.. image:: https://readthedocs.org/projects/b3j0fschema/badge/?version=master
   :target: https://readthedocs.org/projects/b3j0fschema/?badge=master
   :alt: Documentation Status

.. image:: https://landscape.io/github/b3j0f/schema/master/landscape.svg?style=flat
   :target: https://landscape.io/github/b3j0f/schema/master
   :alt: Code Health

Links
-----

- `Homepage`_
- `PyPI`_
- `Documentation`_

Installation
------------

pip install b3j0f.schema

Features
--------

This library provides an abstraction layer for manipulating schema from several languages.

The abstraction layer is a python object which can validate data (properties to validate are object attributes or dictionary items) and be dumped into a dictionary or specific language format.

Supported languages are:

- python
- json
- xsd

It is also possible to generate a schema from a dictionary. And validation rules are fully and easily customisable thanks to using a schema such as a property.

Example
-------

Data Validation
~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import build, validate

   # json format with required subinteger property
   resource = '{"title": "test", "properties": {"subname": {"type": "string", "default": "test"}}, {"subinteger": {"type": "integer"}}, "required": ["subinteger"]}'
   Test = build(resource)

   test = Test(subname='example')

   assert test.subinteger == 0  # instanciation value
   assert Test.subinteger.default == 0  # default value
   assert test.subname == 'example' # instanciation value
   assert Test.subname.default == 'test'  # instanciation value

   error = None
   try:
      test.subname = 2  # wrong setting because subname is not a string

   except TypeError as error:
      pass

   assert error is not None

   assert 'subname' in Test.getschemas()

   validate(Test.subinteger, 1)  # validate property
   validate(test, {'subinteger': 1})  # validate dictionary

   class Sub(object):  # object to validate with required subinteger
      subinteger = 1

   validate(test, Sub)  # validate an object with required subinteger
   validate(test, Sub())

   wrongvalues = [
      '',  # object without subinteger
      {'subinteger': ''},  # wrong data type for subinteger
      {}  # dictionary without the required property subinteger
   ]

   for wrongvalue in wrongvalues:

      error = None
      try:
         validate(test, wrongvalues)

      except TypeError as error:
         pass

      assert error is not None

Schema retrieving
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import register, getbyname, getbyuuid, data2schema

   assert getbyuuid(test.uuid) is None
   assert test not in getbyname(test.name)

   register(test)

   assert test is getbyuuid(test.uuid)

   assert test in getbyname(test.name)

   schema = data2schema(2, name='vint')  # get an integer schema with 2 such as a default value and name vint

   assert schema.default == 2
   assert schema.name == 'vint'

   error = None
   try:
      schema.default = ''

   except TypeError as error:
      pass

   assert error is not None

Schema definition
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import Schema, updatecontent

   @updatecontent  # change public attributes/functionss to schemas
   class Test(Schema):

      subname = 'test'  # specify inner schema such as a string schema with default value 'test'
      subinteger = 1  # speciy inner schema sub as an integer with default value 1

   test = Test()

   test = Test(subname='example')

   assert test.subname == 'example' # instanciation value
   assert Test.subname.default == 'test'  # instanciation value
   assert test.subinteger == 1  # instanciation value
   assert Test.subinteger.default == 1  # default value

   error = None
   try:
      test.subname = 2  # wrong setting because subname is not a string

   except TypeError as error:
      pass

   assert error is not None

   assert 'subname' in Test.getschemas()

Complex Schema definition
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import Schema, ThisSchema, RefSchema, build
   from random import random

   @build(foo=2)  # transform a python class to a schema class with the additional property foo
   class Test(object):

      key = DynamicValue(lambda: random())  # generate a new key at each instanciation
      subtest = ThisSchema(key=3.)  # use this schema such as inner schema
      ref = RefSchema()  # ref is validated by this schema

   assert issubclass(Test, Schema)

   test1, test2 = Test(), Test()

   # check foo
   assert test1.foo == test2.foo == 2

   # check key and subtest properties
   assert test1.key != test2.key
   assert test1.subtest.key == test2.subtest.key == 3.

   # check ref
   assert test1.ref is None
   test1.ref = Test()

   error = None
   try:
      test.ref = 2

   except TypeError as error:
      pass

   assert error is not None

Function schema definition
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import FunctionSchema, ParamSchema, FloatSchema, BooleanSchema, StringSchema, ArraySchema

   @data2schema
   def test(a, b, c=2):  # definition of a shema function. Parameter values and (function) types are defined in the signature and the docstring.
      """
      :param float a: default 0.
      :type b: bool
      :rtype: str
      """

      return a, b, c

   assert isinstance(test, FunctionSchema)
   assert isinstance(test.params, ArraySchema)
   assert isinstance(test.params[0], ParamSchema)
   assert len(test.params) == 3

   assert test.params[0].name == 'a'
   assert test.params[0].mandatory == True
   assert test.params[0].ref is FloatSchema
   assert test.params[0].default is 0.

   assert test.params[1].name == 'b'
   assert test.params[1].ref is BooleanSchema
   assert test.params[1].mandatory is True
   assert test.params[1].default is False

   assert test.params[2].name == 'c'
   assert test.params[2].ref is IntegerSchema
   assert test.params[2].mandatory is False
   assert test.params[2].default is 2

   assert test.rtype is StringSchema

   assert test(1, 2) == 'test'

Generate a schema from a data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import data2schema

   data = {  # data is a dict
      'a': 1
   }

   schemacls = dict2schemacls(data, name='test')

   assert isinstance(schemacls.a, IntegerSchema)
   assert schemacls.a.default is 1
   assert isinstance(schemacls.name, StringSchema)
   assert schemacls.name.default == 'test'

   validate(schemacls(), data)

   class Test(object):  # data is an object
      a = 1

   schemacls = dict2schemacls(data, name='test')

   assert isinstance(schemacls.a, IntegerSchema)
   assert schemacls.a.default is 1
   assert isinstance(schemacls.name, StringSchema)
   assert schemacls.name.default == 'test'

   validate(schemacls(), Test)
   validate(schemacls(), Test())


Schema property getting/setting/deleting customisation such as a property
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class Test(Schema):

      @Schema
      def test(self):
         self.op =  'get'
         return getattr(self, '_test', 1)

      @test.setter
      def test(self, value):
         self.op = 'set'
         self._test = value

      @test.deleter
      def test(self):
         self.op = 'del'
         del self._test

   test = Test()

   # check getter
   assert test.test == 1
   assert test.op == 'get'

   # check setter
   test.test = 2
   assert test.op == 'set'
   assert test.test == 2

   # check deleter
   del test.test
   assert test.op == 'del'
   assert test.test == 1

Perspectives
------------

- wait feedbacks during 6 months before passing it to a stable version.
- Cython implementation.

Donation
--------

.. image:: https://liberapay.com/assets/widgets/donate.svg
   :target: https://liberapay.com/b3j0f/donate
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/schema
.. _Documentation: http://b3j0fschema.readthedocs.org/en/master/
.. _PyPI: https://pypi.python.org/pypi/b3j0f.schema/
