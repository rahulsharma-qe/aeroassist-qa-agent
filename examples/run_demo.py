"""Deterministic demo — NO API KEY NEEDED.

Loads the committed sample package (examples/output/package.json), runs the generic engine
against the mock SUT, and prints a pass/fail report. This is what CI runs.
"""
import json
import os
from fastapi.testclient import TestClient

from examples.sut.app import app
from examples.service_spec import AEROASSIST_SPEC
from adapters.python_api import run_api_tests

HERE = os.path.dirname(__file__)


def main():
    with open(os.path.join(HERE, "output", "package.json")) as f:
        package = json.load(f)

    client = TestClient(app)
    report = run_api_tests(AEROASSIST_SPEC, package["data"], client)

    from collections import Counter
    tally = Counter(r[2] for r in report)
    print("=" * 60)
    print(f"API TEST RUN - {len(report)} tests across {len(AEROASSIST_SPEC['endpoints'])} endpoints")
    print("summary:", dict(tally))
    print("=" * 60)
    for name, rid, verdict, reason in report:
        mark = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERR ", "SKIP": "SKIP"}[verdict]
        line = f"  [{mark}] {name} {rid}"
        if verdict != "PASS":
            line += f" - {reason}"
        print(line)

    failures = [r for r in report if r[2] != "PASS"]
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
