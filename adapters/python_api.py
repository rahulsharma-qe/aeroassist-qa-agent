"""SOLID adapter — the generic, service-agnostic API test engine (runnable).

Reads (service spec + records) -> builds requests -> runs oracles -> pass/fail report.
No endpoint is hardcoded; behaviour is driven entirely by the spec. No LLM.
This is the one adapter executed live (see tests/ and examples/run_demo.py).
"""


def run_api_tests(spec, records, http_client):
    results = []
    for ep in spec["endpoints"]:
        for rec in records:
            path = ep["path"]
            if ep.get("path_params"):
                for k, v in ep["path_params"](rec).items():
                    path = path.replace("{" + k + "}", str(v))
            url = spec["base_url"] + path
            try:
                if ep["method"] == "POST":
                    body = ep["body_from_record"](rec) if ep.get("body_from_record") else None
                    resp = http_client.post(url, json=body)
                elif ep["method"] == "GET":
                    resp = http_client.get(url)
                elif ep["method"] == "DELETE":
                    resp = http_client.delete(url)
                else:
                    results.append((ep["name"], rec["id"], "SKIP", f"unsupported {ep['method']}"))
                    continue
                status = resp.status_code
                body_json = resp.json() if resp.content else {}
                passed = (status in ep["expected_status"]) and ep["oracle"](rec, body_json, status)
                results.append((ep["name"], rec["id"], "PASS" if passed else "FAIL",
                                "ok" if passed else f"got {status}"))
            except Exception as e:  # noqa: BLE001
                results.append((ep["name"], rec["id"], "ERROR", str(e)[:80]))
    return results
