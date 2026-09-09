import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
import requests

from app import app
from config import Config
from services import camera_service as cameras, workflow_service as workflows
from services import event_service as events, settings_service as settings, storage_service as storage

A = '11111111-1111-4111-8111-111111111111'
B = '22222222-2222-4222-8222-222222222222'
DEFAULT = '33333333-3333-4333-8333-333333333333'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for module, key, name in [
            (cameras, 'CAMERAS_FILE', 'cameras.json'),
            (workflows, 'WORKFLOWS_FILE', 'workflows.json'),
            (events, 'EVENTS_FILE', 'events.json'),
            (events, 'LOGS_DIR', 'logs'),
            (settings, 'ENV_FILE', '.env'),
            (storage, 'LOCK_FILE', '.lock'),
        ]:
            self.enterContext(patch.object(module, key, self.root / name))
        # Suppress event logging in tests; never contact a real FH2 instance.
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.post = self.enterContext(patch('services.fh2_service.requests.post', return_value=Mock(status_code=200, text='OK')))
        self.enterContext(patch('routes.settings_routes.comprobar_gateway', return_value=True))
        self.enterContext(patch.object(Config, 'FH2_WORKFLOW_UUID', 'stale-process-value'))
        self.enterContext(patch('services.settings_service.aplicar_configuracion_runtime'))
        settings.guardar_configuracion(dict(FH2_URL='http://fh2.invalid/api', FH2_USER_TOKEN='secret-test-token',
            FH2_PROJECT_UUID='project', FH2_WORKFLOW_UUID=DEFAULT, FH2_CREATOR_ID='creator', DEFAULT_LEVEL='5'))
        self.client = app.test_client()

    def test_distinct_cameras_send_distinct_workflows(self):
        for cam, uuid in [('cam1', A), ('cam2', B)]:
            self.assertTrue(workflows.agregar_workflow(cam, uuid)[0])
            self.assertTrue(cameras.agregar_camara(cam, cam, '19', '-99', uuid)[0])
            response = self.client.post('/hik-alert', json={'camera_id': cam})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.post.call_args.kwargs['json']['workflow_uuid'], uuid)
            self.assertEqual(self.post.call_args.kwargs['headers']['x-project-uuid'], 'project')
            self.assertEqual(response.json['workflow_uuid'], uuid)
        self.assertEqual([e['workflow_uuid'] for e in events.cargar_eventos()], [A, B])

    def test_legacy_camera_uses_fresh_persisted_default(self):
        storage.atomic_json(cameras.CAMERAS_FILE, {'old': {'name': 'Old', 'latitude': 19, 'longitude': -99}})
        self.client.post('/hik-alert', json={'camera_id': 'old'})
        self.assertEqual(self.post.call_args.kwargs['json']['workflow_uuid'], DEFAULT)
        settings.guardar_configuracion({'FH2_WORKFLOW_UUID': B})
        self.client.post('/hik-alert', json={'camera_id': 'old'})
        self.assertEqual(self.post.call_args.kwargs['json']['workflow_uuid'], B)

    def test_edit_preserves_or_explicitly_resets_assignment(self):
        workflows.agregar_workflow('A', A)
        cameras.agregar_camara('cam', 'Camera', 19, -99, A)
        cameras.editar_camara('cam', 'Renamed', 20, -98)
        self.assertEqual(cameras.obtener_camara('cam')['workflow_uuid'], A)
        cameras.editar_camara('cam', 'Renamed', 20, -98, '')
        self.client.post('/hik-alert', json={'camera_id': 'cam'})
        self.assertEqual(self.post.call_args.kwargs['json']['workflow_uuid'], DEFAULT)

    def test_assigned_workflow_cannot_be_deleted(self):
        workflows.agregar_workflow('A', A)
        cameras.agregar_camara('cam', 'Camera', 19, -99, A)
        self.assertFalse(workflows.eliminar_workflow(A)[0])
        cameras.editar_camara('cam', 'Camera', 19, -99, '')
        self.assertTrue(workflows.eliminar_workflow(A)[0])

    def test_invalid_duplicate_and_unknown_workflows(self):
        self.assertFalse(workflows.agregar_workflow('Invalid', 'invalid')[0])
        self.assertFalse(workflows.agregar_workflow('', A)[0])
        self.assertTrue(workflows.agregar_workflow('A', A)[0])
        self.assertFalse(workflows.agregar_workflow('Duplicate', A)[0])
        self.assertFalse(cameras.agregar_camara('cam', 'Camera', 19, -99, B)[0])
        self.assertFalse(workflows.eliminar_workflow(B)[0])

    def test_missing_assignment_does_not_fall_back_to_another_workflow(self):
        storage.atomic_json(cameras.CAMERAS_FILE, {'cam': {'name': 'Cam', 'latitude': 19, 'longitude': -99, 'workflow_uuid': A}})
        self.assertEqual(self.client.post('/hik-alert', json={'camera_id': 'cam'}).status_code, 409)
        self.post.assert_not_called()

    def test_unconfigured_default_does_not_send(self):
        settings.guardar_configuracion({'FH2_WORKFLOW_UUID': ''})
        cameras.agregar_camara('cam', 'Camera', 19, -99)
        self.assertEqual(self.client.post('/hik-alert', json={'camera_id': 'cam'}).status_code, 409)
        self.post.assert_not_called()

    def test_network_failure_keeps_workflow_in_history(self):
        cameras.agregar_camara('cam', 'Camera', 19, -99)
        self.post.side_effect = requests.Timeout()
        self.assertEqual(self.client.post('/hik-alert', json={'camera_id': 'cam'}).status_code, 502)
        self.assertEqual(events.cargar_eventos()[-1]['workflow_uuid'], DEFAULT)

    def test_http_error_records_selected_workflow(self):
        cameras.agregar_camara('cam', 'Camera', 19, -99)
        self.post.return_value = Mock(status_code=400, text='Workflow error')
        response = self.client.post('/hik-alert', json={'camera_id': 'cam'})
        self.assertEqual(response.json['fh2_status'], 400)
        self.assertEqual(events.cargar_eventos()[-1]['workflow_uuid'], DEFAULT)

    def test_form_routes_and_html_escape_workflow_names(self):
        result = self.client.post('/settings/workflows/add', data={'name': '<script>alert(1)</script>', 'workflow_uuid': A})
        self.assertEqual(result.status_code, 302)
        self.client.post('/cameras/add', data={'camera_id': 'cam', 'name': 'Cam', 'latitude': '19', 'longitude': '-99', 'workflow_uuid': A})
        self.assertEqual(cameras.obtener_camara('cam')['workflow_uuid'], A)
        html = self.client.get('/cameras').get_data(as_text=True)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn(f'value="{A}" selected', html)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertEqual(self.client.get('/settings').status_code, 200)
        self.client.post('/settings/workflows/delete/' + A)
        self.assertIn(A, workflows.cargar_workflows())

    def test_old_event_history_remains_readable(self):
        storage.atomic_json(events.EVENTS_FILE, [{'camera_id': 'cam', 'fh2_status': 200}])
        self.assertEqual(events.cargar_eventos()[0]['fh2_status'], 200)

    def test_invalid_alert_payloads_never_send(self):
        for payload in [[], ['cam'], {'camera_id': []}, {}, {'camera_id': 'missing'}]:
            self.assertIn(self.client.post('/hik-alert', json=payload).status_code, [400, 404])
        self.post.assert_not_called()


if __name__ == '__main__':
    unittest.main()
