#!/usr/bin/env python

import circleclient
import pytest
import httpretty


ENDPOINT = 'https://circleci.com/api/v1'


@pytest.fixture(scope='module')
def client():
    return circleclient.CircleClient(api_token='token')


def test_client_has_instances(client):
    assert isinstance(client.user, circleclient.User)
    assert isinstance(client.projects, circleclient.Projects)
    assert isinstance(client.build, circleclient.Build)


def test_client_headers(client):
    headers = client.headers
    assert isinstance(headers, dict)
    assert 'content-type' in headers
    assert 'accept' in headers
    assert 'application/json' == headers['content-type']
    assert 'application/json' == headers['accept']


@pytest.mark.httpretty
def test_get_user_info(client):
    url = ENDPOINT + '/me?circle-token=token'

    httpretty.register_uri(httpretty.GET, url,
        status=200, content_type='application/json',
        body='{"basic_email_prefs": "smart", "login": "qba73"}')

    response = client.user.get_info()

    assert isinstance(response, dict)
    assert response["login"] == 'qba73'


@pytest.mark.httpretty
def test_list_followed_projects(client):
    url = ENDPOINT + '/projects?circle-token=token'

    httpretty.register_uri(httpretty.GET, url,
        status=200, content_type='application/json',
        body='[{"username": "qba73", ' + 
            '"reponame": "circleclient", ' + 
            '"branches": {"master": {"a": "xcv"}}}]')

    builds = client.projects.list_projects()

    assert isinstance(builds, list)
    assert isinstance(builds[0]["branches"], dict)


@pytest.mark.httpretty
def test_trigger_build(client):
    url = ENDPOINT + '/project/qba73/circleclient/tree/master?circle-token=token'

    httpretty.register_uri(httpretty.POST, url,
        status=201,
        content_type='application/json',
        body='{"build_num": 54, "reponame": "mongofinil"}')

    build = client.build.trigger_new('qba73', 'circleclient', 'master')

    assert isinstance(build, dict)


@pytest.mark.httpretty
def test_cancel_build(client):
    url = ENDPOINT + '/project/qba73/circleclient/54/cancel?circle-token=token'

    httpretty.register_uri(httpretty.POST, url, status=201,
        content_type='application/json',
        body='{"build_num": 54, "reponame": "mongofinil"}')

    response = client.build.cancel(username='qba73', project='circleclient',
                                build_num=54)

    assert isinstance(response, dict)
    assert 'reponame'  in response