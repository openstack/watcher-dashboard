# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Logging redirection for watcher-dashboard tests.

Adapted from ``watcher.tests.fixtures.watcher`` (``StandardLogging`` /
``NullHandler``): quiet local runs by default, still exercises debug log
formatting, and honors ``OS_DEBUG`` like upstream.

Uses ``addCleanup`` so this works with Django's ``TestCase`` as well as
testtools-based cases (no ``useFixture`` dependency).
"""

from __future__ import annotations

import logging as std_logging
import os

from io import StringIO


class NullHandler(std_logging.Handler):
    """Format debug records without persisting them (catches format errors)."""

    def handle(self, record) -> None:
        # format() exercises the formatter so broken format strings fail fast;
        # emit() is a no-op so nothing is actually written
        self.format(record)

    def emit(self, record) -> None:
        pass

    def createLock(self) -> None:
        self.lock = None


def setup_standard_logging(testcase) -> None:
    """Configure root logging for one test; teardown via ``addCleanup``."""
    root = std_logging.getLogger()
    saved_level = root.level
    saved_handlers = list(root.handlers)

    for h in saved_handlers:
        root.removeHandler(h)

    root.setLevel(std_logging.DEBUG)

    if os.environ.get("OS_DEBUG") in ("True", "true", "1", "yes"):
        level = std_logging.DEBUG
    else:
        level = std_logging.INFO

    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    stream = StringIO()
    main_handler = std_logging.StreamHandler(stream)
    main_handler.setFormatter(std_logging.Formatter(fmt))
    main_handler.setLevel(level)
    root.addHandler(main_handler)

    extra_handlers: list[std_logging.Handler] = []
    if level > std_logging.DEBUG:
        null_h = NullHandler()
        null_h.setLevel(std_logging.DEBUG)
        root.addHandler(null_h)
        extra_handlers.append(null_h)

    def _restore() -> None:
        root.removeHandler(main_handler)
        for h in extra_handlers:
            root.removeHandler(h)
        for h in saved_handlers:
            root.addHandler(h)
        root.setLevel(saved_level)

    testcase.addCleanup(_restore)
