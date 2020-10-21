import os
import logging

from time import sleep
from aion.logger import lprint, initialize_logger
from aion.microservice import Options, main_decorator
from aion.kanban import KanbanConnection, Kanban
from controllers.apply_controller import ApplyController
from controllers.delete_controller import DeleteController
from manifestJson import ManifestJson
from const import FAILED_STATUS_INDEX

KUBERNETES_PACKAGE = "kubernetes"
SERVICE_NAME = os.environ.get("SERVICE")


class Operator():
    connection_key_default = "default"
    connectoin_key_delete = "delete"

    def __init__(self, kanban: Kanban, kanban_connection: KanbanConnection):
        self.metadata = kanban.get_metadata()
        self.connection_key = kanban.get_connection_key()
        self.kanban_connection = kanban_connection
        self.controller = ""

    def start_controller(self):
        self._set_controller()
        self.controller.start()

    def _set_controller(self):
        if self.connection_key == self.connection_key_default:
            self.controller = ApplyController(ManifestJson(self.metadata), self.kanban_connection, self.metadata)
        elif self.connection_key == self.connectoin_key_delete:
            self.controller = DeleteController(ManifestJson(self.metadata), self.kanban_connection, self.metadata)


@main_decorator(SERVICE_NAME)
def main(opt: Options):
    initialize_logger(SERVICE_NAME)
    logging.getLogger(KUBERNETES_PACKAGE).setLevel(logging.ERROR)

    conn = opt.get_conn()
    num = opt.get_number()

    try:
        for kanban in conn.get_kanban_itr(SERVICE_NAME, num):
            operator = Operator(kanban, conn)
            operator.start_controller()

    except Exception as e:
        lprint(e)
        output_kanban_with_error(conn)
        lprint(f"{SERVICE_NAME} exit")
        sleep(60)


def output_kanban_with_error(conn: KanbanConnection):
    metadata = {}
    metadata['status'] = FAILED_STATUS_INDEX
    metadata['error'] = "failed to get_kanban_itr"

    conn.output_kanban(
        result=False,
        metadata=metadata,
    )


if __name__ == "__main__":
    main()
