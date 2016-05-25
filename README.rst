
Cauldron
========

The un-notebook notebook: an interactive scientific analysis environment.
Cauldron combines the great elements of notebook-style editing:

- `About Cauldron`_
- `Getting Started`_
- `Cauldron Shell`_
- `Example Projects`_
- `First Project`_

About Cauldron
--------------

- **Data Persistence**: Shared variables are stored in memory between
  executions to avoid having to run every step from the beginning each time.
- **Accessible HTML Output**: Output is written to notebook-style formatted
  HTML for efficient display, consumption and sharing.
- **Segmented code execution**: Code is run in distinct steps (just like
  notebook cells), and you control when and which steps are run.

with the best elements of traditional software development:

- **Free From Browser Coding**: Face it, coding in browsers is less than ideal.
- **Your Choice of IDE**: Modern modern IDEs have fantastic productivity
  features such as extensive customization, real-time error checking, intelligent
  code completion and efficient project navigation. Why settle for anything less?
- **All Code Lives as Files**: Ever take a look at the diff for a notebook? Or
  tried to merge notebook conflicts? Code is embedded in data structures that
  obstruct useful version control functionality.

With Cauldron you write code in your choice of interactive development
environment (IDE) or text editor, and run it using the Cauldron shell like a
notebook. The result is an notebook-style HTML output page, without the
traditional drawbacks of notebooks.

Getting Started
---------------

Cauldron is in the early development stages, and so is not yet available on
PyPi. Instead you will need to install pip install directly from the Github
page:

    $ pip install git+https://github.com/sernst/cauldron.git

Once the pip installation is complete, you'll have access to the Cauldron shell
from a terminal. Simply run the command:

    $ cauldron

to start the shell.

Cauldron Shell
--------------

Cauldron is a shell-based program you start from a terminal with the
``cauldron`` command. Once started, the Cauldron shell provides all of the
functionality you need to manage your analysis projects through a collection of
commands. To see a list of available commands and their basic descriptions use
the ``?`` or ``help`` command on the Cauldron prompt:

    <>: ?

or

    <>: help

For more detailed information on a specific command use the ``help`` command
along with the name of the command you wish to learn more about. For example,
to get help on the ``open`` command, you would enter:

    <>: help open

on the Cauldron prompt.

Example Projects
----------------

Cauldron comes bundled with a few example projects for demonstration purposes.
To open one of these projects, use the command:

    <>: open @examples:[EXAMPLE_PROJECT_NAME]

where ``[EXAMPLE_PROJECT_NAME]`` is the name of an existing example project.
The ``@examples:`` prefix is an alias in Cauldron that resolves to the path
where the example files are stored. You can also create your own aliases,
which will be explained in detail later.

Like all commands in Cauldron, the open command supports tab auto-completion. If
you enter the beginning of the command above:

    <>: open @examples:

and hit the tab key with the cursor at the end of the line, Cauldron will give
you a list of the example project subdirectories.

A good example to start would be Cauldron's *hello-world*:

    <>: open @examples:hello-world/

Once this command is run, the hello-world project will be opened and readied
for you to run. The Cauldron shell prompt updates to reflect the open project.
Instead of ``<>:``, which signifies no open project, the prompt should now be
``<hello-world>:``.

If you now enter the ``run`` command without any arguments, all steps (cells)
in the project will run:

    <hello-world>: run

Once complete, you can view the current state of the notebook display with the
show command:

    <hello-world>: show

which opens the current project display file in your default browser.

First Project
-------------

To create your first project run the Cauldron shell command:

    <>: create hello_cauldron @home:

For more details about the create command, use the Cauldron shell command:

    <>: help create

The create command takes two arguments:

1. The name of your new project (``hello_cauldron`` in the example above)
2. The absolute path to the directory where the project will be saved. In the
example above, the ``@home:`` argument is a shortcut to Cauldron's default home
directory, which is ~/cauldron/.

When the example create command above is executed, a *hello_cauldron* project
will be created in the directory *~/cauldron/hello_cauldron/*, with the
scaffolding for the project already written. The create command also
immediately opens the new project, which is ready to run.

