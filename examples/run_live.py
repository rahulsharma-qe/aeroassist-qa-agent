"""Live demo — REQUIRES an LLM API key (set LLM_PROVIDER + the matching key in the env / .env).

Runs the full QA agent (generate -> review -> approve-policy -> revise -> data -> validate),
then renders all five stack outputs from the one fresh package. This regenerates artifacts;
it is NOT run in CI (CI uses the committed samples via run_demo.py).
"""
import os
import json

from core.orchestrator import orchestrate
from core.llm import get_client
from examples.oracles import should_refund, is_well_formed
from adapters.rest_assured import to_rest_assured
from adapters.apache_testng import to_apache_testng, REST_CLIENT_STUB, TEST_BASE_STUB
from adapters.bdd_gherkin import to_gherkin
from adapters.playwright import to_playwright

REQUIREMENT = "Passengers can cancel their booking and get a full refund within 24 hours of booking."
OUT = os.path.join(os.path.dirname(__file__), "output")


def main():
    client = get_client()                       # raises a clear error if no key
    package = orchestrate(REQUIREMENT, client=client, human_in_the_loop=False)

    with open(os.path.join(OUT, "package.json"), "w") as f:
        json.dump(package, f, indent=2)

    # render every reference adapter from the SAME package + SAME oracle
    renders = {
        "RefundCancellationTest.java": to_rest_assured(package, should_refund, is_well_formed),
        "RefundCancellationApiTest.java": to_apache_testng(package, should_refund, is_well_formed),
        "RestClient.java": REST_CLIENT_STUB,
        "TestBase.java": TEST_BASE_STUB,
        "refund_cancellation.feature": to_gherkin(package, should_refund, is_well_formed),
        "refund_cancellation.spec.js": to_playwright(package, should_refund, is_well_formed),
    }
    for name, text in renders.items():
        with open(os.path.join(OUT, name), "w") as f:
            f.write(text)
    print(f"\nRegenerated package + {len(renders)} adapter outputs in examples/output/")


if __name__ == "__main__":
    main()
