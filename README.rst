.. title

What is Horizon HWM Store?
==========================

|Repo Status| |Build Status| |PyPI License| |PyPI Python Version| |Documentation| |Coverage|

.. |Repo Status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://github.com/MobileTeleSystems/horizon-hwm-store
.. |Build Status| image:: https://github.com/MobileTeleSystems/horizon-hwm-store/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/horizon-hwm-store/actions
.. |PyPI License| image:: https://img.shields.io/pypi/l/horizon-hwm-store.svg
    :target: https://github.com/MobileTeleSystems/horizon-hwm-store/blob/develop/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/horizon-hwm-store.svg
    :target: https://badge.fury.io/py/horizon-hwm-store
.. |Documentation| image:: https://readthedocs.org/projects/horizon-hwm-store/badge/?version=stable
    :target: https://horizon-hwm-store.readthedocs.io/
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/horizon-hwm-store/branch/develop/graph/badge.svg?token=RIO8URKNZJ
    :target: https://codecov.io/gh/MobileTeleSystems/horizon-hwm-store

* ``horizon-hwm-store`` is a Python library to interact with Horizon service by saving and retrieving HWM.

Requirements
------------
* **Python 3.7+**

Documentation
-------------

See https://horizon-hwm-store.readthedocs.io/

.. install

Installation
---------------

.. code:: bash

    pip install horizon-hwm-store

.. develops

Develop
-------

Clone repo
~~~~~~~~~~

Clone repo:

.. code:: bash

    git clone https://github.com/MobileTeleSystems/horizon-hwm-store.git -b develop

    cd horizon-hwm-store

Setup environment
~~~~~~~~~~~~~~~~~

Create virtualenv and install dependencies:

.. code:: bash

    python -m venv venv
    source venv/bin/activate
    pip install -U wheel
    pip install -U pip setuptools
    pip install -U \
        -r requirements.txt \
        -r requirements-dev.txt \
        -r requirements-docs.txt \
        -r requirements-test.txt

Enable pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~~

Install pre-commit hooks:

.. code:: bash

    pre-commit install --install-hooks

Test pre-commit hooks run:

.. code:: bash

    pre-commit run

.. tests

Tests
~~~~~

Start all containers with dependencies:

.. code:: bash

    docker-compose up -d

Load environment variables with connection properties:

.. code:: bash

    source .env.local

Run tests:

.. code:: bash

    ./run_tests.sh

You can pass additional arguments, they will be passed to pytest:

.. code:: bash

    ./run_tests.sh -k sometest -lsx -vvvv --log-cli-level=INFO

Stop all containers and remove created volumes:

.. code:: bash

    docker-compose down -v
