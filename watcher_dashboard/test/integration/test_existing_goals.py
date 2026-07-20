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

"""Integration tests for Goals using Playwright."""

from django import test

from watcher_dashboard.test.integration import playwright_base
from watcher_dashboard.test.integration import playwright_config as config


@test.tag('integration')
class GoalsTests(playwright_base.PlaywrightTestCase):
    """Integration tests for Goals using Playwright."""

    def test_goals_match_watcher_api(self):
        """Test that goals displayed in UI match those from Watcher API.

        This test verifies that the Horizon dashboard correctly displays all
        goals registered in Watcher, ensuring consistency between the API and
        the UI representation.

        Steps:
            1. Fetch goals list from Watcher API
            2. Navigate to Admin > Optimization > Goals in Horizon
            3. Verify goal count matches between API and UI
            4. Verify each goal from API is visible in UI with correct name
               and display_name
            5. For each goal, verify efficacy specifications match API

        Expected Result:
            All goals from Watcher API should be visible in the dashboard with
            matching names, display names, and efficacy specifications.
        """
        # Fetch goals from Watcher API as source of truth
        api_goals = self.watcher_client.goal.list(detail=True)
        self.assertGreater(len(api_goals), 0, "No goals found in Watcher API")

        # Navigate to Goals page through the menu
        # This ensures Horizon loads all panels correctly
        self.page.get_by_text("Optimization").click()
        self.take_screenshot("optimization_clicked")
        self.page.get_by_role("link", name="Goals").click()
        self.take_screenshot("goals_page_loaded")

        # Verify goal count matches between API and UI
        ui_goal_rows = self.page.locator("tbody tr")
        self.expect(ui_goal_rows).to_have_count(len(api_goals))
        self.take_screenshot("goals_count_verified")

        # Verify each goal from API is correctly displayed in UI
        for idx, api_goal in enumerate(api_goals):
            goal_name = api_goal.name
            display_name = api_goal.display_name
            goal_uuid = api_goal.uuid

            # Locate the row by goal name
            row = self.page.locator(f"tbody tr[data-display='{goal_name}']")
            self.expect(row).to_be_visible()

            # Verify the display name is visible in the row
            self.expect(
                row.get_by_text(display_name, exact=True)
            ).to_be_visible()

            # Click on the goal UUID to view details
            uuid_link = row.get_by_role("link", name=goal_uuid)
            self.expect(uuid_link).to_be_visible()
            uuid_link.click()
            self.take_screenshot(f"goal_{idx}_{goal_name}_details_opened")

            # Verify efficacy specifications match API
            self._verify_efficacy_specifications(api_goal, goal_name, idx)

            # Go back to the goals list
            self.page.go_back()
            self.page.wait_for_load_state(
                "networkidle", timeout=config.get_timeout()
            )
            self.take_screenshot(f"goal_{idx}_back_to_list")

        self.take_screenshot("all_goals_verified")

    def _verify_efficacy_specifications(self, api_goal, goal_name, idx):
        """Verify that efficacy specifications in UI match API data.

        :param api_goal: Goal object from Watcher API
        :param goal_name: Name of the goal for screenshot naming
        :param idx: Index for screenshot naming
        """
        api_specs = api_goal.efficacy_specification

        if not api_specs:
            # No efficacy specifications - verify UI shows this
            # Look for "No items to display" or similar message
            no_data_msg = self.page.get_by_text("No items to display")
            self.expect(no_data_msg).to_be_visible()
            self.take_screenshot(f"goal_{idx}_{goal_name}_no_efficacy_specs")
            return

        # Find the efficacy specifications table by its ID
        spec_table = self.page.locator("table#efficacy_specification")
        self.expect(spec_table).to_be_visible()

        # Verify count matches
        spec_rows = spec_table.locator("tbody tr")
        self.expect(spec_rows).to_have_count(len(api_specs))
        self.take_screenshot(f"goal_{idx}_{goal_name}_efficacy_specs_count_ok")

        # Verify each specification
        for spec_idx, api_spec in enumerate(api_specs):
            spec_name = api_spec['name']
            spec_description = api_spec['description']
            spec_unit = api_spec.get('unit') or '-'
            spec_schema = api_spec['schema']

            # Find the row for this specification
            spec_row = spec_table.locator(
                f"tbody tr:has(td:text-is('{spec_name}'))"
            )
            self.expect(spec_row).to_be_visible()

            # Verify description
            self.expect(
                spec_row.get_by_text(spec_description, exact=True)
            ).to_be_visible()

            # Verify unit
            self.expect(
                spec_row.get_by_text(spec_unit, exact=True)
            ).to_be_visible()

            # Verify schema
            self.expect(
                spec_row.get_by_text(spec_schema, exact=True)
            ).to_be_visible()

        self.take_screenshot(
            f"goal_{idx}_{goal_name}_all_efficacy_specs_verified"
        )
