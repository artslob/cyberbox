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

    # in project root
    pyenv install 3.7.4
    pyenv virtualenv 3.7.4 cyberbox
    pyenv local cyberbox
    poetry install

If you had active virtualenv while running ``poetry install`` one of following commands
should work:

.. code-block:: bash

    poetry run uvicorn --version
    uvicorn --version

***************
Running backend
***************

.. code-block:: bash

    uvicorn 'cyberbox.asgi:app' --reload

Then go to http://127.0.0.1:8000.

*****
Notes
*****

#. To view ``.rst`` format use `restview <https://mg.pov.lt/restview/>`_.
#. Use following symbols to create headings:

   * H1 - Part - ``#`` with overline
   * H2 - Chapter - ``*`` with overline
   * H3 - Section - ``=``
   * H4 - Subsection - ``-``
   * H5 - Subsubsection - ``^``
   * H6 - Paragraph - ``"``

