djangorestframework-jwk
======================================

|build-status-image| |pypi-version|

Overview
--------

Easy JSON Web Keys (JWK) for your Django project

Requirements
------------

-  Python (3.6, 3.7, 3.8, 3.9)
-  Django (2.2, 3.0, 3.1)
-  Django REST Framework (3.10, 3.11, 3.12)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install djangorestframework-jwk

Example
-------

TODO: Write example.

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ ./runtests.py

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

Documentation
-------------

To build the documentation, you’ll need to install ``mkdocs``.

.. code:: bash

    $ pip install mkdocs

To preview the documentation:

.. code:: bash

    $ mkdocs serve
    Running at: http://127.0.0.1:8000/

To build the documentation:

.. code:: bash

    $ mkdocs build

.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/maronato/django-rest-framework-jwk.svg?branch=master
   :target: http://travis-ci.org/maronato/django-rest-framework-jwk?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/djangorestframework-jwk.svg
   :target: https://pypi.python.org/pypi/djangorestframework-jwk
