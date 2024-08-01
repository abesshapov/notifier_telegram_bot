"""Repositories helper fixtures."""

import math
import random

import pytest


@pytest.fixture
def client_id() -> int:
    return math.ceil(random.random() * 10000)
