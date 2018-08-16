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

import uuid

from openstack_dashboard.test.integration_tests import helpers


class AuditTemplateCreatePanelTests(helpers.AdminTestCase):

    def test_create_audit_template(self):
        """Test the audit template panel:

        * Loads the audit template panel
        * Creates a new audit template with random-generated name
        * Checks that this audit template is in list
        * Deletes this audit template (in tearDown)
        * Checks that the audit template is removed
        """
        audit_template_name = "audit_template_%s" % uuid.uuid1()
        audit_template_page = \
            self.home_pg.go_to_optimization_audittemplatespage()
        audit_template_page.create_audit_template(audit_template_name)
        self.assertTrue(audit_template_page.is_audit_template_present(
            audit_template_name))


class AuditTemplatePanelTests(helpers.AdminTestCase):

    def setUp(self):
        super(AuditTemplatePanelTests, self).setUp()
        self.audit_template_name = "audit_template_%s" % uuid.uuid1()
        audit_template_page = \
            self.home_pg.go_to_optimization_audittemplatespage()
        audit_template_page.create_audit_template(self.audit_template_name)

    def tearDown(self):
        audit_template_page = \
            self.home_pg.go_to_optimization_audittemplatespage()
        audit_template_page.delete_audit_template(self.audit_template_name)
        # Uncomment this line when <Delete> button will be implemented
        self.assertFalse(audit_template_page.is_audit_template_present(
            self.audit_template_name))
        super(AuditTemplatePanelTests, self).tearDown()

    def test_show_audit_template_info(self):
        """Test the audit template panel information page

        * Loads the audit template panel
        * Click on link behind the audit template name
        * Checks the info page (only the "Audit Template Info" title for now)
        """
        audit_template_page = \
            self.home_pg.go_to_optimization_audittemplatespage()
        self.assertTrue(
            audit_template_page.show_audit_template_info(
                self.audit_template_name))

    def test_launch_audit(self):
        """Test the audit template panel "Launch Audit" row button

        * Loads the audit template panel
        * Click on the button "Launch Audit"
        * Checks the audits page for audit template name in page
        """
        audit_template_page = \
            self.home_pg.go_to_optimization_audittemplatespage()
        self.assertTrue(
            audit_template_page.launch_audit(self.audit_template_name))
