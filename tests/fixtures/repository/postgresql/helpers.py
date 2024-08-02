"""Repositories helper fixtures."""

import math
import random

import pytest

from app.pkg.settings import settings


@pytest.fixture
def client_id() -> int:
    return math.ceil(random.random() * 10000)


@pytest.fixture
def specific_client_id() -> int:
    return settings.TELEGRAM.TEST_CLIENT_ID
