log_level = "info"
base_image = "debian"  # change with your base image
base_image_tag = "stable-slim"  # change with your base image tag
dockerfile = "Dockerfile"
docker_registry = "docker.io"
share_args = {"DOCKER_REGISTRY": docker_registry}
exclude_images = []  # images for exclude during hierarchy build
images = {
    "cat": {
        "name": "cat",  # image name can be different
        "args": share_args | {"TAG": base_image_tag} | {"BASE_IMAGE": base_image}
    },
    "tiger": {
        "name": "tiger",
        "args": share_args
    },
    "leon": {
        "name": "leon",
        "args": share_args
    },
    "cheetah": {
        "name": "cheetah",
        "args": share_args
    },
    "leopard": {
        "name": "leopard",
        "args": share_args
    },
    "puma": {
        "name": "puma",
        "args": share_args
    },
    # "new_image": {
    #     "name": "name",
    #     "args": share_args | {"NEW_ARG_KEY": "new_arg_value"}
    # }
}
