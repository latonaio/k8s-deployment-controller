from aion.logger import lprint
from aion.kanban import KanbanConnection
from cri.docker import Docker
from controllers.controller import Controller
from manifestJson import ManifestJson


class ApplyController(Controller):
    def __init__(self, manifest_json: ManifestJson, conn: KanbanConnection, metadata):
        super().__init__(manifest_json, conn, metadata)

    def start(self):
        try:
            self.manifest_json.validate()
            self._set_k8s_conf()
            self._set_controller_list()

            for controller in self.controller_list:
                controller.apply()

            docker = Docker()
            docker.push_to_local_registry(self.manifest_json.remote_image_name, self.manifest_json.local_image_name)
            self._output_kanban_with_success()

        except Exception as e:
            lprint(e)
            self._output_kanban_with_error()
            lprint("keep alive...")
