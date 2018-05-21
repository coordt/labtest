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
        cmd = ' '.join([
            'aws ecr describe-repositories',
            '--region us-east-1',
            '--query "repositories[0]"',
            '--repository-names "{}"'.format(repo_name)])
        output = run(cmd, quiet=env.quiet)
        if output.return_code != 0 and 'RepositoryNotFoundException' in output:
            return False
        elif output.return_code != 0 and 'RepositoryNotFoundException' not in output:
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
    cmd = ' '.join([
        'aws ecr put-lifecycle-policy',
        '--repository-name {}'.format(repo_name),
        '--region us-east-1',
        '--output json',
        '--lifecycle-policy-text \'{}\''.format(json.dumps(lifecycle_policy))
    ])
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
    existing_repo = _repository_exists(repo_name)
    if not existing_repo:
        cmd = ' '.join([
            'aws ecr create-repository',
            '--region us-east-1',
            '--repository-name {}'.format(repo_name),
            '--output json',
        ])
        output = run(cmd, quiet=env.quiet)
        if output.return_code == 0:
            response = json.loads(output)
            url = response['repository']['repositoryUri']
            _add_repository_lifecycle(repo_name)
            return url
        else:
            raise Exception(output)
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
        cmd = ' '.join([
            'aws ecr delete-repository',
            '--region us-east-1',
            '--force',
            '--repository-name {}'.format(repo_name),
            '--output json',
        ])
        output = run(cmd, quiet=env.quiet)
        if output.return_code != 0:
            raise Exception(output)


def _upload_to_repository():
    """
    Tag the docker image, upload to repository
    """
    kwargs = {
        'project_name': '{}/{}'.format(env.app_name, env.instance_name),
        'repository': env.repository_url,
    }
    docker_cmd = "docker tag {project_name} {repository}:latest".format(**kwargs)
    run(docker_cmd, quiet=env.quiet)

    click.echo("Pushing to {repository}".format(**kwargs))
    docker_cmd = "eval $(aws ecr get-login --no-include-email --region us-east-1) && " \
                "docker push {repository}:latest".format(**kwargs)
    run(docker_cmd, quiet=env.quiet)
