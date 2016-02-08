# -*- encoding: utf-8 -*-
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

from django.conf import urls

from watcher_dashboard.content.action_plans import views


urlpatterns = urls.patterns(
    'watcher_dashboard.content.action_plans.views',
    urls.url(r'^$',
             views.IndexView.as_view(), name='index'),
    urls.url(r'^(?P<action_plan_id>[^/]+)/detail$',
             views.DetailView.as_view(), name='detail'),
    urls.url(r'^archive/$',
             views.ArchiveView.as_view(), name='archive'),
)
