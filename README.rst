
Cauldron
========

The un-notebook notebook: an interactive scientific analysis environment.
Cauldron combines the great elements of notebook-style editing:

- Data persistence
- Accessible HTML output
- Segmented code execution

with the best elements of traditional software development:

- Your choice of IDE
- Not coding in a Browser
- Code files live as files

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

First Project
-------------

To create your first project run the Cauldron shell command:

    <>: create hello_cauldron @home:

For more details about the create command, use the Cauldron shell command:

    <>: help create

The create command takes two arguments:

1. The name of your new project (``hello_cauldron`` in the example above)
2. The absolute path to the directory where the project will be saved. In the
    example above, the ``@home:`` argument is a shortcut to Cauldron's default
    home directory, which is ~/cauldron/.

When the example create command above is executed, a *hello_cauldron* project
will be created in the directory *~/cauldron/hello_cauldron/*, with the
scaffolding for the project already written. The create command also
immediately opens the new project, which is ready to run.

