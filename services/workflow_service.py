"""Named workflows belonging to the configured FlightHub project."""
from pathlib import Path
from uuid import UUID
import json

from services.storage_service import atomic_json, locked

WORKFLOWS_FILE = Path(__file__).resolve().parent.parent / 'workflows.json'


def cargar_workflows():
    try:
        with open(WORKFLOWS_FILE, encoding='utf-8') as source:
            data = json.load(source)
        if not isinstance(data, dict):
            raise ValueError('El catálogo de workflows no es válido.')
        return data
    except FileNotFoundError:
        return {}


@locked
def agregar_workflow(name, workflow_uuid):
    name = name.strip()
    if not name or len(name) > 100:
        return False, 'Escribe un nombre de hasta 100 caracteres.'
    try:
        workflow_uuid = str(UUID(workflow_uuid.strip()))
    except (ValueError, AttributeError):
        return False, 'El Workflow UUID no es válido.'
    workflows = cargar_workflows()
    if workflow_uuid in workflows:
        return False, 'Este Workflow UUID ya está registrado.'
    workflows[workflow_uuid] = {'name': name}
    atomic_json(WORKFLOWS_FILE, workflows)
    return True, 'Workflow agregado. Ya puedes asignarlo a una cámara.'


@locked
def eliminar_workflow(workflow_uuid):
    from services.camera_service import cargar_camaras
    workflows = cargar_workflows()
    if workflow_uuid not in workflows:
        return False, 'El workflow no existe.'
    if any(c.get('workflow_uuid') == workflow_uuid for c in cargar_camaras().values()):
        return False, 'Este workflow está asignado a una cámara. Cambia su asignación antes de eliminarlo.'
    del workflows[workflow_uuid]
    atomic_json(WORKFLOWS_FILE, workflows)
    return True, 'Workflow eliminado del catálogo.'
