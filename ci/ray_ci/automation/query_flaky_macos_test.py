#!/usr/bin/env python3
from ray_release.test import Test, TestState
from ci.ray_ci.utils import logger
from typing import List
from ray_release.configs.global_config import init_global_config
from ray_release.bazel import bazel_runfile
import json

ALL_TEST_PREFIXES = ["darwin:"]

def main() -> None:
    logger.info("Start querying flaky tests ...")
    init_global_config(bazel_runfile("release/ray_release/configs/oss_config.yaml"))
    tests = query_all_tests()
    flaky_tests = filter_flaky_tests(tests)
    logger.info("Number of flaky tests found: " + str(len(flaky_tests)))
    logger.info("List of flaky tests: ")
    print(retrieve_test_names(flaky_tests, 'darwin://'))

def query_all_tests() -> List[Test]:
    """
    Queries all tests with the listed prefixes.
    """
    tests = []
    for test_prefix in ALL_TEST_PREFIXES:
        logger.info("Querying tests with prefix: " + test_prefix + " ....")
        tests.extend(Test.gen_from_s3(test_prefix))
    logger.info("Number of tests found: " + str(len(tests)))
    return tests

def filter_flaky_tests(tests: List[Test]) -> List[Test]:
    """
    Filters and returns list of tests with flaky state.

    Input:
    tests: List of Test objects
    """
    flaky_tests = []
    for test in tests:
        if test.get_state() == TestState.FLAKY:
            flaky_tests.append(test)
    return flaky_tests

def retrieve_test_names(tests: List[Test], prefix: str) -> str:
    """
    Return list of test names with prefix stripped.

    Input:
    tests: List of Test objects
    prefix: Prefix of the test names
    """
    test_names = [test.get_name().replace(prefix, '') for test in tests]
    return json.dumps(test_names)

if __name__ == "__main__":
    main()
