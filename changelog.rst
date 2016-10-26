ChangeLog
=========

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
