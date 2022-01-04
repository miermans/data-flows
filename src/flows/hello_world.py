from os import environ

import prefect
from prefect import task, Flow
from prefect.run_configs import ECSRun
import pandas
import pyarrow
import fastparquet


@task
def log_versions():
    logger = prefect.context.get("logger")
    logger.info(f"pandas version = {pandas.__version__}")
    logger.info(f"pyarrow version = {pyarrow.__version__}")
    logger.info(f"fastparquet version = {fastparquet.__version__}")


with Flow("hello_world") as flow:
    log_versions()

if __name__ == "__main__":
    flow.run()
