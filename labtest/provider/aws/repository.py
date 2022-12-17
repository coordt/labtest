# -*- coding: utf-8 -*-
from fabric.api import env, run
from fabric.context_managers import hide
import json
import click


def _authenticate_to_registry():
    """
    Authenticate to the ECR for docker
    """
    run('eval $(aws ecr get-login --no-include-email --region us-east-1)')


def _repository_exists(repo_name):
    """
    Return True if the specified repository exists
    """
    with hide('everything'):
        cmd = ' '.join(
            [
                'aws ecr describe-repositories',
                '--region us-east-1',
                '--query "repositories[0]"',
                f'--repository-names "{repo_name}"',
            ]
        )
        output = run(cmd, quiet=env.quiet)
        if output.return_code != 0 and 'RepositoryNotFoundException' in output:
            return False
        elif output.return_code != 0:
            raise Exception(output)
        else:
            return json.loads(output)


def _add_repository_lifecycle(repo_name):
    """
    Add the lifecycle policy to the repository
    """
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
    cmd = ' '.join(
        [
            'aws ecr put-lifecycle-policy',
            f'--repository-name {repo_name}',
            '--region us-east-1',
            '--output json',
            f"--lifecycle-policy-text \'{json.dumps(lifecycle_policy)}\'",
        ]
    )
    output = run(cmd, quiet=env.quiet)
    if output.return_code != 0:
        raise Exception(output)


def _get_or_create_repository():
    """
    Create a new Docker repository on ECR using the app_name/instance_name as
    the name of the repo

    returns the repository URL
    """
    repo_name = '{app_name}/{instance_name}'.format(**env)
    if existing_repo := _repository_exists(repo_name):
        return existing_repo['repositoryUri']
    cmd = ' '.join(
        [
            'aws ecr create-repository',
            '--region us-east-1',
            f'--repository-name {repo_name}',
            '--output json',
        ]
    )
    output = run(cmd, quiet=env.quiet)
    if output.return_code != 0:
        raise Exception(output)
    response = json.loads(output)
    url = response['repository']['repositoryUri']
    _add_repository_lifecycle(repo_name)
    return url


def _delete_repository():
    """
    Delete an existing Docker repository on ECR using the app_name/instance_name as
    the name of the repo
    """
    repo_name = '{app_name}/{instance_name}'.format(**env)
    if existing_repo := _repository_exists(repo_name):
        cmd = ' '.join(
            [
                'aws ecr delete-repository',
                '--region us-east-1',
                '--force',
                f'--repository-name {repo_name}',
                '--output json',
            ]
        )
        output = run(cmd, quiet=env.quiet)
        if output.return_code != 0:
            raise Exception(output)


def _upload_to_repository():
    """
    Tag the docker image, upload to repository
    """
    kwargs = {
        'project_name': f'{env.app_name}/{env.instance_name}',
        'repository': env.repository_url,
    }
    docker_cmd = "docker tag {project_name} {repository}:latest".format(**kwargs)
    run(docker_cmd, quiet=env.quiet)

    click.echo("Pushing to {repository}".format(**kwargs))
    docker_cmd = "eval $(aws ecr get-login --no-include-email --region us-east-1) && " \
                "docker push {repository}:latest".format(**kwargs)
    run(docker_cmd, quiet=env.quiet)
