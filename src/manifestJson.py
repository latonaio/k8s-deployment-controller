from const import LOCAL_IMAGE_REGISTRY, NODE_PORT, CLUSTER_IP


class ManifestJson():
    required_keys = [
        "priorDeviceName", "deviceName", "projectName",
        "ip", "port", "microserviceName", "dockerTag"
    ]

    def __init__(self, metadata):
        self.metadata = metadata

    def validate(self):
        for key in self.required_keys:
            if key not in self.metadata:
                raise RuntimeError(f"Not found '{key}' in metadadata.")

    def is_port_config_list(self):
        return self.port_config_list and len(self.port_config_list) > 0

    @property
    def microservice_name(self):
        return self.metadata.get("microserviceName")

    @property
    def remote_registry(self):
        return self.metadata.get("ip") + ":" + self.metadata.get("port")

    @property
    def remote_image_name(self):
        return self.remote_registry + "/" + self.microservice_name + ":" + self.metadata.get("dockerTag")

    @property
    def local_image_name(self):
        return LOCAL_IMAGE_REGISTRY + "/" + self.microservice_name + ":" + self.metadata.get("dockerTag")

    @property
    def service_type(self):
        if self.metadata.get("serviceType") is None:
            return CLUSTER_IP
        elif self.metadata.get("serviceType") == NODE_PORT:
            return NODE_PORT
        elif self.metadata.get("serviceType") == "nodePort":
            return NODE_PORT

        return CLUSTER_IP

    @property
    def port_config_list(self):
        return self.metadata.get("portConfigList")

    @property
    def envs(self):
        return self.metadata.get("env")

    @property
    def volume_mounts(self):
        return self.metadata.get("volumeMounts")

    @property
    def volumes(self):
        return self.metadata.get("volumes")

    @property
    def service_account(self):
        return self.metadata.get("serviceAccountName")

    @property
    def prior_device_name(self):
        return self.metadata.get("priorDeviceName")

    @property
    def namespace(self):
        return self.metadata.get("projectName").lower()
