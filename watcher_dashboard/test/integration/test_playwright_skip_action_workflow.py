#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Integration tests for skip action workflow using Playwright."""

import re

from django import test

from watcher_dashboard.test.integration import playwright_base


@test.tag('integration')
class SkipActionWorkflowTests(playwright_base.PlaywrightTestCase):
    """Integration tests for skip action workflow."""

    def test_skip_action_workflow(self):
        """Test skipping an action and verifying plan succeeds with skip msg.

        Steps:
            1. Create an audit template and audit, wait for SUCCEEDED
            2. Navigate to the action plan and skip the first action
            3. Verify the action shows SKIPPED state and skip reason
            4. Start the action plan and wait for SUCCEEDED
            5. Verify the status message reflects the skipped action

        Expected Result:
            The skipped action should show SKIPPED state with the reason,
            and the action plan should succeed with a status message
            indicating one or more actions were skipped.
        """
        skip_reason = "this action is skipped in CI testing"

        template_name = self._generate_unique_name("dummy_skip_template")
        self.create_audit_template(
            name=template_name,
            goal_name="Dummy goal",
            strategy_name="Dummy strategy",
        )

        audit_name = self._generate_unique_name("dummy_skip_audit")
        self.create_audit(
            template_name=template_name,
            audit_name=audit_name,
            audit_type="ONESHOT",
        )

        self.page.goto(f"{self.dashboard_url}/admin/audits/")
        row = self.page.get_by_role("row").filter(has_text=audit_name).first
        self.expect(row).to_be_visible()
        row.get_by_role("link", name=audit_name).click()
        self.take_screenshot("audit_detail_loaded")

        final_audit_state = self.wait_for_audit_terminal_state(timeout=300)
        self.assertEqual("SUCCEEDED", final_audit_state)
        self.take_screenshot("audit_terminal_state_succeeded")

        action_plans_table = self.page.get_by_role(
            "table", name="Related Action Plans"
        )
        action_plan_row = action_plans_table.locator("tbody tr").first
        self.expect(action_plan_row).to_be_visible()
        action_plan_link = action_plan_row.get_by_role("link").first
        self.expect(action_plan_link).to_be_visible()
        action_plan_href = action_plan_link.get_attribute("href")
        action_plan_uuid = self._extract_uuid_from_href(action_plan_href)
        action_plan_link.click()
        self.take_screenshot("action_plan_detail_loaded")

        actions_table = self.page.get_by_role("table", name="Related Actions")
        first_action_row = actions_table.locator("tbody tr").first
        self.expect(first_action_row).to_be_visible()

        action_link = first_action_row.get_by_role("link").first
        self.expect(action_link).to_be_visible()
        action_href = action_link.get_attribute("href")
        action_uuid = self._extract_uuid_from_href(action_href)

        skip_btn = first_action_row.get_by_role("link", name="Skip Action")
        self.expect(skip_btn).to_be_visible()
        skip_btn.click()
        self.take_screenshot("skip_action_modal_open")

        modal_header = self.page.get_by_role("heading", name="Skip Action")
        self.expect(modal_header).to_be_visible()
        self.page.get_by_label("Reason for skipping").fill(skip_reason)
        self.take_screenshot("skip_reason_filled")
        self.page.get_by_role("button", name="Skip Action").click()
        self.wait_for_success_message()
        self.take_screenshot("skip_action_submitted")

        self.page.goto(
            f"{self.dashboard_url}/admin/actions/{action_uuid}/detail"
        )
        self.take_screenshot("action_detail_loaded")

        self.expect(self.page.get_by_text("State")).to_be_visible()
        self.expect(
            self.page.get_by_text("SKIPPED", exact=True)
        ).to_be_visible()

        self.expect(self.page.get_by_text("Skip Reason")).to_be_visible()
        self.expect(
            self.page.get_by_text(
                re.compile(r"(skipped.*CI testing|Action skipped by user\.?)")
            )
        ).to_be_visible()

        self.page.goto(f"{self.dashboard_url}/admin/audits/")
        audit_row = (
            self.page.get_by_role("row").filter(has_text=audit_name).first
        )
        self.expect(audit_row).to_be_visible()
        audit_row.get_by_role("link", name=audit_name).click()
        self.take_screenshot("audit_detail_reloaded")

        plan_row = (
            self.page.get_by_role("table", name="Related Action Plans")
            .locator("tbody tr")
            .filter(has_text=action_plan_uuid)
            .first
        )
        self.expect(plan_row).to_be_visible()

        start_control = plan_row.get_by_role(
            "button", name="Start Action Plan"
        ).or_(plan_row.get_by_role("link", name="Start Action Plan"))
        self.expect(start_control.first).to_be_visible()
        start_control.first.click()
        self.wait_for_success_message()
        self.take_screenshot("action_plan_started")

        self.page.goto(
            f"{self.dashboard_url}/admin/action_plans/"
            f"{action_plan_uuid}/detail"
        )
        self.take_screenshot("action_plan_detail_after_start")

        self.expect(
            self.page.get_by_role("heading", name="Action Plan Overview")
        ).to_be_visible()

        final_plan_state = self.wait_for_action_plan_terminal_state(
            timeout=300
        )
        self.assertEqual(
            "SUCCEEDED",
            final_plan_state,
            "Action plan did not succeed; state=%s" % final_plan_state,
        )
        self.take_screenshot("action_plan_succeeded")

        # Backend may set the message slightly after plan reaches SUCCEEDED
        self.expect(
            self.page.get_by_text(
                re.compile(r"one or more actions were skipped\.?", re.I)
            )
        ).to_be_visible(timeout=30000)
