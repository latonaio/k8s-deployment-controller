import docker
import os

from aion.logger import lprint
from const import LOCAL_IMAGE_REGISTRY


class Docker():
    def __init__(self):
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.username = os.environ.get("REGISTRY_USER")
        self.password = os.environ.get("REGISTRY_PASSWORD")
        self._login()

    def _login(self):
        self.client.login(
            username=self.username, password=self.password, registry=LOCAL_IMAGE_REGISTRY)

    def push_to_local_registry(self, remote_image_name, local_image_name):
        try:
            image = self.client.images.get(remote_image_name)
            image.tag(local_image_name)

            lprint(f"tagged {remote_image_name} to {local_image_name}")

            ret = self.client.images.push(local_image_name)
            if "err" in ret:
                raise RuntimeError(f"failed to push image {local_image_name}")

            lprint(ret)
            return True

        except Exception as e:
            raise RuntimeError(e)

