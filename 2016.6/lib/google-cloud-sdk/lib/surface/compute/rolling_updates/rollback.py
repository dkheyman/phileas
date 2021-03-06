# Copyright 2014 Google Inc. All Rights Reserved.
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

"""rolling-updates rollback command."""

from googlecloudsdk.api_lib.compute import rolling_updates_util as updater_util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import resources
from googlecloudsdk.third_party.apitools.base.py import exceptions as apitools_exceptions


class Rollback(base.Command):
  """Rolls back an existing update."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument('update', help='Update id.')
    # TODO(user): Support --async which does not wait for state transition.

  def Run(self, args):
    """Run 'rolling-updates rollback'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Raises:
      HttpException: An http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing
          the command.
    """
    client = updater_util.GetApiClientInstance()
    messages = updater_util.GetApiMessages()

    ref = resources.Parse(
        args.update,
        collection='replicapoolupdater.rollingUpdates')
    request = messages.ReplicapoolupdaterRollingUpdatesRollbackRequest(
        project=ref.project,
        zone=ref.zone,
        rollingUpdate=ref.rollingUpdate)

    try:
      operation = client.rollingUpdates.Rollback(request)
      operation_ref = resources.Parse(
          operation.name,
          collection='replicapoolupdater.zoneOperations')
      result = updater_util.WaitForOperation(
          client, operation_ref, 'Initiating rollback of the update')
      if result:
        log.status.write('Initiated rollback of [{0}].\n'.format(ref))
      else:
        raise exceptions.ToolException(
            'could not initiate rollback of [{0}]'.format(ref))

    except apitools_exceptions.HttpError as error:
      raise exceptions.HttpException(updater_util.GetError(error))

Rollback.detailed_help = {
    'brief': 'Rolls back an existing update.',
    'DESCRIPTION': """\
        Rolls back the update in state ROLLING_FORWARD, ROLLING_BACK or PAUSED \
        (fails if the update is in any other state).
        No-op if invoked in state ROLLED_BACK.

        Rollback sets the template that the Managed Instance Group \
        used before the update was started and gradually restarts back to the \
        old template all instances that are running in the new template.
        """,
}
