import os
import shutil

from cauldron import environ


def initialize_results_path(results_path: str):
    """

    :param results_path:
    :return:
    """

    dest_path = environ.paths.clean(results_path)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    web_src_path = environ.paths.resources('web')
    for item in os.listdir(web_src_path):
        item_path = os.path.join(web_src_path, item)
        out_path = os.path.join(dest_path, item)

        if os.path.exists(out_path):
            os.remove(out_path)
        shutil.copy2(item_path, out_path)
