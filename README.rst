########
Cyberbox
########

.. contents:: Contents:
    :depth: 3

*****
About
*****

Cyberbox - REST API для  файлохранилища с возможностью создавать ссылки на файлы.

===========
Реализовано
===========

Общее:

* Alembic: ORM миграции.

Аутентификация:

* Регистрация пользователей. Пользователи по умолчанию создаются заблокированными.
* Логин: отправка имени и пароля - получение ``jwt`` токена. Защищённые ендпоинты проверяют
  валидность токена, время действия токена, заблокирован ли пользователь.

Файлы (доступны только для владельца файлов):

* Просмотр списка.
* Сохранение файла на сервере.
* Загрузка файла с сервера.
* Удаление файла.

Ссылки:

* Создание ссылки на файл (для владельца файла) с опциями:
    * Ограничение времени жизни - параметр ``valid_until``;
    * Сделать одноразовой - параметр ``is_onetime``.
      После загрузки файла по ссылке, ссылка будет удалена;
    * Также у ссылки есть параметр, показывающий сколько раз был загружен по ней файл.
* Загрузка файла по ссылке - любой, у кого есть ссылка.
* Удаление ссылки (для владельца файла).

===========
Реализовать
===========

* Создание админа через коммандную оболочку.
* Возможность блокировать и разблокировать пользователей админу.
* Улучшить фильтрацию списков.
* Проверять соответствие схемы миграций и схемы метадаты.

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

Create config file. Example is ``configs/config-dev-example.yaml``. Validation can be found in
``cyberbox/config.py`` file.

Do **not forget to change secret** key! Use following command to generate new one::

    openssl rand -hex 32

Provide path to config it in ``CYBERBOX_CONFIG_FILE`` variable (also you can create copy of
``export-vars-example.sh`` and source it):

.. code-block:: bash

    export CYBERBOX_CONFIG_FILE="$(pwd)/configs/config-dev.yaml"
    docker-compose up -d
    alembic -c cyberbox/migrations/alembic.ini upgrade head
    python cyberbox/dev/pre_create_data.py  # optional step
    uvicorn 'cyberbox.asgi:app' --reload

Then go to http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc.

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

    tag='registry.gitlab.com/artslob/cyberbox/ci-image:latest'
    docker login registry.gitlab.com
    docker build -f .ci/Dockerfile -t "$tag" .
    docker push "$tag"

*****
Stack
*****
Cyberbox made with these tools:

#. `FastAPI <https://fastapi.tiangolo.com>`_ (`starlette <https://www.starlette.io/>`_ +
   `pydanntic <https://pydantic-docs.helpmanual.io/>`_) - asyncio web framework with cool validation
   powered by python type hinting.
#. `encode/databases <https://www.encode.io/databases>`_ for asyncio database interaction
   (alternative to `GINO <https://python-gino.org/>`_).
#. `aiofiles <https://github.com/Tinche/aiofiles>`_ - asyncio interface for file IO.
#. `SqlAlchemy <https://docs.sqlalchemy.org/en/13/core/tutorial.html>`_ and
   `Alembic <https://alembic.sqlalchemy.org/en/latest/>`_ - sql query builder and migrations.

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
#. `<https://github.com/tiangolo/fastapi/issues/58>`_

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

