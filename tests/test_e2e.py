import pytest
import os
from testcontainers.compose import DockerCompose


compose = DockerCompose(context=".", compose_file_name="docker-compose.yaml")


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    compose.start()

    def teardown():
        compose.stop()

    request.addfinalizer(teardown)


def test_yarp():
    pass


def test_second():
    pass
