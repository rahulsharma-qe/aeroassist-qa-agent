"""Deterministic engine test — runs in CI, needs NO API key.

Loads the committed sample package, runs the generic engine against the mock SUT, and asserts
every generated test passes. Also asserts the committed data is clean per the rules layer.
"""
import json
import os
import pytest
from fastapi.testclient import TestClient

from examples.sut.app import app
from examples.service_spec import AEROASSIST_SPEC
from adapters.python_api import run_api_tests
from core.validate_data import validate_data_rules

HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(HERE)


@pytest.fixture(scope="module")
def package():
    with open(os.path.join(ROOT, "examples", "output", "package.json")) as f:
        return json.load(f)


def test_committed_data_passes_rules(package):
    assert validate_data_rules(package["data"]) == []


def test_engine_all_green(package):
    client = TestClient(app)
    report = run_api_tests(AEROASSIST_SPEC, package["data"], client)
    failures = [r for r in report if r[2] != "PASS"]
    assert not failures, f"non-passing tests: {failures}"
    # 6 records x 2 endpoints
    assert len(report) == len(package["data"]) * len(AEROASSIST_SPEC["endpoints"])
