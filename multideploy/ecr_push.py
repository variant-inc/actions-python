from multideploy.utils import docker_client

async def ecr_create():
    # check if repo already exists
    response = client.create_repository(
    repositoryName='project-a/nginx-web-app',
    )

async def ecr_push():
    # do login, then docker push
    docker_client.login()
    for line in  client.api.push('yourname/app', stream=True, decode=True):
        print(line)