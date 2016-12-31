Cauldron
========

The Unnotebook: The dexterity of a notebook and the wisdom of software
engineering in one data analysis environment


.. image:: https://img.shields.io/pypi/v/cauldron-notebook.svg
   :target: https://pypi.python.org/pypi/cauldron-notebook

.. image:: https://anaconda.org/sernst/cauldron/badges/version.svg
   :target: https://anaconda.org/sernst/cauldron

.. image:: https://travis-ci.org/sernst/cauldron.svg?branch=master
   :target: https://travis-ci.org/sernst/cauldron

.. image:: https://codecov.io/gh/sernst/cauldron/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/sernst/cauldron

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/sernst/cauldron/master/LICENSE

.. image:: https://badges.gitter.im/gitterHQ/gitter.svg
   :target: https://gitter.im/cauldron-notebook/Lobby

The rest of this documentation pertains to the Cauldron CLI. For more
general information about Cauldron, including downloads for the desktop
application, please visit: http://www.unnotebook.com


- `Installation`_
- `Getting Started`_
- `Example Projects`_
- `Tutorial: First Project`_


Installation
------------

The latest release of Cauldron is available from both PyPi::

    $ pip install cauldron-notebook

and Anaconda::

   $ conda install -c sernst cauldron

If you want to use the latest developments, you can install directly from the Github
page instead of from PyPi::

    $ pip install git+https://github.com/sernst/cauldron.git

You can also install in development mode if you want to manage updates using git
instead of pip. To install in that way, clone a local copy of this repository
to your local machine and, inside a terminal, ``cd`` into your local copy
directory and run the command::

    $ python3 setup.py develop

Or in an Anaconda installation using its develop command::

   $ conda develop .

which must be executed in the root project directory of your local copy of
Cauldron.

Getting Started
---------------

Cauldron can be used as either through its Command Line Interface (CLI) or with
the Cauldron desktop application. For more information about the desktop
application visit http://www.unnotebook.com where you can find the download
links and documentation. The rest of this README describes using Cauldron
directly from the command line.

Cauldron is a shell-based program you start from a terminal. For installations
that support python script installation you can start Cauldron
once the installation is complete with the ``cauldron`` command::

    $ cauldron

or on Windows using the ``cauldron.exe`` command::

    % cauldron.exe

For installations where the installation of scripts was not permitted, you can
start Cauldron from within a Python shell. To do this import cauldron and
run the ``cauldron.run_shell()`` function as follows::

    >>> import cauldron
    >>> cauldron.run_shell()

Once started, the Cauldron shell provides all of the functionality you need to
manage your analysis projects through a collection of commands. To see a list
of available commands and their basic descriptions use the ``?`` or ``help``
command on the Cauldron prompt::

    <>: ?

or::

    <>: help

For more detailed information on a specific command use the ``help`` command
along with the name of the command you wish to learn more about. For example,
to get help on the ``open`` command, you would enter::

    <>: help open

on the Cauldron prompt.

Example Projects
----------------

Cauldron comes bundled with a few example projects for demonstration purposes.
To open one of these projects, use the command::

    <>: open @examples:[EXAMPLE_PROJECT_NAME]

where ``[EXAMPLE_PROJECT_NAME]`` is the name of an existing example project.
The ``@examples:`` prefix is an alias in Cauldron that resolves to the path
where the example files are stored. You can also create your own aliases,
which will be explained in detail later.

Like all commands in Cauldron, the open command supports tab auto-completion.
If you enter the beginning of the command above::

    <>: open @examples:

and hit the tab key with the cursor at the end of the line, Cauldron will give
you a list of the example project subdirectories.

A good example to start would be Cauldron's *hello_cauldron*::

    <>: open @examples:hello_cauldron/

Once this command is run, the hello_cauldron project will be opened and readied
for you to run. The Cauldron shell prompt updates to reflect the open project.
Instead of ``<>:``, which signifies no open project, the prompt should now be
``<hello_cauldron>:``.

If you now enter the ``run`` command without any arguments, all steps (cells)
in the project will run::

    <hello_cauldron>: run

Once complete, you can view the current state of the notebook display with the
show command::

    <hello_cauldron>: show

which opens the current project display file in your default browser. When you
are finished working on a project, you use the close to command::

   <hello_cauldron>: close

This empties all of the information Cauldron has been storing for your project
in memory, and takes you back to the initial command prompt where you started::

   <>:

Tutorial: First Project
-----------------------

This tutorial walks through creating your first project. It mirrors the
**@example:hello_cauldron** project that comes installed with Cauldron.

Create New Project
~~~~~~~~~~~~~~~~~~

To create your first project run the Cauldron shell command::

    <>: create hello_cauldron @home:

For more details about the create command, use the Cauldron shell command::

    <>: help create

The create command takes two arguments:

#. The name of your new project (``hello_cauldron`` in the example above)
#. The absolute path to the directory where the project will be saved. In the
   example above, the ``@home:`` argument is a shortcut to Cauldron's default
   home directory, which is ~/cauldron/.

When the example create command above is executed, a *hello_cauldron* project
will be created in the directory *~/cauldron/hello_cauldron/*, with the
scaffolding for the project already written. The create command also
immediately opens the new project in the shell.

Add First Code Step
~~~~~~~~~~~~~~~~~~~

Now that the project has been created, you need to add some code to it. To
do that, use the ``steps add`` command::

    <hello_cauldron>: steps add create_data.py

This will create a new step called *S01-create_data.py* in your project
directory and add it to the Cauldron project. Notice that the name you gave
the step and the one actual step name are different. There's an *S01-* prefix
added to the file. This prefix is added automatically by Cauldron to help you
organize your files. You can disable this feature when you create a project if
you really want to manage the names all yourself, but we'll get into that in
an advanced tutorial.

The step file you created is ready to be modified. Open the
*S01-create_data.py* step file in your choice of Python code editor. You'll
find the file in the project directory, which is *~/cauldron/hello_cauldron/*.
Add the following code to the *S01-create_data.py* file:

.. code-block:: python3

    import numpy as np
    import pandas as pd
    import cauldron as cd

    df = pd.DataFrame(
        np.random.randn(10, 5),
        columns=['a', 'b', 'c', 'd', 'e']
    )

    cd.display.header('Random Data Frame:')
    cd.display.table(df)

    cd.shared.df = df

Once you've saved that code to the *S01-create_data.py* file, you can run your
project using the ``run`` command::

    <hello_cauldron>: run

Then use the ``show`` command to see the results::

    <hello_cauldron>: show

The project display file will open in your default browser.

Add Another Step
~~~~~~~~~~~~~~~~

Now we'll add another code step to plot each column in our DataFrame. Once
again use the steps command::

    <hello_cauldron>: steps add plot_data.py

Open the *S02-plot_data.py* step file and add the following code:

.. code-block:: python3

    import matplotlib.pyplot as plt
    import cauldron as cd

    df = cd.shared.df

    for column_name in df.columns:
        plt.plot(df[column_name])

    plt.title('Random Plot')
    plt.xlabel('Indexes')
    plt.ylabel('Values')

    cd.display.pyplot()

We used matplotlib for this tutorial, but Cauldron also supports Seaborn,
Bokeh, Plotly or any other Python plotting library that can produce an HTML
output. There are Cauldron example projects showing how to plot using each of
these libraries.

Now run the project again::

    <hello_cauldron>: run

You'll notice that the shell output looks like::

    === RUNNING ===
    [S01-create_data.py]: Nothing to update
    [S02-plot_data.py]: Updated

The *S01-create_data.py* step was not run because it hasn't been modified since
the last time you executed the ``run`` command. Just like other notebooks, the
results of running a step (cell) persist until you close the project and do not
need to be updated each time. Cauldron watches for changes to your files and
only updates steps if the files have been modified, or an early step was
modified that may affect their output.

Now you can view the updated project display simply by refreshing your browser.
However, if you already closed the project display browser window, you can show
it again at any time with the ``show`` command.

And that's that. You've successfully created your first Cauldron project. You
can close your project with the ``close`` command::

   <hello_cauldron>: close

Or, if you want to exit the Cauldron shell at any time, use the ``exit``
command::

   <>: exit

See Cauldron's documentation at http://www.unnotebook.com/docs/ for more
information.
