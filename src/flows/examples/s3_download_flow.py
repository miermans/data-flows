from prefect import Flow
from prefect.tasks.aws.s3 import S3Download

from utils.flow import get_flow_name

FLOW_NAME = get_flow_name(__file__)

s3_bucket_source = 'transport-tracker'
s3_bucket_key='mvg/departures/1587357722.json'

with Flow(FLOW_NAME) as flow:
    s3download_result = S3Download()(key=s3_bucket_key, bucket=s3_bucket_source, as_bytes=True)

if __name__ == "__main__":
    flow.run()
