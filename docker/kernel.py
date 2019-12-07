"""
This file serves as the package entrypoint for kernel execution via
gunicorn. The environment variables are set in the paired kernel-run.py
file where the gunicorn application is called.
"""
import os

from cauldron.cli import server

# Allow for changing the directory as part of the application launch
# action so that this application directory isn't where users start
# when browsing in the user-interface.
os.chdir(os.environ.get('CAULDRON_INITIAL_DIRECTORY') or '.')

kernel_data = server.create_application(
    port=int(os.environ.get('CAULDRON_SERVER_PORT', '8000')),
    debug=False,
    public=True,
    quiet=True
)

# Assign to the application to expose it for gunicorn access
application = kernel_data['application']
