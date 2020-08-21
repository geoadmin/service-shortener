from urllib.parse import urlparse

from boto3.dynamodb.conditions import Key
from flask import abort

from app.helpers.response_generation import make_error_msg
from app import app

config = app.config


def check_params(scheme, host, url, base_path):
    if url is None:
        abort(make_error_msg(400, 'url parameter missing from request'))
    hostname = urlparse(url).hostname
    if hostname is None:
        abort(make_error_msg(400, 'Could not determine the query hostname'))
    domain = ".".join(hostname.split(".")[-2:])
    if domain not in config['allowed_domains'] and hostname not in config['allowed_hosts']:
        abort(make_error_msg(400, f'Service shortlink can only be used for {config["allowed_domains"]} domains or '
                                  f'{config["allowed_hosts"]} hosts'))
    if host not in config['allowed_hosts']:
        """
        This allows for compatibility with dev hosts or local builds for testing purpose.
        """
        host_url = ''.join((scheme, '://', host, base_path if 'localhost' not in host else '', '/redirect/'))
    else:
        host_url = ''.join((scheme, '://s.geo.admin.ch/'))

    return host_url


def check_and_get_url_short(table, url):

    response = table.query(
        IndexName="UrlIndex",
        KeyConditionExpression=Key('url').eq(url),
    )
    try:
        return response['Items'][0]['url_short']
    except IndexError:
        return None
