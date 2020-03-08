########
Cyberbox
########

.. contents:: Contents:
    :depth: 3

************
Installation
************

To install package locally firstly you need to install these:

#. Python 3.7. You can install it with `pyenv <https://github.com/pyenv/pyenv>`_.
   I suggest also to install `virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_ plugin.
#. `Poetry <https://python-poetry.org/docs/basic-usage/>`_ to manage dependencies.

.. code-block:: bash

    pyenv install 3.7.4
    pyenv virtualenv 3.7.4 cyberbox
    # in project root directory:
    pyenv local cyberbox
    # now virtualenv cyberbox should be active
    poetry install

If you had active virtualenv while running ``poetry install`` one of following commands
should work:

.. code-block:: bash

    poetry run uvicorn --version
    uvicorn --version

So if first command is working and second is not, it means you should prepend all commands with
``poetry run``. That`s why I suggested a way to install packages to local virtualenv so there is
no need to call ``poetry run`` every time.

***************
Running backend
***************

Create config file and provide path to it in ``CYBERBOX_CONFIG_FILE`` variable:

.. code-block:: bash

    export CYBERBOX_CONFIG_FILE="$(pwd)/configs/config-dev.yaml"
    # optional step
    python cyberbox/dev/pre_create_data.py
    uvicorn 'cyberbox.asgi:app' --reload

Then go to http://127.0.0.1:8000.

*******
Testing
*******

Tests require database:

.. code-block:: bash

    docker-compose up -d
    export CYBERBOX_TEST_DB_URL="postgresql://testuser:testpass@localhost:6432/cyberbox-test"
    pytest

Also you can install gitlab-runner locally and use it:

.. code-block:: bash

    # gitlab-runner exec <executor> <job-name>
    gitlab-runner exec docker tests

****************************
Building docker image for CI
****************************

Use following commands:

.. code-block:: bash

    docker login registry.gitlab.com
    docker build -f .ci/Dockerfile -t registry.gitlab.com/artslob/cyberbox/ci-image:latest .
    docker push registry.gitlab.com/artslob/cyberbox/ci-image:latest

*****
Stack
*****
Cyberbox made with these tools:

#. `FastAPI <https://fastapi.tiangolo.com>`_ (`starlette <https://www.starlette.io/>`_ +
   `pydanntic <https://pydantic-docs.helpmanual.io/>`_) - asyncio web framework with cool validation
   powered by python type hinting.
#. `encode/databases <https://www.encode.io/databases>`_ for asyncio database interaction
   (alternative to `GINO <https://python-gino.org/>`_).

Testing:

#. `pytest-asyncio <https://github.com/pytest-dev/pytest-asyncio>`_ - pytest plugin for testing
   asyncio code.
#. `encode/httpx <https://www.python-httpx.org/>`_ - asyncio client with support for ability to make
   requests directly to ASGI applications (alternative to
   `async-asgi-testclient <https://github.com/vinissimus/async-asgi-testclient>`_). Asynchronous
   client is used because it allows to interact with database using asyncio like in apps code. But
   this client requires ``asgi-lifespan`` for ASGI events.
#. `asgi-lifespan <https://github.com/florimondmanca/asgi-lifespan>`_ - startup/shutdown of ASGI apps.

************
Useful links
************

#. `<https://github.com/encode/starlette/issues/104>`_
#. `<https://github.com/encode/httpx/issues/350>`_

*****
Notes
*****

#. To view ``.rst`` format use `restview <https://mg.pov.lt/restview/>`_.

   .. code-block:: bash

    # runs restview in background without creating nohup.out file
    nohup restview README.rst > /dev/null 2>&1 &

#. Use following symbols to create headings:

   * H1 - Part - ``#`` with overline
   * H2 - Chapter - ``*`` with overline
   * H3 - Section - ``=``
   * H4 - Subsection - ``-``
   * H5 - Subsubsection - ``^``
   * H6 - Paragraph - ``"``

