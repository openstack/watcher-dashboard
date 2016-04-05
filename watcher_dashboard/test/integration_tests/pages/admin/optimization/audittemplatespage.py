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

from selenium.webdriver.common import by

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables


class AuditTemplatesTable(tables.TableRegion):

    name = 'audit_templates'

    CREATE_AUDIT_TEMPLATE_FORM_FIELDS = ("name", "description",
                                         "goal_id", "strategy_id")

    @tables.bind_table_action('create')
    def create_audit_template(self, create_button):
        create_button.click()
        return forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.CREATE_AUDIT_TEMPLATE_FORM_FIELDS)

    @tables.bind_table_action('delete')
    def delete_audit_template(self, delete_button):
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf, None)

    @tables.bind_row_action('launch_audit')
    def launch_audit(self, launch_button, row):
        launch_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)


class AudittemplatesPage(basepage.BaseNavigationPage):

    DEFAULT_DESCRIPTION = "Fake description from integration tests"
    DEFAULT_GOAL = "SERVER_CONSOLIDATION"

    AUDITS_PAGE_TITLE = "Audits - OpenStack Dashboard"

    AUDIT_TEMPLATE_INFO_SUB_TITLE = "Audit Template Info"

    # Set fields name attribute
    CREATE_AUDIT_TEMPLATE_FORM_FIELDS = (
        "name", "description", "goal"
    )

    _audittemplates_info_title_locator = (by.By.CSS_SELECTOR, 'div.detail>h4')

    def __init__(self, driver, conf):
        super(AudittemplatesPage, self).__init__(driver, conf)
        self._page_title = "Audit Templates"

    @property
    def audittemplates_table(self):
        return AuditTemplatesTable(self.driver, self.conf)

    @property
    def audit_templates__action_create_form(self):
        return forms.FormRegion(self.driver, self.conf, None,
                                self.CREATE_AUDIT_TEMPLATE_FORM_FIELDS)

    def _get_row_with_audit_template_name(self, name):
        self._turn_off_implicit_wait()
        row = self.audittemplates_table.get_row("name", name)
        self._turn_on_implicit_wait()
        return row

    def delete_audit_template(self, name):
        row = self._get_row_with_audit_template_name(name)
        row.mark()
        confirm_delete_audit_template_form = (
            self.audittemplates_table.delete_audit_template())
        confirm_delete_audit_template_form.submit()

    def create_audit_template(self,
                              name,
                              description=DEFAULT_DESCRIPTION,
                              goal_id=DEFAULT_GOAL):
        self.audittemplates_table.create_audit_template()
        self.audit_templates__action_create_form.name.text = name
        self.audit_templates__action_create_form.description.text = description
        self.audit_templates__action_create_form.goal_id.value = goal_id
        self.audit_templates__action_create_form.submit()

    def is_audit_template_present(self, name):
        return bool(
            self._get_row_with_audit_template_name(name))

    def launch_audit(self, name):
        row = self._get_row_with_audit_template_name(name)
        self.audittemplates_table.launch_audit(row)
        # Check that the name appears in Audits page
        return (self.driver.title == self.AUDITS_PAGE_TITLE) \
            and (name in self.driver.page_source)

    def show_audit_template_info(self, name):
        self.driver.find_element_by_link_text(name).click()
        info_line = self._get_element(*self._audittemplates_info_title_locator)
        return self._is_text_visible(
            info_line, self.AUDIT_TEMPLATE_INFO_SUB_TITLE)
