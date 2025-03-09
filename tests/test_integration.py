import pytest
import os
from testcontainers.compose import DockerCompose
import requests
import time
from tests.fixtures.zitadel import ZitadelIntegration

compose = DockerCompose(context=".", compose_file_name="docker-compose.yaml")
zitadel = ZitadelIntegration()


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    compose.start()

    def teardown():
        # TODO: enable stop after setup
        # compose.stop()
        pass

    request.addfinalizer(teardown)
    zitadel.load_pat()

    # prepare zitadel projects, applications and users
    zitadel.create_project("integration-test")


def test_yarp():
    pass


def test_second():
    pass
