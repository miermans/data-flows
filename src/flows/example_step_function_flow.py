from os import environ
import json

import prefect
from prefect import task, Flow
from prefect.run_configs import ECSRun
import uuid

from typing import Dict

from prefect import Task
from prefect.utilities.aws import get_boto_client
from prefect.utilities.tasks import defaults_from_attrs


# TODO: When https://github.com/PrefectHQ/prefect/pull/5231 is released, we can use Prefect's StepActivate again.
class StepActivate(Task):
    """
    Task for activating an AWS Step Function.

    Args:
        - state_machine_arn (str): the Amazon Resource Name (ARN) of the state machine
            to execute
        - execution_name (str): the name of the execution, this name must be unique for
            your AWS account, region, and state machine for 90 days
        - execution_input (str, optional): string that contains the JSON input data for
            the execution, defaults to `"{}"`
        - boto_kwargs (dict, optional): additional keyword arguments to forward to the boto client.
        - **kwargs (dict, optional): additional keyword arguments to pass to the
            Task constructor
    """

    def __init__(
        self,
        state_machine_arn: str = None,
        execution_name: str = None,
        execution_input: str = "{}",
        boto_kwargs: dict = None,
        **kwargs
    ):
        self.state_machine_arn = state_machine_arn
        self.execution_name = execution_name
        self.execution_input = execution_input

        if boto_kwargs is None:
            self.boto_kwargs = {}
        else:
            self.boto_kwargs = boto_kwargs

        super().__init__(**kwargs)

    @defaults_from_attrs(
        "state_machine_arn",
        "execution_name",
        "execution_input",
    )
    def run(
        self,
        credentials: dict = None,
        state_machine_arn: str = None,
        execution_name: str = None,
        execution_input: str = None,
    ) -> Dict:
        """
        Task run method. Activates AWS Step function.

        Args:
            - credentials (dict, optional): your AWS credentials passed from an upstream
                Secret task; this Secret must be a JSON string
                with two keys: `ACCESS_KEY` and `SECRET_ACCESS_KEY` which will be
                passed directly to `boto3`.  If not provided here or in context, `boto3`
                will fall back on standard AWS rules for authentication.
            - state_machine_arn (str): the Amazon Resource Name (ARN) of the state machine
                to execute
            - execution_name (str): the name of the execution, this name must be unique for
                your AWS account, region, and state machine for 90 days
            - execution_input (str, optional): string that contains the JSON input data for
                the execution, defaults to `"{}"`

        Returns:
            - dict: response from AWS StartExecution endpoint
        """
        if not state_machine_arn:
            raise ValueError("A state machine ARN must be provided")

        step_client = get_boto_client(
            "stepfunctions", credentials=credentials, **self.boto_kwargs
        )

        response = step_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=execution_name,
            input=execution_input,
        )

        return response


activate_step_function = StepActivate(
    state_machine_arn='arn:aws:states:us-east-1:410318598490:stateMachine:TimespentProspectsFlow',
    execution_input=json.dumps({
        "Parameters": "{}",
    }),
)

with Flow("step_function_flow") as flow:
    step_function_result = activate_step_function(execution_name=str(uuid.uuid4()))

if __name__ == "__main__":
    flow.run()
