import os

from abc import ABCMeta, abstractmethod
from kubernetes import client
from aion.kanban import KanbanConnection
from k8s.deployment import Deployment
from k8s.service import Service
from manifestJson import ManifestJson
from const import SUCCEED_STATUS_INDEX, FAILED_STATUS_INDEX


class Controller(metaclass=ABCMeta):
    def __init__(self, manifest_json: ManifestJson, conn: KanbanConnection, metadata):
        self.manifest_json = manifest_json
        self.conn = conn
        self.metadata = metadata
        self.controller_list = []

    @abstractmethod
    def start(self):
        pass

    def _set_k8s_conf(self):
        self.k8s_conf = client.Configuration()
        self.k8s_conf.verify_ssl = True
        self.k8s_conf.host = "https://" + os.environ.get("KUBERNETES_SERVICE_HOST")
        self.k8s_conf.api_key["authorization"] = self._get_token()
        self.k8s_conf.api_key_prefix["authorization"] = "Bearer"
        self.k8s_conf.ssl_ca_cert = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

    def _set_controller_list(self):
        self.controller_list.append(self._create_deployment())

        if self.manifest_json.is_port_config_list():
            self.controller_list.append(self._create_service())

    def _get_token(self):
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token") as f:
            return f.read()

    def _create_deployment(self) -> Deployment:
        return Deployment(
            self.k8s_conf,
            self.manifest_json.microservice_name,
            self.manifest_json.remote_image_name,
            self.manifest_json.port_config_list,
            self.manifest_json.envs,
            self.manifest_json.volume_mounts,
            self.manifest_json.volumes,
            self.manifest_json.service_account,
            self.manifest_json.prior_device_name,
            self.manifest_json.namespace,
        )

    def _create_service(self) -> Service:
        return Service(
            self.k8s_conf,
            self.manifest_json.microservice_name,
            self.manifest_json.service_type,
            self.manifest_json.port_config_list,
            self.manifest_json.namespace,
        )

    def _output_kanban_with_success(self):
        self.metadata["status"] = SUCCEED_STATUS_INDEX
        self.metadata["error"] = ""

        self.conn.output_kanban(
            result=True,
            metadata=self.metadata,
            device_name=self.manifest_json.prior_device_name,
        )

    def _output_kanban_with_error(self):
        self.metadata["status"] = FAILED_STATUS_INDEX
        self.metadata["error"] = ""

        prior_device_name = self.manifest_json.prior_device_name
        if prior_device_name is None:
            prior_device_name = os.environ.get("PRIOR_DEVICE_NAME")

        self.conn.output_kanban(
            result=False,
            metadata=self.metadata,
            device_name=prior_device_name,
        )
