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

.. code-block:: bash

    uvicorn 'cyberbox.asgi:app' --reload

Then go to http://127.0.0.1:8000.

****************************
Building docker image for CI
****************************

Use following commands:

.. code-block:: bash

    docker login registry.gitlab.com
    docker build -f .ci/Dockerfile -t registry.gitlab.com/artslob/cyberbox/ci-image:latest .
    docker push registry.gitlab.com/artslob/cyberbox/ci-image:latest

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

