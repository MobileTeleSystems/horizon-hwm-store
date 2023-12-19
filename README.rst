.. title

What is Horizon HWM Store?
==========================

|Build Status| |Coverage| |Documentation| |PyPI|

.. |Build Status| image:: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon-hwm-store/badges/develop/pipeline.svg
    :target: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon-hwm-store/-/pipelines
.. |Coverage| image:: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon-hwm-store/badges/develop/coverage.svg
    :target: https://gitlab.services.mts.ru/bigdata/platform/onetools/horizon-hwm-store/-/graphs/develop/charts
.. |Documentation| image:: https://img.shields.io/badge/docs-latest-success
    :target: https://bigdata.pages.mts.ru/platform/onetools/horizon-hwm-store/
.. |PyPI| image:: https://img.shields.io/badge/pypi-download-orange
    :target: https://artifactory.mts.ru/artifactory/own-onetl-pypi-local/horizon-hwm-store/

* ``horizon-hwm-store`` is a Python library to interact with Horizon service by saving and retrieving HWM.

Requirements
------------
* **Python 3.7+**

Documentation
-------------

See https://bigdata.pages.mts.ru/platform/onetools/horizon-hwm-store/

Wiki page
-------------

.. TDB
.. See https://wiki.bd.msk.mts.ru/display/ONE/horizon-hwm-store

.. install

Installation
---------------

.. code:: bash

    pip install horizon-hwm-store --extra-index-url https://artifactory.mts.ru/artifactory/api/pypi/pip-bigdata/simple

.. develops

Develop
-------

Clone repo
~~~~~~~~~~

Clone repo:

.. code:: bash

    git clone git@gitlab.services.mts.ru:bigdata/platform/onetools/horizon-hwm-store.git -b develop

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
