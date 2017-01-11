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

from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables

from openstack_dashboard.test.integration_tests.pages import basepage


class AuditsTable(tables.TableRegion):

    name = "audits"

    @tables.bind_table_action('launch_audit')
    def launch_audit(self, launch_button):
        launch_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('go_to_action_plan')
    def go_to_action_plan(self, goto_button):
        goto_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('go_to_audit_template')
    def go_to_audit_template(self, goto_button):
        goto_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)


class AuditsPage(basepage.BaseNavigationPage):

    DEFAULT_ID = "auto"
    AUDIT_TABLE_NAME_COLUMN = 'name'
    AUDIT_TABLE_TEMPLATE_COLUMN_INDEX = 1

    def __init__(self, driver, conf):
        super(AuditsPage, self).__init__(driver, conf)
        self._page_title = "Audits"

    @property
    def audits_table(self):
        return AuditsTable(self.driver, self.conf)

    def _get_audit_row(self, name):
        return self.audits_table.get_row(self.AUDIT_TABLE_NAME_COLUMN, name)

    def create_audit(self, name, id_=DEFAULT_ID, vcpus=None, ram=None,
                     root_disk=None, ephemeral_disk=None, swap_disk=None):
        create_audit_form = self.audits_table.create_audit()
        create_audit_form.name.text = name
        if id_ is not None:
            create_audit_form.audit_id.text = id_
        create_audit_form.vcpus.value = vcpus
        create_audit_form.memory_mb.value = ram
        create_audit_form.disk_gb.value = root_disk
        create_audit_form.eph_gb.value = ephemeral_disk
        create_audit_form.swap_mb.value = swap_disk
        create_audit_form.submit()
        self.wait_till_popups_disappear()

    def delete_audit(self, name):
        row = self._get_audit_row(name)
        row.mark()
        confirm_delete_audits_form = self.audits_table.delete_audit()
        confirm_delete_audits_form.submit()
        self.wait_till_popups_disappear()

    def is_audit_present(self, name):
        return bool(self._get_audit_row(name))
