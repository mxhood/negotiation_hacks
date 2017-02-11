# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Zones service."""

from googlecloudsdk.api_lib.compute import constants


def List(compute_client, project):
  """Return list of zonal resources."""
  client = compute_client.apitools_client
  messages = compute_client.messages
  request = (client.zones,
             'List',
             messages.ComputeZonesListRequest(
                 project=project,
                 maxResults=constants.MAX_RESULTS_PER_PAGE))
  return compute_client.MakeRequests([request])
