import docker
import networkx as nx

from hierarchy_builder.utils.logger import logger

def get_images_for_rebuild(graph: nx.classes.digraph.DiGraph, diff: list) -> list:
    result = []
    for i in diff:
        temp = []
        for j in diff:
            try:
                if i in list(nx.nodes(nx.dfs_tree(graph, j)))[1:]:
                    temp.append(i)
            except Exception as e:
                logger.error(f"{e} Please check heararchy in tree.txt.")   
        if not temp:
            result.append(i)
    return result


def buld_docker_image(client: docker.client.DockerClient, image: str,
                      tag: str, buildargs: dict) -> bool:
    try:
        response = client.images.build(
            path=".",
            dockerfile=f'./{image}/Dockerfile',
            tag=tag,
            buildargs=buildargs,
            platform="linux/amd64",
            nocache=True
        )
        log = response[-1]
        for line in log:
            logger.info(line)
        if 'error' in log:
            raise Exception(log['error'])
        return True
    except Exception as e:
        logger.error(f"Error during build {image}: {str(e)}")


def push_docker_image(client: docker.client.DockerClient, tag: str) -> bool:
    try:
        response = [line for line in client.images.push(
            tag, stream=True, decode=True)]
        for line in response:
            if 'error' in line:
                raise Exception(line['errorDetail']['message'])
        return True
    except Exception as e:
        logger.error(f"Error during push {tag}: {str(e)}")
