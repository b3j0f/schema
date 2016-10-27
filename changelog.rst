ChangeLog
=========

0.0.9 (2016/08/27)
------------------

- use ParamTypeSchema for function parameters/rtype from where it is impossible to generate a schema.
- enhance error messages.

0.0.8 (2016/08/27)
------------------

- add support of "one of" and "list of" function parameter type and result.

0.0.7 (2016/08/27)
------------------

- fix error message on function rtype error.
- fix recursive definition of rtype/param of functionschema.

0.0.6 (2016/08/26)
------------------

- fix factory.build methods.
- fix python language.
- fix recursive calls of function param/rtype from parent class.

0.0.5 (2016/08/26)
------------------

- fix generation of schema with __slots__.

0.0.4 (2016/08/08)
------------------

- fix schema class without mro (python2).
- raise an exception while trying to import a type defined in a function signature not present in the python execution scope.

0.0.3 (2016/08/08)
------------------

- add definition of function/param schema at the root package.

0.0.2 (2016/08/08)
------------------

- add support for validating object attributes and dictionary items
- add schema generation from a dictionary or object.

0.0.1 (2016/06/06)
------------------

- library creation.
