from functools import wraps
from flask import request
from flask import Response
from flask import abort

from cauldron.cli.server import run as server_runner


@server_runner.APPLICATION.errorhandler(401)
def custom_401(*args, **kwargs):
    return Response('Invalid authorization', 401)


def gatekeeper(func):
    """ 
    This function is used to handle authorization code authentication of 
    protected endpoints. This form of authentication is not recommended 
    because it's not very secure, but can be used in places where SSH 
    tunneling or similar strong connection security is not possible.
    
    The function looks for a special "Cauldron-Authentication-Code" header
    in the request and confirms that the specified value matches the code
    that was provided by arguments to the Cauldron kernel server. This function
    acts as a pass-through if no code is specified when the server starts.
    """

    @wraps(func)
    def check_identity(*args, **kwargs):
        code = server_runner.authorization['code']
        comparison = request.headers.get('Cauldron-Authentication-Code')

        return (
            abort(401)
            if code and code != comparison else
            func(*args, **kwargs)
        )

    return check_identity
