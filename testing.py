"""EcoSort AI - automated test runner.   Run:  python testing.py

Runs the test files of every subsystem (and the end-to-end test with the real
YOLO model) and prints one summary table:

    python testing.py              # everything
    python testing.py --quick      # skip the real-model test (no torch needed)
    python testing.py --live KEY   # additionally ask the REAL LLM one question
    python testing.py -v           # show each test name

Exit code 0 = everything passed, 1 = at least one failure (handy for CI / Docker).
No API key, GPU or internet is required for the normal run: tests use a fake
detector and a fake LLM.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

#: (label, owner, test file) - one row per team member plus the end-to-end test.
SUITES = [
    ("Subsystem 1 - Dataset & Preprocessing", "Deepa Halapeti", "tests/test_subsystem_1_dataset.py"),
    ("Subsystem 2 - Image Recognition", "Prasad Hule", "tests/test_subsystem_2_recognition.py"),
    ("Subsystem 3 - Recycling Rules & Ask AI", "Mayuresh Kumbhar", "tests/test_subsystem_3_recycling_ai.py"),
    ("Subsystem 4 - Web App & Integration", "Vijay Kathiresan", "tests/test_subsystem_4_web.py"),
    ("End-to-end (real YOLO model)", "whole team", "tests/test_integration.py"),
]


def run_suite(path: str, verbose: bool) -> tuple[int, int, int, str]:
    """Run one pytest file in a child process. Returns (passed, failed, skipped, output)."""
    command = [sys.executable, "-m", "pytest", path, "-q", "--no-header", "-p", "no:cacheprovider"]
    if verbose:
        command.append("-v")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    text = result.stdout + result.stderr
    count = lambda word: int(next(iter(re.findall(rf"(\d+) {word}", text)), 0))   # noqa: E731
    return count("passed"), count("failed") + count("error"), count("skipped"), text


def live_llm_check(api_key: str) -> bool:
    """Optional: ask the real LLM one short question to prove the key works."""
    sys.path.insert(0, str(ROOT))
    from subsystem_3_recycling_ai import LLMServiceError, OpenAICompatibleClient
    client = OpenAICompatibleClient(api_key, "Qwen3.8 27B", "https://chat.kiconnect.nrw/api/v1")
    try:
        answer = client.ask("In one short sentence: which German bin takes clean paper?")
    except LLMServiceError as error:
        print(f"  LIVE LLM  : FAILED - {error.detail}")
        return False
    print(f"  LIVE LLM  : OK - {answer[:100]!r}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EcoSort AI automated tests.")
    parser.add_argument("--quick", action="store_true", help="skip the real-model end-to-end test")
    parser.add_argument("--live", metavar="API_KEY", help="also test the real LLM with this key")
    parser.add_argument("-v", "--verbose", action="store_true", help="list every test")
    args = parser.parse_args()

    suites = [s for s in SUITES if not (args.quick and "integration" in s[2])]
    print("EcoSort AI - automated tests\n" + "=" * 78)
    total_pass = total_fail = total_skip = 0
    failures: list[str] = []
    started = time.time()
    for label, owner, path in suites:
        passed, failed, skipped, output = run_suite(path, args.verbose)
        total_pass, total_fail, total_skip = total_pass + passed, total_fail + failed, total_skip + skipped
        status = "PASS" if failed == 0 and passed > 0 else "FAIL"
        print(f"[{status}] {label:<42} {owner:<17} {passed:>3} passed {failed:>2} failed {skipped:>2} skipped")
        if args.verbose:
            print(output)
        if status == "FAIL":
            failures.append(output)
    print("=" * 78)
    print(f"TOTAL: {total_pass} passed, {total_fail} failed, {total_skip} skipped "
          f"in {time.time() - started:.1f}s")

    live_ok = True
    if args.live:
        print("\nLive check:")
        live_ok = live_llm_check(args.live)

    for output in failures:
        print("\n--- details of failing suite ---\n" + output)
    ok = total_fail == 0 and total_pass > 0 and live_ok
    print("\nRESULT:", "ALL GOOD" if ok else "SOMETHING FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
