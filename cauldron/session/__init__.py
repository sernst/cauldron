import os

from cauldron import environ
from cauldron.environ import systems
from cauldron.session.exposed import ExposedProject
from cauldron.session.exposed import ExposedStep
from cauldron.session.writing import file_io

project = ExposedProject()
step = ExposedStep()


def initialize_results_path(results_path: str):
    """..."""
    dest_path = environ.paths.clean(results_path)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    web_src_path = environ.paths.resources('web')
    for item in os.listdir(web_src_path):
        item_path = os.path.join(web_src_path, item)
        out_path = os.path.join(dest_path, item)

        systems.remove(out_path, max_retries=10)
        file_io.copy(file_io.FILE_COPY_ENTRY(
            source=item_path,
            destination=out_path
        ))
