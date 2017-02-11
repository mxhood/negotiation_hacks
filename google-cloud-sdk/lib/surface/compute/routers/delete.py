# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Command for deleting routers."""
from googlecloudsdk.api_lib.compute import base_classes


class Delete(base_classes.RegionalDeleter):
  """Delete Google Compute Engine routers."""

  @staticmethod
  def Args(parser):
    base_classes.RegionalDeleter.Args(parser, 'compute.routers')

  @property
  def service(self):
    return self.compute.routers

  @property
  def resource_type(self):
    return 'routers'


Delete.detailed_help = {
    'brief': 'Delete Google Compute Engine routers',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine
        routers. Routers can only be deleted when no other resources
        (e.g., virtual machine instances) refer to them.
        """,
}
