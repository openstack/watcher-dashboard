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

"""Integration tests for Filters using Playwright."""

import time

from django import test

from watcher_dashboard.test.integration import playwright_base


@test.tag('integration')
class FiltersTests(playwright_base.PlaywrightTestCase):
    """Integration tests for Filters using Playwright."""

    def _apply_filter(self, value, switch_to=None, current_filter="Goal = "):
        """Apply a table filter on the current page.

        :param value: The filter value to enter in the text input.
        :param switch_to: Optional data-select-value to switch the filter
            dropdown before applying (e.g. 'strategy').
        :param current_filter: The button name of the current default
            filter dropdown (e.g. 'Goal = ').
        """
        if switch_to:
            dropdown = self.page.get_by_role("button", name=current_filter)
            dropdown.click()
            option = self.page.locator(f"a[data-select-value='{switch_to}']")
            option.click()

        filter_input = self.page.locator("input[type='text']").last
        self.expect(filter_input).to_be_visible(timeout=5000)
        filter_input.fill(value)
        self.take_screenshot(f"filter_value_entered_{value}")

        filter_button = self.page.get_by_role("button", name="Filter")
        self.expect(filter_button).to_be_visible()

        with self.page.expect_navigation(
            wait_until="networkidle", timeout=10000
        ):
            filter_button.click()

        self.take_screenshot(f"filter_applied_{value}")

    def _get_column_values(
        self, column_index, use_link=False, expected_count=None
    ):
        """Extract text values from a column in the filtered table rows.

        :param column_index: Zero-based column index to extract from.
        :param use_link: If True, extract text from the <a> inside the cell.
        :param expected_count: If set, assert exact row count. Otherwise
            just assert at least one row is visible.
        :returns: Set of text values from the specified column.
        """
        rows = self.page.locator("tbody tr")
        if expected_count is not None:
            self.expect(rows).to_have_count(expected_count)
            count = expected_count
        else:
            self.assertGreater(
                rows.count(), 0, "No rows visible after filtering"
            )
            count = rows.count()
        values = set()
        for i in range(count):
            cell = rows.nth(i).locator("td").nth(column_index)
            if use_link:
                text = cell.locator("a").text_content().strip()
            else:
                text = cell.text_content().strip()
            values.add(text)
        return values

    def _wait_for_audit_completion(
        self, audit_uuids, timeout=180, target_state='SUCCEEDED'
    ):
        """Wait for audits to reach a target state via API polling.

        :param audit_uuids: List of audit UUIDs to wait for.
        :param timeout: Maximum wait time in seconds per audit.
        :param target_state: The audit state to wait for.
        """
        terminal_states = ('SUCCEEDED', 'FAILED', 'CANCELLED', 'DELETED')
        for audit_uuid in audit_uuids:
            start_time = time.time()
            while time.time() - start_time < timeout:
                audit = self.watcher_client.audit.get(audit_uuid)
                if audit.state == target_state:
                    break
                if audit.state in terminal_states:
                    self.fail(
                        f"Audit {audit_uuid} reached terminal state "
                        f"{audit.state} instead of {target_state}"
                    )
                time.sleep(5)
            else:
                raise TimeoutError(
                    f"Audit {audit_uuid} did not reach {target_state} "
                    f"in {timeout}s"
                )

    def test_filters_strategies_by_goal(self):
        """Test that strategies can be filtered by goal."""
        all_strategies = self.watcher_client.strategy.list(detail=True)
        self.assertGreater(
            len(all_strategies), 0, "No strategies found in Watcher API"
        )

        target_goal_name = "workload_balancing"
        expected_strategies = [
            s
            for s in all_strategies
            if hasattr(s, 'goal_name') and s.goal_name == target_goal_name
        ]
        self.assertGreater(
            len(expected_strategies),
            0,
            f"No strategies found for goal '{target_goal_name}'",
        )

        self.page.get_by_text("Optimization").click()
        self.page.get_by_role("link", name="Strategies").click()

        all_rows = self.page.locator("tbody tr")
        self.expect(all_rows).to_have_count(len(all_strategies))

        self._apply_filter(target_goal_name)

        visible_names = self._get_column_values(
            column_index=1, expected_count=len(expected_strategies)
        )
        expected_names = {s.name for s in expected_strategies}
        self.assertEqual(visible_names, expected_names)

    def test_filters_audit_templates_by_goal(self):
        """Test that audit templates can be filtered by goal."""
        target_goal_name = "server_consolidation"

        for i in range(2):
            name = self._generate_unique_name("test_filter_sc")
            self.create_audit_template(
                name,
                goal_name="Server Consolidation",
                strategy_name="Basic offline consolidation",
            )
        for i in range(2):
            name = self._generate_unique_name("test_filter_other")
            self.create_audit_template(
                name, goal_name="Dummy goal", strategy_name="Dummy strategy"
            )

        self.page.goto(f"{self.dashboard_url}/admin/audit_templates/")

        all_templates = self.watcher_client.audit_template.list(detail=True)
        expected_templates = [
            t
            for t in all_templates
            if hasattr(t, 'goal_name') and t.goal_name == target_goal_name
        ]
        self.assertGreater(
            len(expected_templates),
            0,
            f"No audit templates found for goal '{target_goal_name}'",
        )

        self._apply_filter(target_goal_name)

        visible_names = self._get_column_values(
            column_index=1, expected_count=len(expected_templates)
        )
        expected_names = {t.name for t in expected_templates}
        self.assertEqual(visible_names, expected_names)

    def test_filters_audit_templates_by_strategy(self):
        """Test that audit templates can be filtered by strategy."""
        target_strategy_name = "basic"

        for i in range(2):
            name = self._generate_unique_name("test_filter_basic")
            self.create_audit_template(
                name,
                goal_name="Server Consolidation",
                strategy_name="Basic offline consolidation",
            )
        for i in range(2):
            name = self._generate_unique_name("test_filter_other")
            self.create_audit_template(
                name, goal_name="Dummy goal", strategy_name="Dummy strategy"
            )

        self.page.goto(f"{self.dashboard_url}/admin/audit_templates/")

        all_templates = self.watcher_client.audit_template.list(detail=True)
        expected_templates = [
            t
            for t in all_templates
            if hasattr(t, 'strategy_name')
            and t.strategy_name == target_strategy_name
        ]
        self.assertGreater(
            len(expected_templates),
            0,
            f"No templates found for strategy '{target_strategy_name}'",
        )

        self._apply_filter(target_strategy_name, switch_to="strategy")

        visible_names = self._get_column_values(
            column_index=1, expected_count=len(expected_templates)
        )
        expected_names = {t.name for t in expected_templates}
        self.assertEqual(visible_names, expected_names)

    def test_filters_audits_by_goal(self):
        """Test that audits can be filtered by goal."""
        target_goal_name = "server_consolidation"

        template_target = self._generate_unique_name("test_filter_audit_sc")
        self.create_audit_template(
            template_target,
            goal_name="Server Consolidation",
            strategy_name="Basic offline consolidation",
        )
        created_names = set()
        for i in range(2):
            audit_name = self._generate_unique_name("test_filter_audit")
            self.create_audit(template_target, audit_name)
            created_names.add(audit_name)

        template_other = self._generate_unique_name("test_filter_audit_other")
        self.create_audit_template(
            template_other,
            goal_name="Dummy goal",
            strategy_name="Dummy strategy",
        )
        excluded_names = set()
        for i in range(2):
            audit_name = self._generate_unique_name("test_filter_audit_other")
            self.create_audit(template_other, audit_name)
            excluded_names.add(audit_name)

        self.page.goto(f"{self.dashboard_url}/admin/audits/")

        self._apply_filter(target_goal_name)

        visible_names = self._get_column_values(column_index=1)
        self.assertTrue(
            created_names.issubset(visible_names),
            f"Created audits {created_names} not found in "
            f"visible audits {visible_names}",
        )
        self.assertFalse(
            excluded_names & visible_names,
            f"Excluded audits {excluded_names & visible_names} "
            f"should not appear after filtering",
        )

    def test_filters_audits_by_strategy(self):
        """Test that audits can be filtered by strategy."""
        target_strategy_name = "basic"

        template_target = self._generate_unique_name("test_filter_audit_basic")
        self.create_audit_template(
            template_target,
            goal_name="Server Consolidation",
            strategy_name="Basic offline consolidation",
        )
        created_names = set()
        for i in range(2):
            audit_name = self._generate_unique_name("test_filter_audit")
            self.create_audit(template_target, audit_name)
            created_names.add(audit_name)

        template_other = self._generate_unique_name("test_filter_audit_other")
        self.create_audit_template(
            template_other,
            goal_name="Dummy goal",
            strategy_name="Dummy strategy",
        )
        excluded_names = set()
        for i in range(2):
            audit_name = self._generate_unique_name("test_filter_audit_other")
            self.create_audit(template_other, audit_name)
            excluded_names.add(audit_name)

        self.page.goto(f"{self.dashboard_url}/admin/audits/")

        self._apply_filter(target_strategy_name, switch_to="strategy")

        visible_names = self._get_column_values(column_index=1)
        self.assertTrue(
            created_names.issubset(visible_names),
            f"Created audits {created_names} not found in "
            f"visible audits {visible_names}",
        )
        self.assertFalse(
            excluded_names & visible_names,
            f"Excluded audits {excluded_names & visible_names} "
            f"should not appear after filtering",
        )

    def test_filters_action_plans_by_audit(self):
        """Test that action plans can be filtered by audit."""
        template_name = self._generate_unique_name("test_filter_ap_tpl")
        self.create_audit_template(
            template_name,
            goal_name="Dummy goal",
            strategy_name="Dummy strategy",
        )

        audit_uuids = []
        for i in range(2):
            audit_name = self._generate_unique_name("test_filter_ap_audit")
            audit_uuid = self.create_audit(template_name, audit_name)
            audit_uuids.append(audit_uuid)

        self._wait_for_audit_completion(audit_uuids)

        target_audit_uuid = audit_uuids[0]

        # Get expected action plan UUIDs for the target audit
        all_aps = self.watcher_client.action_plan.list(detail=True)
        expected_ap_uuids = {
            ap.uuid for ap in all_aps if ap.audit_uuid == target_audit_uuid
        }
        excluded_ap_uuids = {
            ap.uuid for ap in all_aps if ap.audit_uuid == audit_uuids[1]
        }
        self.assertGreater(
            len(expected_ap_uuids),
            0,
            f"No action plans found for audit '{target_audit_uuid}'",
        )

        self.page.goto(f"{self.dashboard_url}/admin/action_plans/")

        self._apply_filter(target_audit_uuid)

        visible_uuids = self._get_column_values(column_index=1, use_link=True)
        self.assertTrue(
            expected_ap_uuids.issubset(visible_uuids),
            f"Expected action plans {expected_ap_uuids} not found "
            f"in visible {visible_uuids}",
        )
        self.assertFalse(
            excluded_ap_uuids & visible_uuids,
            f"Excluded action plans {excluded_ap_uuids & visible_uuids} "
            f"should not appear after filtering",
        )

    def test_filters_actions_by_action_plan(self):
        """Test that actions can be filtered by action plan ID."""
        template_name = self._generate_unique_name("test_filter_actions_tpl")
        self.create_audit_template(
            template_name,
            goal_name="Dummy goal",
            strategy_name="Dummy strategy",
        )

        audit_uuids = []
        for i in range(2):
            audit_name = self._generate_unique_name(
                "test_filter_actions_audit"
            )
            audit_uuid = self.create_audit(template_name, audit_name)
            audit_uuids.append(audit_uuid)

        self._wait_for_audit_completion(audit_uuids)

        # Get action plan UUIDs from completed audits
        all_aps = self.watcher_client.action_plan.list(detail=True)
        target_ap_uuid = None
        excluded_ap_uuid = None
        for ap in all_aps:
            if ap.audit_uuid == audit_uuids[0]:
                target_ap_uuid = ap.uuid
            elif ap.audit_uuid == audit_uuids[1]:
                excluded_ap_uuid = ap.uuid
        self.assertIsNotNone(
            target_ap_uuid, "No action plan generated for target audit"
        )

        # Get expected action UUIDs for the target action plan
        all_actions = self.watcher_client.action.list(detail=True)
        expected_action_uuids = {
            a.uuid for a in all_actions if a.action_plan_uuid == target_ap_uuid
        }
        excluded_action_uuids = set()
        if excluded_ap_uuid:
            excluded_action_uuids = {
                a.uuid
                for a in all_actions
                if a.action_plan_uuid == excluded_ap_uuid
            }
        self.assertGreater(
            len(expected_action_uuids),
            0,
            f"No actions found for action plan '{target_ap_uuid}'",
        )

        self.page.goto(f"{self.dashboard_url}/admin/actions/")

        self._apply_filter(target_ap_uuid)

        visible_uuids = self._get_column_values(column_index=0, use_link=True)
        self.assertTrue(
            expected_action_uuids.issubset(visible_uuids),
            f"Expected actions {expected_action_uuids} not found "
            f"in visible {visible_uuids}",
        )
        self.assertFalse(
            excluded_action_uuids & visible_uuids,
            f"Excluded actions {excluded_action_uuids & visible_uuids} "
            f"should not appear after filtering",
        )
