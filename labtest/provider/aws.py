# -*- coding: utf-8 -*-
import boto3
from botocore.exceptions import ClientError
from fabric.api import env, run


def _authenticate_to_registry():
    """
    Authenticate to the ECR registry for docker
    """
    run('eval $(aws ecr get-login --no-include-email --region us-east-1)')


def _repository_exists(repo_name):
    """
    Return True if the specified repository exists
    """
    ecr = boto3.client('ecr')
    try:
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        if len(response['repositories']) == 1:
            return response['repositories'][0]
        else:
            raise Exception('Multiple repositories named "{}"'.format(repo_name))
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            return False
        else:
            raise e


def _get_or_create_repository():
    """
    Create a new Docker repository on ECR using the app_name/instance_name as
    the name of the repo

    returns the repository URL
    """
    import json

    lifecycle_policy = {
        "rules": [
            {
                "rulePriority": 1,
                "description": "Keep only one untagged image, expire all others",
                "selection": {
                    "tagStatus": "untagged",
                    "countType": "imageCountMoreThan",
                    "countNumber": 1
                },
                "action": {
                    "type": "expire"
                }
            }
        ]
    }
    repo_name = '{app_name}/{instance_name}'.format(**env)
    existing_repo = _repository_exists(repo_name)
    if not existing_repo:
        ecr = boto3.client('ecr')
        try:
            response = ecr.create_repository(repositoryName=repo_name)
            url = response['repository']['repositoryUri']
            ecr.put_lifecycle_policy(
                repositoryName=repo_name,
                lifecyclePolicyText=json.dumps(lifecycle_policy))
            return url
        except ClientError as e:
            raise e
    else:
        return existing_repo['repositoryUri']


def _delete_repository():
    """
    Delete an existing Docker repository on ECR using the app_name/instance_name as
    the name of the repo
    """
    repo_name = '{app_name}/{instance_name}'.format(**env)
    existing_repo = _repository_exists(repo_name)
    if existing_repo:
        ecr = boto3.client('ecr')
        try:
            ecr.delete_repository(repositoryName=repo_name, force=True)
        except ClientError as e:
            raise e


def _upload_to_repository():
    """
    Tag the docker image, upload to repository
    """
    kwargs = {
        'project_name': '{}/{}'.format(env.app_name, env.instance_name),
        'repository': env.repository_url,
    }
    docker_cmd = "docker tag {project_name} {repository}:latest".format(**kwargs)
    run(docker_cmd)

    print "Pushing to {repository}".format(**kwargs)
    docker_cmd = "eval $(aws ecr get-login --no-include-email --region us-east-1) && " \
                "docker push {repository}:latest".format(**kwargs)
    run(docker_cmd)
