Contributing Guide
==================

Welcome! There are many ways to contribute, including submitting bug
reports, improving documentation, submitting feature requests, reviewing
new submissions, or contributing code that can be incorporated into the
project.

Limitations
-----------

We should keep close to these items during development:

* Some companies still use Python 3.7. So it is required to keep compatibility if possible.

Initial setup for local development
-----------------------------------

Install Git
~~~~~~~~~~~

Please follow `instruction <https://docs.github.com/en/get-started/quickstart/set-up-git>`_.

Create a fork
~~~~~~~~~~~~~

If you are not a member of a development team building Horizon HWM Store, you should create a fork before making any changes.

Please follow `instruction <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_.

Clone the repo
~~~~~~~~~~~~~~

Open terminal and run these commands:

.. code:: bash

    git clone https://github.com/MobileTeleSystems/horizon-hwm-store -b develop

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

`pre-commit <https://pre-commit.com/>`_ hooks allows to validate & fix repository content before making new commit.
It allows to run linters, formatters, fix file permissions and so on. If something is wrong, changes cannot be committed.

Firstly, install pre-commit hooks:

.. code:: bash

    pre-commit install --install-hooks

Ant then test hooks run:

.. code:: bash

    pre-commit run

How to
------

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

Build documentation
~~~~~~~~~~~~~~~~~~~

Build documentation using Sphinx:

.. code:: bash

    cd docs
    make html

If documentation should be build cleanly instead of reusing existing build result:

.. code:: bash

    make clean html

Pull Request Process
--------------------

1. Update the README.md with details of changes to the interface,
   including new environment variables, exposed ports, proper file
   locations, and container parameters.
2. Increase the version numbers in any examples files and the README.md
   to the new version that this Pull Request would represent. The
   versioning scheme we use is SemVer.
3. You may merge the Pull Request in once you have the sign-off of two
   other developers, or if you do not have permission to do that, you
   may request the second reviewer to merge it for you. We expect to
   have a minimum of one approval from someone else on the core team.

Review Process
--------------

We keep pull requests open for a few days for multiple people to have
the chance to review/comment.

After feedback has been given, we expect responses within two weeks.
After two weeks, we may close the pull request if it isn't showing any
activity.

Create pull request
~~~~~~~~~~~~~~~~~~~

Commit your changes:

.. code:: bash

    git commit -m "Commit message"
    git push

Then open Github interface and `create pull request <https://docs.github.com/en/get-started/quickstart/contributing-to-projects#making-a-pull-request>`_.
Please follow guide from PR body template.

After pull request is created, it get a corresponding number, e.g. 123 (``pr_number``).

Write release notes
~~~~~~~~~~~~~~~~~~~

``Horizon HWM Store`` uses `towncrier <https://pypi.org/project/towncrier/>`_
for changelog management.

To submit a change note about your PR, add a text file into the
`docs/changelog/next_release <./next_release>`_ folder. It should contain an
explanation of what applying this PR will change in the way
end-users interact with the project. One sentence is usually
enough but feel free to add as many details as you feel necessary
for the users to understand what it means.

**Use the past tense** for the text in your fragment because,
combined with others, it will be a part of the "news digest"
telling the readers **what changed** in a specific version of
the library *since the previous version*.

You should also use
reStructuredText syntax for highlighting code (inline or block),
linking parts of the docs or external sites.
If you wish to sign your change, feel free to add ``-- by
:user:`github-username``` at the end (replace ``github-username``
with your own!).

Finally, name your file following the convention that Towncrier
understands: it should start with the number of an issue or a
PR followed by a dot, then add a patch type, like ``feature``,
``doc``, ``misc`` etc., and add ``.rst`` as a suffix. If you
need to add more than one fragment, you may add an optional
sequence number (delimited with another period) between the type
and the suffix.

In general the name will follow ``<pr_number>.<category>.rst`` pattern,
where the categories are:

- ``feature``: Any new feature
- ``bugfix``: A bug fix
- ``improvement``: An improvement
- ``doc``: A change to the documentation
- ``dependency``: Dependency-related changes
- ``misc``: Changes internal to the repo like CI, test and build changes

A pull request may have more than one of these components, for example
a code change may introduce a new feature that deprecates an old
feature, in which case two fragments should be added. It is not
necessary to make a separate documentation fragment for documentation
changes accompanying the relevant code changes.

Examples for adding changelog entries to your Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rst
    :caption: docs/changelog/next_release/1234.doc.1.rst

    Added a ``:github:user:`` role to Sphinx config -- by :github:user:`someuser`

.. code-block:: rst
    :caption: docs/changelog/next_release/2345.bugfix.rst

    Fixed behavior of ``WebDAV`` connector -- by :github:user:`someuser`

.. code-block:: rst
    :caption: docs/changelog/next_release/3456.feature.rst

    Added support of ``timeout`` in ``S3`` connector
    -- by :github:user:`someuser`, :github:user:`anotheruser` and :github:user:`otheruser`

.. tip::

    See `pyproject.toml <pyproject.toml>`_ for all available categories
    (``tool.towncrier.type``).

.. _Towncrier philosophy:
    https://towncrier.readthedocs.io/en/stable/#philosophy


How to skip change notes check?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just add ``ci:skip-changelog`` label to pull request.

Release Process
^^^^^^^^^^^^^^^

Before making a release from the ``develop`` branch, follow these steps:

0. Checkout to ``develop`` branch and update it to the actual state

.. code:: bash

    git checkout develop
    git pull -p

1. Backup ``NEXT_RELEASE.rst``

.. code:: bash

    cp "docs/changelog/NEXT_RELEASE.rst" "docs/changelog/temp_NEXT_RELEASE.rst"

2. Build the Release notes with Towncrier

.. code:: bash

    VERSION=$(cat horizon_hwm_store/VERSION)
    towncrier build "--version=${VERSION}" --yes

3. Change file with changelog to release version number

.. code:: bash

    mv docs/changelog/NEXT_RELEASE.rst "docs/changelog/${VERSION}.rst"

4. Remove content above the version number heading in the ``${VERSION}.rst`` file

.. code:: bash

    awk '!/^.*towncrier release notes start/' "docs/changelog/${VERSION}.rst" > temp && mv temp "docs/changelog/${VERSION}.rst"

5. Update Changelog Index

.. code:: bash

    awk -v version=${VERSION} '/DRAFT/{print;print "    " version;next}1' docs/changelog/index.rst > temp && mv temp docs/changelog/index.rst

6. Restore ``NEXT_RELEASE.rst`` file from backup

.. code:: bash

    mv "docs/changelog/temp_NEXT_RELEASE.rst" "docs/changelog/NEXT_RELEASE.rst"

7. Commit and push changes to ``develop`` branch

.. code:: bash

    git add .
    git commit -m "Prepare for release ${VERSION}"
    git push

8. Merge ``develop`` branch to ``master``, **WITHOUT** squashing

.. code:: bash

    git checkout master
    git pull
    git merge develop
    git push

9. Add git tag to the latest commit in ``master`` branch

.. code:: bash

    git tag "$VERSION"
    git push origin "$VERSION"

10. Update version in ``develop`` branch **after release**:

.. code:: bash

    git checkout develop

    NEXT_VERSION=$(echo "$VERSION" | awk -F. '/[0-9]+\./{$NF++;print}' OFS=.)
    echo "$NEXT_VERSION" > horizon_hwm_store/VERSION

    git add .
    git commit -m "Bump version"
    git push
