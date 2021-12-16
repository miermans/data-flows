# data-flows
Data flows orchestrated using Prefect

## Local development
1. Create a Prefect API key on the [API keys page](https://cloud.prefect.io/user/keys).
2. Create a `.env` file in the project root with the following contents, using the above Prefect API key:
    ```
    PREFECT__CLOUD__API_KEY=********
    AWS_PROFILE=pocket-dev-PocketSSOBackend
    AWS_DEFAULT_REGION=us-east-1
    PREFECT_TASK_ROLE_ARN=the task role (e.g. DataFlows-Dev-RunTaskRole) you want your tasks to use
    ```
3. Choose how to run code:
   1. Docker compose: consistent environment
   2. pipenv: fast startup

### Option 1: Docker compose
Prerequisites:
- docker

Steps:
1. Run `docker compose build && docker compose up`
2. In PyCharm, [Configuring Docker Compose as a remote interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote)

### Option 2: PyCharm and pipenv
Prerequisites:
- pipenv
- python 3.9 ([pyenv](https://github.com/pyenv/pyenv) makes it easy to manage Python versions)

Steps:
1. Run `pipenv install` in the project root directory.
2. In PyCharm, [configure pipenv as the interpreter](https://www.jetbrains.com/help/pycharm/pipenv.html#pipenv-existing-project).

## Road map

### CI/CD
As we're experimenting with Prefect we've deployed flows from our local machines. When we productionalize Prefect,
we'll want to automate this. It might look something like this: 

1. Collect all flows, and for each flow:
   1. Set the storage and run configuration.
   2. Register the flow with Prefect.

There's [a Github discussion on Prefect CI/CD patterns](https://github.com/PrefectHQ/prefect/discussions/4042)
with more details and more patterns.

## References
- Experimental cloud account: https://cloud.prefect.io/mathijs-getpocket-com-s-account
- Running Prefect locally
  - [Prefect Getting Started](https://docs.prefect.io/orchestration/getting-started/quick-start.html)
- Running Prefect on AWS
  - [Prefect architecture diagram](https://docs.prefect.io/orchestration/#architecture-overview) 
  - [ECS Agent](https://docs.prefect.io/orchestration/agents/ecs.html#running-ecs-agent-in-production)
  - [ECS Agent CLI](https://docs.prefect.io/api/latest/cli/agent.html#ecs-start)
  - [ECSRun Run Configuration](https://docs.prefect.io/api/latest/run_configs.html#ecsrun)
  - [S3 Storage](https://docs.prefect.io/api/latest/storage.html#s3)
  - [Result Serializers](https://docs.prefect.io/api/latest/engine/serializers.html#serializer)
