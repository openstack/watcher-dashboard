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

import logging

from django.utils.translation import gettext_lazy as _
from horizon import forms
from horizon import messages

from watcher_dashboard.api import watcher
from watcher_dashboard.common import client as common_client
from watcher_dashboard.common import exceptions as watcher_exc


LOG = logging.getLogger(__name__)


class SkipActionForm(forms.SelfHandlingForm):
    """Form to skip an action or update its skip reason."""

    action_id = forms.CharField(widget=forms.HiddenInput())
    reason = forms.CharField(
        label=_("Reason for skipping"),
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_("Optional reason for skipping this action."))

    def clean(self):
        """Validate the action exists and is in a skippable state."""
        cleaned = super().clean()
        action_id = cleaned.get('action_id')
        if not action_id:
            # Django calls clean() even when required fields fail
            # validation. Without this guard, None would be passed
            # to the API as the action ID.
            return cleaned
        action = watcher.Action.get(
            self.request, action_id)
        if action is None:
            raise forms.ValidationError(
                _('Unable to retrieve action.'))
        if action.state not in ('PENDING', 'SKIPPED'):
            raise forms.ValidationError(
                _('Action must be in PENDING or SKIPPED '
                  'state.'))
        reason = cleaned.get('reason', '').strip()
        if action.state == 'SKIPPED' and not reason:
            raise forms.ValidationError(
                _('A reason is required when updating a '
                  'skipped action.'))
        cleaned['_action'] = action
        return cleaned

    def handle(self, request, data):
        """Submit skip request to the Watcher API."""
        action_id = data['action_id']
        reason = data.get('reason', '').strip() or None
        action = data['_action']

        state = None if action.state == 'SKIPPED' else 'SKIPPED'
        try:
            result = watcher.Action.update(
                request, action_id, state=state, reason=reason,
                api_version=common_client.MV_SKIP_ACTION)
        except watcher_exc.WatcherDashboardException as exc:
            LOG.info("Skip action validation error: %s", exc)
            messages.error(request, str(exc))
            return False

        if result is None:
            messages.warning(
                request,
                _('Skip is not supported by this server.'))
            return False

        if state is None:
            msg = _('Skip reason was successfully updated.')
        else:
            msg = _('Action was successfully skipped.')
        messages.success(request, msg)
        return True
