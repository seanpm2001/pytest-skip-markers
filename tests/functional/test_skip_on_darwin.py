# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""
Test the ``@pytest.mark.skip_on_darwin`` marker.
"""
import sys
from unittest import mock

import pytest

pytestmark = [
    pytest.mark.skipif(
        sys.platform.startswith("win")
        and sys.version_info >= (3, 8)
        and sys.version_info < (3, 10),
        reason="PyTest's capture and pytester.runpytest_inprocess looks broken on Windows and Py(>3.8,<3.10)",
    ),
]


def test_skipped(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.skip_on_darwin
        def test_one():
            assert True
        """
    )
    return_value = True
    with mock.patch("pytestskipmarkers.utils.platform.is_darwin", return_value=return_value):
        res = pytester.runpytest_inprocess()
        res.assert_outcomes(skipped=1)
    res.stdout.no_fnmatch_line("*PytestUnknownMarkWarning*")


def test_not_skipped(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.skip_on_darwin
        def test_one():
            assert True
        """
    )
    return_value = False
    with mock.patch("pytestskipmarkers.utils.platform.is_darwin", return_value=return_value):
        res = pytester.runpytest_inprocess()
        res.assert_outcomes(passed=1)
    res.stdout.no_fnmatch_line("*PytestUnknownMarkWarning*")


def test_skip_reason(pytester):
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.skip_on_darwin(reason='Because!')
        def test_one():
            assert True
        """
    )
    return_value = True
    with mock.patch("pytestskipmarkers.utils.platform.is_darwin", return_value=return_value):
        res = pytester.runpytest_inprocess("-ra", "-s", "-vv")
        res.assert_outcomes(skipped=1)
    res.stdout.fnmatch_lines(["SKIPPED * test_skip_reason.py:*: Because!"])
