# Copyright (c) 2016 b<>com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from horizon.test import helpers as test
from selenium.common import exceptions as selenium_exceptions


class BrowserTests(test.SeleniumTestCase):
    def test_jasmine(self):
        url = "%s%s" % (self.live_server_url, "/jasmine/")
        self.selenium.get(url)
        wait = self.ui.WebDriverWait(self.selenium, 10)

        def jasmine_done(driver):
            text = driver.find_element_by_id("jasmine-testresult").text
            return "Tests completed" in text

        wait.until(jasmine_done)

        failed_elem = self.selenium.find_element_by_class_name("failed")
        failed = int(failed_elem.text)
        if failed:
            self.log_failure_messages()
        self.assertEqual(failed, 0)

    def log_failure_messages(self):
        logger = logging.getLogger('selenium')
        logger.error("Errors found during jasmine test:")
        fail_elems = self.selenium.find_elements_by_class_name("fail")
        for elem in fail_elems:
            try:
                module = elem.find_element_by_class_name("module-name").text
            except selenium_exceptions.NoSuchElementException:
                continue
            message = elem.find_element_by_class_name("test-message").text
            source = elem.find_element_by_tag_name("pre").text
            logger.error("Module: %s, message: %s, source: %s" % (
                module, message, source))
