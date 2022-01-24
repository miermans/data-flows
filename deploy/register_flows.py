#!/usr/bin/env python

import copy
import os
from os import environ
from typing import Any, Dict

import prefect
import yaml
from prefect.run_configs import RunConfig, ECSRun
from prefect.storage import Storage, S3
from prefect.utilities.filesystems import read_bytes_from_path


class FlowDeployment:
    """
    Discovers, builds, and registers flows with Prefect Cloud.
    """

    def __init__(self, project_name: str, storage: Storage, run_config: RunConfig):
        """
        :param project_name: Name of the Prefect project to deploy flows to.
        :param storage: Prefect storage option: https://docs.prefect.io/orchestration/execution/storage_options.html
        :param run_config: Prefect run config: https://docs.prefect.io/orchestration/flow_config/run_configs.html
        """
        self.project_name = project_name
        self.storage = storage
        self.run_config = run_config

    def register_flow(self, file_path: str):
        """
        Register a single flow with Prefect
        :param file_path: Path of the Python file where the flow is defined.
        """
        flow = prefect.utilities.storage.extract_flow_from_file(file_path)
        # If storage objects are shared across flows the flow will be built multiple times.
        flow.storage = copy.deepcopy(self.storage)
        flow.run_config = copy.deepcopy(self.run_config)
        # flow.register builds the flow and registers it with Prefect.
        flow.register(self.project_name)

    def register_all_flows(self, flows_path: str):
        """
        Discover all flows in the given directory, including recursively, and register them.
        :param flows_path: Directory path containing Prefect flows.
        """
        for flow_path in self._get_all_python_files(flows_path):
            print(f"Registering {flow_path}")
            self.register_flow(flow_path)

    def _get_all_python_files(self, dir_path: str) -> str:
        """
        Get all Python files in the given directory, including sub-directories.
        :param dir_path: Directory path containing Python files.
        :return: List of full paths for all Python files in dir_path
        """
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                # Ignore __pycache__ and other non-python files by filtering on .py extension.
                if file.endswith(".py") and file != '__init__.py':
                    yield os.path.join(root, file)


def create_ecs_run(
        environment: str,
        project_name: str,
        image: str,
        task_definition_arn: str,
) -> ECSRun:
    """
    Creates an ECSRun Prefect run configuration, that determines how the Prefect ECS agent will start tasks.
    :param environment: 'Prod' or 'Dev'
    :param project_name: Prefect project name. Currently 'main' or 'dev'.
    :param image: ECR image ARN
    :param task_definition_arn: ARN of task definition for the ECS task. The Prefect ECS agent will set some additional
                                fields through boto3 run_task kwargs, for example the Docker command to start the flow.
    :return: The ECSRun object
    """
    return ECSRun(
        labels=[PREFECT_PROJECT_NAME],
        image=PREFECT_IMAGE,
        task_definition_arn=task_definition_arn,
    )


# This script is executed in CodeBuild using buildspec_register_flows.yml
if __name__ == "__main__":
    # TODO: It would be cleaner to use command line arguments instead of loading values from environment variables.
    ENVIRONMENT = environ['ENVIRONMENT']
    PREFECT_PROJECT_NAME = environ['PREFECT_PROJECT_NAME']
    PREFECT_STORAGE_BUCKET = environ['PREFECT_STORAGE_BUCKET']
    PREFECT_IMAGE = environ['PREFECT_IMAGE']
    PREFECT_TASK_DEFINITION_ARN = environ['PREFECT_TASK_DEFINITION_ARN']

    FLOWS_PATH = r'./src/flows'
    TASK_DEFINITION_PATH = os.path.join(
        os.path.dirname(__file__), "task_definition.yaml"
    )

    ecs_run = create_ecs_run(
        environment=ENVIRONMENT,
        project_name=PREFECT_PROJECT_NAME,
        image=PREFECT_IMAGE,
        task_definition_arn=PREFECT_TASK_DEFINITION_ARN,
    )

    FlowDeployment(
        project_name=PREFECT_PROJECT_NAME,
        storage=S3(
            bucket=PREFECT_STORAGE_BUCKET,
            add_default_labels=False,
        ),
        run_config=ecs_run,
    ).register_all_flows(FLOWS_PATH)