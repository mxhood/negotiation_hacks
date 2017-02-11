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
"""Flags and helpers for the compute firewall-rules commands."""

from googlecloudsdk.command_lib.compute import flags as compute_flags


def FirewallRuleArgument(required=True, operation_type='create'):
  return compute_flags.ResourceArgument(
      resource_name='firewall',
      completion_resource_id='compute.firewalls',
      plural=False,
      required=required,
      global_collection='compute.firewalls',
      short_help='The name of the firewall rule to {0}.'.format(operation_type))
