import click
import docker
import networkx as nx
import functools

from hierarchy_builder import config
from hierarchy_builder.scripts import build_images, show_graph
from hierarchy_builder.utils import build_graph, git_tag_manager
from hierarchy_builder.utils.logger import logger


def shared_option(func):
    @click.option(
        "--tree-file",
        help="Path to file with hierarchy",
        type=str,
        required=True,
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@click.group()
def cli():
    """Application command line interface"""
    pass


@cli.command()
@shared_option
@click.option("--git-diff", help="Git diff after merge (newline-separated)", type=str, required=True)
@click.option("--push", help="Push image(s) after build")
@click.option("--disable-deps", help="Disable building of dependencies")
@click.option("--bump-type", help="Type of version bump (major, minor, patch)", type=str, default="patch")
@click.option("--dry-run", help="Enable dry run mode")
def build_hierarchy(tree_file: str, git_diff: str, push: bool,
                    disable_deps: bool, bump_type: str, dry_run: bool):
    """Build images according to the hierarchy"""
    if dry_run:
        click.echo("Script is running in dry run mode")
    else:
        click.echo("Building images according to hierarchy")

    run_build_process(tree_file, git_diff, push,
                      disable_deps, bump_type, dry_run)


@cli.command()
@shared_option
def show_hierarchy(tree_file: str):
    """Visualize the images hierarchy"""
    G, nodes = build_graph.build_graph(tree_file)
    show_graph.visualize_graphs(G, len(nodes))


def run_build_process(tree_file: str, git_diff: str, push: bool,
                      disable_deps: bool, bump_type: str, dry_run: bool):
    G, _ = build_graph.build_graph(tree_file)
    diff_files = git_diff.strip().splitlines()
    images_to_rebuild = build_images.get_images_for_rebuild(G, diff_files)

    client = docker.from_env()
    built_images = []

    for root_image in images_to_rebuild:
        if disable_deps:
            image_nodes = [root_image]
        else:
            logger.info(
                "The following image(s) will rebuild according to hierarhy")
            nx.write_network_text(G, with_labels=True, sources=[root_image],
                                  max_depth=None, ascii_only=False, vertical_chains=False)
            image_nodes = list(nx.nodes(nx.dfs_tree(G, root_image)))          
        for image in image_nodes:
            if image in config.exclude_images:
                logger.info(f"Skipping {image} (excluded)")
                continue

            tag_info = process_image_tagging(image, bump_type, G)
            if not tag_info:
                continue

            tag, build_args = tag_info
            logger.info(f"Preparing to build: {tag}")
            built_images.append(tag)

            if not dry_run:
                if build_images.buld_docker_image(client, image, tag, build_args):
                    logger.info(f"Successfully built: {tag}")
                    new_git_tag = f"{tag.split(':')[-1]}@{image}"
                    if git_tag_manager.add_git_tag(new_git_tag, "local"):
                        logger.info(f"Local git tag {new_git_tag} successfully added")

                    if push:
                        logger.info(f"Pushing image: {tag}")
                        if build_images.push_docker_image(client, tag):
                            logger.info(f"Successfully pushed: {tag}")
                            if git_tag_manager.add_git_tag(new_git_tag, "remote"):
                                logger.info(f"Remote git tag {new_git_tag} successfully added")
                            

    logger.info("Built image list:\n" + "\n".join(built_images))


def process_image_tagging(image: str, bump_type: str, G: nx.DiGraph):
    git_tags = git_tag_manager.get_local_git_tags(image)
    last_tag = git_tag_manager.get_last_tag(git_tags) if git_tags else "0.0.0"
    logger.info(f"{image} latest tag: {last_tag}")

    new_tag = git_tag_manager.bump_version(last_tag, bump_type)
    logger.info(f"{image} new tag: {new_tag}")

    parent = next(G.predecessors(image), None)
    build_args = dict(config.images[image]['args'])

    if parent:
        parent_tags = git_tag_manager.get_local_git_tags(parent)
        if not parent_tags:
            logger.error(f"No tags found for parent image: {parent}")
            return None
        parent_tag = git_tag_manager.get_last_tag(parent_tags)
        build_args.update({"PARENT": parent, "SEM_VER": parent_tag})
        logger.info(f"{image} depends on {parent}:{parent_tag}")
    else:
        logger.info(f"{image} is a root image")

    tag = f"{config.docker_registry}/{config.images[image]['name']}:{new_tag}"
    return tag, build_args


if __name__ == "__main__":
    cli()
