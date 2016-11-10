Cauldron
========

The un-notebook notebook: an interactive scientific analysis environment.


.. image:: https://badge.fury.io/py/cauldron-notebook.svg
   :target: https://badge.fury.io/py/cauldron-notebook

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


- `About Cauldron`_
- `Installation`_
- `Getting Started`_
- `Example Projects`_
- `Tutorial: First Project`_
- `Programming Guide`_
- `Running in Production`_

About Cauldron
--------------

Cauldron combines the crucial workflow of notebook-style editing:

- **Data Persistence**: Shared variables are stored in memory between
  executions to avoid having to run every step from the beginning each time.
- **Accessible HTML Output**: Output is written to notebook-style formatted
  HTML for efficient display, consumption and sharing.
- **Segmented Code Execution**: Code is run in distinct steps (just like
  notebook cells), and you control when and which steps are run.

with the best elements of traditional software development workflow:

- **Your Choice of IDE**: Modern modern IDEs have excellent productivity
  features like extensive customization, real-time error checking,
  intelligent code completion and efficient project navigation. Use whichever
  one works best for you.
- **Straight to Production**: Cauldron projects can be run in non-interactive
  mode as well as run from inside other python applications, which makes it
  easy to *productionize* and deploy an analysis when it's ready.
- **Clean Version Control**: Common version control actions like diff-ing and
  merging are obstructed when the code is embedded in notebook files. In
  Cauldron, where code is stored in independent code files, you can take full
  advantage of version control functionality.
- **Pull Request & Code Review Friendly**: Embedded notebook code also makes reviews
  cumbersome to say the least. Cauldron's independent code files provide all
  of the flexibility available to traditional code review.
- **Variable Scope Management**: Variables in Cauldron are locally scoped unless
  explicitly shared. This prevents polluting the notebook with global variables
  and the many potential errors that come from sharing all variables in a non-linear
  computational environment.

With Cauldron you write code in your choice of interactive development
environment (IDE) or text editor, and run it using the Cauldron shell like a
notebook. The result is a notebook-style HTML output page, without the
traditional drawbacks of notebooks.

Installation
------------

The latest release of Cauldron is available from both PyPi::

    $ pip install cauldron-notebook

and Anaconda::

   $ conda install -c sernst cauldron

Because Cauldron is still in the early stages of development and rapidly
evolving, the latest releases can lag behind the development version. If you
want keep up with the latest developments, install directly from the Github
page instead of from PyPi::

    $ pip install git+https://github.com/sernst/cauldron.git

Or you can install in development mode if you want to manage updates using git
instead of pip. To install in that way, clone a local copy of this repository
to your local machine and, inside a terminal, ``cd`` into your local copy
directory and run the command::

    $ python3 setup.py develop

Getting Started
---------------

Cauldron is a shell-based program you start from a terminal. For installations
that support python script installation you can start Cauldron
once the installation is complete with the ``cauldron`` command::

    $ cauldron

or on Windows using the ``cauldron.exe`` command:

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

Programming Guide
-----------------

There are a few key concepts when programming Cauldron notebooks that differ from traditional
notebooks. The first is the display. Anything that you want to appear in the notebook from
text to graphs, must be added to the notebook display:

.. code-block:: python3

   from cauldron import cd

   cd.display.text('Hello World!')

You access the display from the imported cauldron library as shown in the code example above. The one
exception is that Python's built-in **print** function will also add text to the display in a monospaced
font that preserves whitespace just like printing to a console.

The different display functions that can be used for displaying different types of content include:

Display Functions
~~~~~~~~~~~~~~~~~

- **bokeh**: Adds a Bokeh plot model/figure

  - model: The model to be added
  - scale: How tall the plot should be in the notebook as a fraction of screen height. A number
    between 0.1 and 1.0.
  - responsive: Whether or not the plot should responsively scale to fill the width of the notebook.
    The default it True.

- **head**: Displays a specified number of elements in a source object of many different possible
  types.

  - source: DataFrames will show *count* rows of that DataFrame. A list, tuple or other
    iterable, will show the first *count* rows. Dictionaries will show *count* keys from the
    dictionary, which will be randomly selected unless you are using an OrderedDict. Strings will
    show the first *count* characters.
  - count: The number of elements to show from the source.

- **header**: Adds a text header to the display with the specified level.

  - header_text: The text to display in the header
  - level: The level of the header, which corresponds to the html header levels, such as
    <h1>, <h2>, ...

- **html**: A string containing an HTML DOM snippet

  - dom: The HTML string to add to the display

- **inspect**: Inspects the data and structure of the source dictionary object and adds the
  results to the display for viewing.

  - source: The dictionary object to be inspected

- **jinja**: Renders the specified jinja template to HTML and adds the output to the display

  - path: The fully-qualified path to the template to be rendered.
  - kwargs: Any keyword arguments that will be use as variable replacements within the template

- **json**: Adds the specified data to the output display window with the specified key. This
  allows you to make available arbitrary JSON-compatible data to the display for runtime use.

  - window_key: The key on the global window object to which this data will be assigned.
  - data: The data to be assigned to the window object. This data must be serializable as
    JSON data.

- **latex**: Add a mathematical equation in latex math-mode syntax to the display. Instead of the
  traditional backslash escape character, the @ character is used instead to prevent backslash
  conflicts with Python strings. For example, \delta would be @delta.

  - source: The string representing the latex equation to be rendered.

- **listing**: An unordered or ordered bulleted list of the specified *source* iterable where
  each element is converted to a string representation for display.

  - source: The iterable to display as a list
  - ordered: Whether or not the list should be ordered. If False, which is the default, an unordered
    bulleted list is created.

- **markdown**: Renders the source string using markdown and adds the resulting HTML to the display

  - source: A markdown formatted string.
  - kwargs: Any variable replacements to make within the string using Jinja2 templating syntax.

- **plotly**: Creates a Plotly plot in the display with the specified data and layout

  - data: The Plotly trace data to be plotted. Or an iterable (list, tuple) of plotly traces
    to be plotted on the same plot.
  - layout: The layout data used for the plot
  - scale: The display scale with units of fractional screen height. A value of 0.5 constrains
    the output to a maximum height equal to half the height of browser window when viewed. Values
    below 1.0 are usually recommended so the entire output can be viewed without scrolling.

- **pyplot**: Creates a matplotlib plot in the display for the specified figure. The size of the
  plot is determined automatically to best fit the notebook.

  - figure: The matplotlib figure to plot. If omitted, the currently active figure will be used.
  - scale: The display scale with units of fractional screen height. A value of 0.5 constrains the
    output to a maximum height equal to half the height of browser window when viewed. Values below
    1.0 are usually recommended so the entire output can be viewed without scrolling.
  - clear: Clears the figure after it has been rendered. This is useful to prevent persisting old
    plot data between repeated runs of the project files. This can be disabled if the plot is going
    to be used later in the project files.
  - aspect_ratio: The aspect ratio for the displayed plot as a two-element list or tuple. The first
    element is the width and the second element the height. The units are "inches," which is an
    important consideration for the display of text within the figure. If no aspect ratio is
    specified, the currently assigned values to the plot will be used instead.

- **svg**: Adds the specified SVG string to the display. If a filename is included, the SVG data
  will also be saved to that filename within the project results folder.

  - svg: The SVG string data to add to the display
  - filename: An optional filename where the SVG data should be saved within the project results
    folder.

- **table**: Adds the specified data frame to the display in a nicely formatted scrolling table

  - data_frame: The pandas data frame to be rendered to a table
  - scale: The display scale with units of fractional screen height. A value of 0.5 constrains the
    output to a maximum height equal to half the height of browser window when viewed. Values below
    1.0 are usually recommended so the entire output can be viewed without scrolling.

- **tail**: The opposite of the **head** function described above. Displays the last *count*
  elements of the *source* object.

  - source: DataFrames will show the last *count* rows of that DataFrame. A list, tuple or other
    iterable, will show the last *count* rows. Dictionaries will show *count* keys from the
    dictionary, which will be randomly selected unless you are using an OrderedDict. Strings will
    show the last *count* characters.
  - count: The number of elements to show from the source.

- **text**: Adds text to the display. If the text is not preformatted, it will be displayed in
  paragraph format. Preformatted text will be displayed inside a pre tag with a monospace font.

  - text: The text to display
  -  preformatted: Whether or not to preserve the whitespace display the text

- **whitespace**: Adds a specified number of lines of whitespace.

  - lines: The number of lines of whitespace to show.

Shared & Local Variables
~~~~~~~~~~~~~~~~~~~~~~~~

Cauldron does not share all variables between cells. Instead all variables are local unless you
explicitly share them using the cauldron shared object. Consider a step (cell) in a notebook with
the following code:

.. code-block:: python3

   import cauldron as cd

   x = 12

And then another step (cell) with the following code:

.. code-block:: python3

   import cauldron as cd

   print(x)

If you run these steps in order the second step will raise an exception because the *x* variable
is not defined in that step. The proper way to share variables between steps is to add them to
the cauldron shared object like this:

.. code-block:: python3

   import cauldron as cd

   cd.shared.x = 12

And then another step (cell) with the following code:

.. code-block:: python3

   import cauldron as cd

   print(cd.shared.x)

In this case the second step will correctly print a value of *12* in the second step.

Running in Production
---------------------

Cauldron is designed to make it easy to run a notebook in a production environment from
within Python or directly from a command line.

When called from within Python the execution would look like this:

.. code-block:: python3

    project_directory = '/directory/of/my/cauldron/notebook/project'
    output_directory = '/save/my/results/in/this/directory'
    logging_path = '/log/data/to/this/filename.log'

    cauldron.run_project(project_directory, output_directory, logging_path)

This will open, run and then close the specified project. The HTML will be exported to the output
directory. The data normally printed to the console will be saved to the specified logging_path
file.

The exact same command can be run from the command line using the ``cauldron`` command and
supplying the necessary arguments::

   $ cauldron --project='/directory/of/my/cauldron/notebook/project' \
              --output='/save/my/results/in/this/directory' \
              --log='/log/data/to/this/filename.log'

This does exactly the same thing as the python script shown above, but can be called directly from
a terminal or added to a shell script.
