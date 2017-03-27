import requests
from requests import Response as HttpResponse
from cauldron import environ


def assemble_url(
        endpoint: str,
        remote_connection: 'environ.RemoteConnection' = None
) -> str:
    """
    Assembles a fully-resolved remote connection URL from the given endpoint
    and remote_connection structure. If the remote_connection is omitted, the
    global remote_connection object stored in the environ module will be
    used in its place.

    :param endpoint:
        The endpoint for the API call
    :param remote_connection:
        The remote connection definition data structure
    :return:
        The fully-resolved URL for the given endpoint
    """

    url_root = (
        remote_connection.url
        if remote_connection else
        environ.remote_connection.url
    )
    url_root = url_root if url_root else 'localhost:5010'

    parts = [
        'http://' if not url_root.startswith('http') else '',
        url_root.rstrip('/'),
        '/',
        endpoint.lstrip('/')
    ]

    return ''.join(parts)


def parse_http_response(http_response: HttpResponse) -> 'environ.Response':
    """
    Returns a Cauldron response object parsed from the serialized JSON data
    specified in the http_response argument. If the response doesn't contain
    valid Cauldron response data, an error Cauldron response object is
    returned instead.

    :param http_response:
        The response object from an http request that contains a JSON
        serialized Cauldron response object as its body
    :return:
        The Cauldron response object for the given http response
    """

    try:
        response = environ.Response.deserialize(http_response.json())
    except Exception as error:
        response = environ.Response().fail(
            code='INVALID_REMOTE_RESPONSE',
            error=error,
            message='Invalid HTTP response from remote connection'
        ).console(
            whitespace=1
        ).response

    response.http_response = http_response
    return response


def get_request_function(data: dict = None, method: str = None):
    """ """

    default_method = 'post' if data else 'get'
    return getattr(requests, method.lower() if method else default_method)


def send_request(
        endpoint: str,
        data: dict = None,
        remote_connection: 'environ.RemoteConnection' = None,
        method: str = None,
        **kwargs
) -> 'environ.Response':
    """ """

    url = assemble_url(endpoint, remote_connection)
    func = get_request_function(data, method)

    try:
        http_response = func(url, json=data, **kwargs)
    except Exception as error:
        return environ.Response().fail(
            code='CONNECTION_ERROR',
            error=error,
            message='Unable to communicate with the remote connection'
        ).console(
            whitespace=1
        ).response

    return parse_http_response(http_response)


def download_file(
        filename: str,
        save_path: str,
        remote_connection: 'environ.RemoteConnection' = None
) -> 'environ.Response':
    """ """

    url = assemble_url(
        '/download/{}'.format(filename),
        remote_connection=remote_connection
    )

    try:
        http_response = requests.get(url, stream=True)
    except Exception as error:
        return environ.Response().fail(
            code='CONNECTION_ERROR',
            error=error,
            message='Unable to communicate with the remote download connection'
        ).console(
            whitespace=1
        ).response

    try:
        with open(save_path, 'wb') as f:
            for chunk in http_response.iter_content(2048):
                if chunk:
                    f.write(chunk)
    except Exception as error:
        return environ.Response().fail(
            code='WRITE_ERROR',
            error=error,
            message='Unable to write data to "{}"'.format(save_path)
        ).console(
            whitespace=1
        ).response

    return environ.Response()
