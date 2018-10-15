import boto3
import json
import os

def get_repo_details_from_event(gh_data):
    repo = gh_data["repository"]["name"]
    owner = gh_data["repository"]["owner"]["name"]
    branch = gh_data["ref"].replace("refs/heads/", "")
    commit = gh_data["commits"][0]["id"]

    return repo, owner, branch, commit

def get_pipeline_stack_for_branch(branch):
    return "pipeline-for-{}".format(branch.replace("/", "-"))

def lambda_handler(event, context):
    (repo, owner, branch, commit) = get_repo_details_from_event(event)

    pipeline_name = get_pipeline_stack_for_branch(branch)

    print("> CloudFormation stack for pipeline: {}".format(pipeline_name))
    print("> Repository: {}".format(repo))
    print("> Owner: {}".format(owner))
    print("> Branch: {}".format(branch))
    print("> Commit: {}".format(commit))

    cb = boto3.client('codebuild')

    print("Starting master build...")
    res = cb.start_build(
        projectName='codesuite-gitflow',
        sourceVersion=commit,
        environmentVariablesOverride=[
            {
                'name': 'CAFONSOP_PIPELINE_STACK',
                'value': pipeline_name,
                'type': 'PLAINTEXT'
            },
            {
                'name': 'CAFONSOP_GITHUB_USER',
                'value': owner,
                'type': 'PLAINTEXT'
            },
            {
                'name': 'CAFONSOP_GITHUB_REPO',
                'value': repo,
                'type': 'PLAINTEXT'
            },
            {
                'name': 'CAFONSOP_GITHUB_BRANCH',
                'value': branch,
                'type': 'PLAINTEXT'
            },
            {
                'name': 'CAFONSOP_GITHUB_TOKEN',
                'value': os.environ['GITHUB_TOKEN'],
                'type': 'PLAINTEXT'
            },
            {
                'name': 'CAFONSOP_ECS_CLUSTER',
                'value': os.environ['ECS_CLUSTER'],
                'type': 'PLAINTEXT'
            },
            {
                'name': 'CAFONSOP_ECS_SERVICE',
                'value': os.environ['ECS_SERVICE'],
                'type': 'PLAINTEXT'
            }
        ]
    )

    print(json.dumps(res, sort_keys=True, indent=4, default=str))

    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }
