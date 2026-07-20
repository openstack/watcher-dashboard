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

"""Integration tests for Strategies using Playwright."""

import json

import yaml

from django import test

from watcher_dashboard.test.integration import playwright_base
from watcher_dashboard.test.integration import playwright_config as config


@test.tag('integration')
class StrategiesTests(playwright_base.PlaywrightTestCase):
    """Integration tests for Strategies using Playwright."""

    def test_strategies_match_watcher_api(self):
        """Test that strategies displayed in UI match those from Watcher API.

        This test verifies that the Horizon dashboard correctly displays all
        strategies registered in Watcher, ensuring consistency between the API
        and the UI representation.

        Steps:
            1. Fetch strategies list from Watcher API
            2. Navigate to Admin > Optimization > Strategies in Horizon
            3. Verify strategy count matches between API and UI
            4. Verify each strategy from API is visible in UI with correct name
               and display_name
            5. For each strategy, verify parameter specs match API

        Expected Result:
            All strategies from Watcher API should be visible in the dashboard
            with matching names, display names, and parameter specifications.
        """
        # Fetch strategies from Watcher API as source of truth
        api_strategies = self.watcher_client.strategy.list(detail=True)
        self.assertGreater(
            len(api_strategies), 0, "No strategies found in Watcher API"
        )

        # Navigate to Strategies page through the menu
        # This ensures Horizon loads all panels correctly
        self.page.get_by_text("Optimization").click()
        self.take_screenshot("optimization_clicked")
        self.page.get_by_role("link", name="Strategies").click()
        self.take_screenshot("strategies_page_loaded")

        # Verify strategy count matches between API and UI
        ui_strategy_rows = self.page.locator("tbody tr")
        self.expect(ui_strategy_rows).to_have_count(len(api_strategies))
        self.take_screenshot("strategies_count_verified")

        # Verify each strategy from API is correctly displayed in UI
        for idx, api_strategy in enumerate(api_strategies):
            strategy_name = api_strategy.name
            display_name = api_strategy.display_name
            strategy_uuid = api_strategy.uuid

            # Locate the row by strategy name
            row = self.page.locator(
                f"tbody tr[data-display='{strategy_name}']"
            )
            self.expect(row).to_be_visible()

            # Verify the display name is visible in the row
            self.expect(
                row.get_by_text(display_name, exact=True)
            ).to_be_visible()

            # Click on the strategy UUID to view details
            uuid_link = row.get_by_role("link", name=strategy_uuid)
            self.expect(uuid_link).to_be_visible()
            uuid_link.click()
            self.take_screenshot(
                f"strategy_{idx}_{strategy_name}_details_opened"
            )

            # Verify parameter specs match API
            self._verify_parameter_specs(api_strategy, strategy_name, idx)

            # Go back to the strategies list
            self.page.go_back()
            self.page.wait_for_load_state(
                "networkidle", timeout=config.get_timeout()
            )
            self.take_screenshot(f"strategy_{idx}_back_to_list")

        self.take_screenshot("all_strategies_verified")

    def _verify_parameter_specs(self, api_strategy, strategy_name, idx):
        """Verify that parameter specs in UI match API data.

        :param api_strategy: Strategy object from Watcher API
        :param strategy_name: Name of the strategy for screenshot naming
        :param idx: Index for screenshot naming
        """
        api_specs = api_strategy.parameters_spec

        # The UI shows parameters_spec as a YAML/JSON formatted string
        # Find the definition term "Parameters Spec"
        params_spec_dt = self.page.locator("dt:has-text('Parameters Spec')")
        self.expect(params_spec_dt).to_be_visible()

        # Get the corresponding definition data (dd element)
        params_spec_dd = params_spec_dt.locator(
            "xpath=following-sibling::dd[1]"
        )
        self.expect(params_spec_dd).to_be_visible()

        # Get the text content from the UI
        ui_spec_text = params_spec_dd.inner_text().strip()
        self.take_screenshot(
            f"strategy_{idx}_{strategy_name}_parameter_specs_visible"
        )

        if not api_specs:
            # No parameter specs from API
            # UI should show empty or dash
            self.assertIn(
                ui_spec_text,
                ['-', '', 'None'],
                f"Expected empty params for {strategy_name}, "
                f"got: {ui_spec_text}",
            )
            self.take_screenshot(
                f"strategy_{idx}_{strategy_name}_no_parameter_specs"
            )
            return

        # Parse both API and UI specs for comparison
        # API specs is already a dict
        api_spec_dict = api_specs

        # UI shows it as YAML format, parse it
        try:
            ui_spec_dict = yaml.safe_load(ui_spec_text)
        except yaml.YAMLError:
            # If YAML parsing fails, try JSON
            try:
                ui_spec_dict = json.loads(ui_spec_text)
            except json.JSONDecodeError:
                self.fail(
                    f"Failed to parse UI parameter spec for {strategy_name}: "
                    f"{ui_spec_text}"
                )

        # The UI might strip the top-level $schema, type, and required fields
        # and only show the properties content. Let's check both formats.
        if 'properties' in api_spec_dict and ui_spec_dict == api_spec_dict.get(
            'properties'
        ):
            # UI shows only the properties part
            self.take_screenshot(
                f"strategy_{idx}_{strategy_name}_parameter_specs_verified"
            )
            return

        # Full comparison including top-level fields
        self.assertEqual(
            api_spec_dict,
            ui_spec_dict,
            f"Parameter specs mismatch for {strategy_name}. "
            f"API: {api_spec_dict}, UI: {ui_spec_dict}",
        )

        self.take_screenshot(
            f"strategy_{idx}_{strategy_name}_parameter_specs_verified"
        )
