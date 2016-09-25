import sys
import os
import errno
import glob

from cauldron import environ

spark_environment = dict()


def unload():
    """

    :return:
    """

    for existing_path in spark_environment.get('libs', []):
        if existing_path in sys.path:
            sys.path.remove(existing_path)

    for name, module in list(sys.modules.items()):
        if name.startswith('pyspark'):
            del sys.modules[name]


def initialize(spark_home_path: str = None):
    """
    Registers and initializes the PySpark library dependencies so that the
    pyspark package can be imported and used within the notebook.

    If you specify the path to the spark home folder, the PySpark libraries
    from that location will be loaded. If a value is omitted, the $SPARK_HOME
    environmental variable will be used to determine from where to load the
    libraries.

    :param spark_home_path:
        The path to the spark folder on your system. Leave this blank if you
        want to use the $SPARK_HOME environmental variable default instead.
    :return:
    """

    if not spark_home_path:
        spark_home_path = os.environ.get('SPARK_HOME')

    spark_home_path = environ.paths.clean(spark_home_path)

    if not os.path.exists(spark_home_path):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            spark_home_path
        )

    spark_python_path = os.path.join(spark_home_path, 'python')

    if not os.path.exists(spark_python_path):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            spark_python_path
        )

    spark_pylib_path = os.path.join(spark_python_path, 'lib')

    if not os.path.exists(spark_pylib_path):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            spark_python_path
        )

    lib_glob = os.path.join(spark_pylib_path, '*.zip')
    lib_sources = [path for path in glob.iglob(lib_glob)]

    unload()

    for p in lib_sources:
        if p not in sys.path:
            sys.path.append(p)

    spark_environment.update(dict(
        spark_home_path=spark_home_path,
        spark_python_path=spark_python_path,
        spark_pylib_path=spark_pylib_path,
        libs=lib_sources
    ))
