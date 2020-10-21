from kubernetes import client
from kubernetes.client.rest import ApiException
from k8s.kubernetes import Kubernetes


class Service(Kubernetes):
    def __init__(self, conf, name, service_type, port_config_list, namespace):
        super().__init__()
        self.configuration = conf
        self.name = name
        self.service_type = service_type
        self.port_config_list = port_config_list
        self.namespace = namespace
        self.v1 = client.CoreV1Api(client.ApiClient(self.configuration))

    def apply(self):
        try:
            if self._isExist():
                self.delete()

            return self.v1.create_namespaced_service(
                self.namespace,
                self._get_body(),
            )

        except ApiException as e:
            raise RuntimeError(e)

    def _isExist(self):
        try:
            ret = self.v1.list_namespaced_service(self.namespace)
            for item in ret.items:
                if item.metadata.name == self.name:
                    return True
            return False
        except ApiException as e:
            raise RuntimeError(e)

    def delete(self):
        try:
            return self.v1.delete_namespaced_service(self.name, self.namespace)
        except ApiException as e:
            raise RuntimeError(e)

    def _get_body(self):
        return client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=self._get_spec(),
        )

    def _get_spec(self):
        return client.V1ServiceSpec(
            selector={"run": self.name},
            type=self.service_type,
            ports=self._get_ports(),
        )

    def _get_ports(self):
        port_config_list = []
        for port_config in self.port_config_list:
            port_config_dict = {}

            if port_config.get("name") and port_config.get("name") != "":
                port_config_dict["name"] = port_config.get("name")

            if port_config.get("nodePort") and port_config.get("nodePort") != "":
                port_config_dict["nodePort"] = int(port_config.get("nodePort"))

            if port_config.get("port") and port_config.get("nodePort") != "":
                port_config_dict["port"] = int(port_config.get("port"))

            port_config_list.append(port_config_dict)

        return port_config_list

