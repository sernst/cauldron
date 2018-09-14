# Getting Started running Cauldron in Docker Containers

Cauldron supports running in docker containers for both local and remote workflows. There are 3 officially supported docker containers available at:

https://hub.docker.com/r/swernst/cauldron/tags/

They are:

* `standard`: Includes the Python 3.6 distribution in an Ubuntu environment.
* `conda`: Includes the full Anaconda distribution of Python 3.6 built upon Anaconda's official docker image.
* `miniconda`: Includes the slimmed-down mini Anaconda distribution of Python 3.6 built upon Anaconda's official docker image.

In all three cases, Cauldron is pre-installed with dependencies and the default command for each container is to start the Cauldron kernel on the exposed port 5010. One of these containers can be pulled using the docker pull command:

<pre>$ docker pull swernst/cauldron:latest-standard</pre>

If you do not specify a specific tag, the latest standard image will be used. Once the image has been pulled, you can start a Cauldron kernel:

<pre>$ docker run -d --rm -p 5010:5010 swernst/cauldron:latest-standard</pre>

After the container starts, you can access the kernel through the exposed 5010 port. If you are using the desktop application, you can connect to this container locally by specifying the local kernel URL, http://127.0.0.1:5010 instead of a Python executable path.


The Cauldron command shell also allows you drive the kernel by connecting to it from a locally running Cauldron shell. To do this, you use the `connect` command:

<pre><>: connect http://127.0.0.1:5010</pre>

ed, all shell commands you issue, e.g. opening a project, will be relayed to the kernel. All project files will be synchronized between the local environment and the kernel's environment. This means you can interact with a local project exactly like you normally would, but all of the execution will happen in the kernel's environment, not your local one.

