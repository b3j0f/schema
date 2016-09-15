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

The abstraction layer is a python object which can validate data, be dumped into a dictionary.

Supported languages are:

- python
- json
- xsd

Example
-------

Data Validation
~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import build, validate

   resource = '{"title": "test", "properties": {"subname": {"type": "string", "default": "test"}}, {"subinteger": {"type": "integer"}}}'
   Test = build(resource)  # json format

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
   assert 'subname' in test.getschemas()

Schema retrieving
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import register, getbyname, getbyuuid

   assert getbyuuid(test.uuid) is None
   assert test not in getbyname(test.name)

   register(test)

   assert test is getbyuuid(test.uuid)

   assert test in getbyname(test.name)

Schema definition
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from b3j0f.schema import Schema, updatecontent

   @updatecontent
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

   from b3j0f.schema import Schema, updatecontent, ThisSchema, RefSchema, FunctionSchema, build, FloatSchema, BooleanSchema, StringSchema
   from random import random

   @build(foo=2)  # transform a python class to a schema class with the additional property foo
   class Test(object):

      key = DynamicValue(lambda: random())  # generate a new key at each instanciation
      subtest = ThisSchema(key=3.)  # use this schema such as inner schema
      ref = RefSchema()  # ref is validated by this schema

      def test(self, a, b, c=2):
         """
         :param float a:
         :type b: bool
         :rtype: str
         """

         return 'test'

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

   @build  # transform a python class to a schema class
   class Test(object):

      def test(self, a, b, c=2):  # definition of a shema function. Parameter values and (function) types are defined in the signature and the docstring.
         """
         :param float a: default 0.
         :type b: bool
         :rtype: str
         """

         return 'test'

   assert isinstance(Test.test, FunctionSchema)
   assert isinstance(Test.test.params, ArraySchema)
   assert isinstance(Test.test.params[0], ParamSchema)
   assert len(Test.test.params, 4)

   assert Test.test.params[0].name == 'self'
   assert Test.test.params[0].mandatory == True
   assert Test.test.params[0].ref is None
   assert Test.test.params[0].default is None

   assert Test.test.params[1].name == 'a'
   assert Test.test.params[1].mandatory == True
   assert Test.test.params[1].ref is FloatSchema
   assert Test.test.params[1].default is 0.

   assert Test.test.params[2].name == 'b'
   assert Test.test.params[2].ref is BooleanSchema
   assert Test.test.params[2].mandatory is True
   assert Test.test.params[2].default is False

   assert Test.test.params[3].name == 'c'
   assert Test.test.params[3].ref is IntegerSchema
   assert Test.test.params[3].mandatory is False
   assert Test.test.params[3].default is 2

   assert Test.test.rtype is StringSchema

   assert test1.test(1, 2) == 'test'

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
