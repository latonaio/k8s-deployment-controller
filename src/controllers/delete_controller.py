# import os

from aion.kanban import KanbanConnection
from controllers.controller import Controller
from manifestJson import ManifestJson


class DeleteController(Controller):
    def __init__(self, manifest_json: ManifestJson, conn: KanbanConnection, metadata):
        super().__init__(manifest_json, conn, metadata)
