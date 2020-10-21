import time

from kubernetes import client
from kubernetes.client.rest import ApiException
from aion.logger import lprint
from k8s.kubernetes import Kubernetes


class Deployment(Kubernetes):
    def __init__(self, conf, name, image_name, port_config_list, envs, volume_mounts, volumes, service_account_name, prior_device_name, namespace):
        super().__init__()
        self.configuration = conf
        self.sleep_time = 5
        self.retry_cnt = 60
        self.name = name
        self.image_name = image_name
        self.port_config_list = port_config_list
        self.envs = envs
        self.volume_mounts = volume_mounts
        self.volumes = volumes
        self.service_account_name = service_account_name
        self.prior_device_name = prior_device_name
        self.namespace = namespace
        self.apps_v1 = client.AppsV1Api(client.ApiClient(self.configuration))
        self.v1 = client.CoreV1Api(client.ApiClient(self.configuration))

    def apply(self):
        try:
            if self._isExist():
                self.apps_v1.replace_namespaced_deployment(
                    self.name,
                    self.namespace,
                    self._get_body()
                )
            else:
                self.apps_v1.create_namespaced_deployment(
                    self.namespace,
                    self._get_body(),
                )

            if self.is_pod_with_retry() is False:
                raise RuntimeError(f"timeout pull image {self.name}")

        except ApiException as e:
            raise RuntimeError(e)

    def _isExist(self):
        try:
            ret = self.apps_v1.list_namespaced_deployment(self.namespace)
            for item in ret.items:
                if item.metadata.name == self.name:
                    return True
            return False

        except ApiException as e:
            raise RuntimeError(e)

    def _get_body(self):
        return client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=client.V1DeploymentSpec(
                replicas=1,
                template=self._get_pod_template(),
                selector={'matchLabels': {"run": self.name}}
            )
        )

    def is_pod_with_retry(self):
        if self._is_pod():
            return True

        for i in range(self.retry_cnt):
            lprint("retrying in " + str(self.sleep_time) + " seconds...")
            time.sleep(self.sleep_time)

            if self._is_pod():
                return True

        return False

    def _is_pod(self):
        try:
            ret = self.v1.list_namespaced_pod(self.namespace)
            if ret is None:
                raise RuntimeError(f"can't list namespaced pod")

            for pod in ret.items:
                if self.name in pod.metadata.name and pod.status.container_statuses:
                    for status in pod.status.container_statuses:
                        if status.state.waiting and status.state.waiting.reason == "ImagePullBackOff":
                            raise RuntimeError(f"failed to pull image {self.image_name}")
                        elif status.state.waiting and status.state.waiting.reason == "CrashLoopBackOff":
                            lprint(f"{self.name} is CrashLoopBackOff")
                            return True
                        elif status.ready:
                            lprint(f"{self.name} is Running")
                            return True

        except ApiException as e:
            raise RuntimeError(e)

    def _get_pod_template(self):
        return client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"run": self.name}),
            spec=client.V1PodSpec(
                service_account_name=self.service_account_name,
                image_pull_secrets=[client.V1LocalObjectReference(
                    name=self.prior_device_name + "-registry"
                )],
                containers=[self._get_container()],
                volumes=self._get_volumes(),
            )
        )

    def _get_container(self):
        return client.V1Container(
            name=self.name,
            image=self.image_name,
            image_pull_policy="Always",
            ports=self._get_container_ports(),
            env=self._get_envs(),
            volume_mounts=self._get_volume_mounts(),
        )

    def _get_container_ports(self):
        container_ports = []
        if self.port_config_list and len(self.port_config_list) > 0:
            for port_config in self.port_config_list:
                container_ports.append(client.V1ContainerPort(container_port=int(port_config.get("port"))))

        return container_ports

    def _get_envs(self):
        envs = []
        if self.envs and self.envs != "":
            for name, item in self.envs.items():
                envs.append(client.V1EnvVar(
                    name=name,
                    value=item
                ))

        return envs

    def _get_volume_mounts(self):
        volume_mount_list = []
        if self.volume_mounts and self.volume_mounts != "":
            for name, path in self.volume_mounts.items():
                volume_mount_list.append(client.V1VolumeMount(
                    name=name,
                    mount_path=path
                ))

        return volume_mount_list

    def _get_volumes(self):
        volume_list = []
        if self.volumes and self.volumes != "":
            for name, item in self.volumes.items():
                volume_list.append(client.V1Volume(
                    name=name,
                    host_path=client.V1HostPathVolumeSource(
                        path=item.get("path")
                    )
                ))

        return volume_list
