import unittest
from unittest.mock import patch

from app import app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def assert_status(self, response, status):
        self.assertEqual(response.status_code, status, response.get_data(as_text=True))

    def test_deportes_success_empty_and_internal_error(self):
        with patch('src.routes.deportes_routes.listar_deportes', return_value=[{'id': 1, 'nombre': 'futbol'}]):
            self.assert_status(self.client.get('/deportes'), 200)
        with patch('src.routes.deportes_routes.listar_deportes', return_value=[]):
            self.assert_status(self.client.get('/deportes'), 204)
        with patch('src.routes.deportes_routes.listar_deportes', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/deportes'), 500)

    def test_canchas_list_filters_pagination_and_errors(self):
        with patch('src.routes.canchas_routes.filtrar_canchas', return_value=([{'id': 1}], 1)):
            response = self.client.get('/canchas?nombre=cancha&techada=false&_limit=1&_offset=0')
            self.assert_status(response, 200)
        with patch('src.routes.canchas_routes.filtrar_canchas', return_value=([], 0)):
            self.assert_status(self.client.get('/canchas'), 204)
        self.assert_status(self.client.get('/canchas?techada=yes'), 400)
        self.assert_status(self.client.get('/canchas?desconocido=1'), 400)
        self.assert_status(self.client.get('/canchas?_limit=0'), 400)
        with patch('src.routes.canchas_routes.filtrar_canchas', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/canchas'), 500)

    def test_canchas_create_get_patch_delete_all_statuses(self):
        cancha = {'id': 1, 'nombre': 'Central'}
        with patch('src.routes.canchas_routes.procesar_nueva_cancha', return_value=({'cancha': cancha}, 201)):
            self.assert_status(self.client.post('/canchas', json={'nombre': 'Central'}), 201)
        with patch('src.routes.canchas_routes.procesar_nueva_cancha', return_value=({'errors': []}, 400)):
            self.assert_status(self.client.post('/canchas', json={}), 400)
        self.assert_status(self.client.post('/canchas', json=[]), 400)

        with patch('src.routes.canchas_routes.consultar_cancha', return_value=(cancha, 200)):
            self.assert_status(self.client.get('/canchas/1'), 200)
        with patch('src.routes.canchas_routes.consultar_cancha', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.get('/canchas/999'), 404)
        self.assert_status(self.client.get('/canchas/abc'), 400)

        with patch('src.routes.canchas_routes.procesar_actualizacion_cancha', return_value=('', 204)):
            self.assert_status(self.client.patch('/canchas/1', json={'nombre': 'Nueva'}), 204)
        with patch('src.routes.canchas_routes.procesar_actualizacion_cancha', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.patch('/canchas/999', json={'nombre': 'Nueva'}), 404)
        self.assert_status(self.client.patch('/canchas/1', json={}), 400)

        with patch('src.routes.canchas_routes.procesar_eliminacion_cancha', return_value=('', 204)):
            self.assert_status(self.client.delete('/canchas/1'), 204)
        with patch('src.routes.canchas_routes.procesar_eliminacion_cancha', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.delete('/canchas/999'), 404)
        with patch('src.routes.canchas_routes.procesar_eliminacion_cancha', return_value=({'errors': []}, 409)):
            self.assert_status(self.client.delete('/canchas/1'), 409)

    def test_available_canchas_success_and_validation_edges(self):
        filtros = {'fecha': '2099-10-20', 'hora_inicio': '10:00:00', 'hora_fin': '12:00:00'}
        with patch('src.routes.canchas_routes.filtrar_canchas_disponibles', return_value=([{'id': 1}], 1)):
            self.assert_status(self.client.get('/canchas/disponibles', query_string=filtros), 200)
        self.assert_status(self.client.get('/canchas/disponibles?fecha=2099-10-20&hora_inicio=10:30:00&hora_fin=12:00:00'), 400)
        self.assert_status(self.client.get('/canchas/disponibles?fecha=2099-10-20&hora_inicio=10:00:00'), 400)
        with patch('src.routes.canchas_routes.filtrar_canchas_disponibles', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/canchas/disponibles', query_string=filtros), 500)

    def test_socios_list_create_get_patch(self):
        with patch('src.routes.socios_routes.filtrar_socios', return_value=([{'id': 1}], 1)):
            self.assert_status(self.client.get('/socios?activo=true'), 200)
        with patch('src.routes.socios_routes.filtrar_socios', return_value=([], 0)):
            self.assert_status(self.client.get('/socios'), 204)
        self.assert_status(self.client.get('/socios?activo=maybe'), 400)
        self.assert_status(self.client.get('/socios?x=1'), 400)

        with patch('src.routes.socios_routes.procesar_nuevo_socio', return_value=({'id': 1}, 201)):
            self.assert_status(self.client.post('/socios', json={'nombre': 'Ana', 'email': 'ana@example.com'}), 201)
        with patch('src.routes.socios_routes.procesar_nuevo_socio', return_value=({'errors': []}, 409)):
            self.assert_status(self.client.post('/socios', json={'nombre': 'Ana', 'email': 'ana@example.com'}), 409)
        self.assert_status(self.client.post('/socios', json={}), 400)

        with patch('src.routes.socios_routes.consultar_socio', return_value=({'id': 1}, 200)):
            self.assert_status(self.client.get('/socios/1'), 200)
        with patch('src.routes.socios_routes.consultar_socio', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.get('/socios/999'), 404)
        self.assert_status(self.client.get('/socios/no'), 400)
        with patch('src.routes.socios_routes.procesar_actualizacion_socio', return_value=('', 204)):
            self.assert_status(self.client.patch('/socios/1', json={'nombre': 'Ana'}), 204)
        with patch('src.routes.socios_routes.procesar_actualizacion_socio', return_value=({'errors': []}, 409)):
            self.assert_status(self.client.patch('/socios/1', json={'email': 'dup@example.com'}), 409)
        self.assert_status(self.client.patch('/socios/1', json={}), 400)

    def test_reservas_list_create_get_and_state(self):
        with patch('src.routes.reservas_routes.filtrar_reservas', return_value=([{'id': 1}], 1)):
            self.assert_status(self.client.get('/reservas?estado=confirmada'), 200)
        with patch('src.routes.reservas_routes.filtrar_reservas', return_value=([], 0)):
            self.assert_status(self.client.get('/reservas'), 204)
        self.assert_status(self.client.get('/reservas?estado=otro'), 400)
        self.assert_status(self.client.get('/reservas?fecha_desde=2026-12-31&fecha_hasta=2026-01-01'), 400)

        payload = {
            'id_socio': 1,
            'id_cancha': 1,
            'fecha_hora_inicio': '2099-10-20T10:00:00.000000-03:00',
            'fecha_hora_fin': '2099-10-20T12:00:00.000000-03:00',
        }
        with patch('src.routes.reservas_routes.procesar_nueva_reserva', return_value=({'id': 1}, 201)):
            self.assert_status(self.client.post('/reservas', json=payload), 201)
        with patch('src.routes.reservas_routes.procesar_nueva_reserva', return_value=({'errors': []}, 409)):
            self.assert_status(self.client.post('/reservas', json=payload), 409)
        self.assert_status(self.client.post('/reservas', json={**payload, 'extra': 1}), 400)

        with patch('src.routes.reservas_routes.consultar_reserva', return_value=({'id': 1}, 200)):
            self.assert_status(self.client.get('/reservas/1'), 200)
        with patch('src.routes.reservas_routes.consultar_reserva', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.get('/reservas/999'), 404)
        self.assert_status(self.client.get('/reservas/no'), 400)

        with patch('src.routes.reservas_routes.procesar_estado_reserva', return_value=('', 204)):
            self.assert_status(self.client.put('/reservas/1/estado', json={'estado': 'cancelada'}), 204)
        with patch('src.routes.reservas_routes.procesar_estado_reserva', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.put('/reservas/999/estado', json={'estado': 'cancelada'}), 404)
        self.assert_status(self.client.put('/reservas/1/estado', json={'estado': 'invalido'}), 400)
        self.assert_status(self.client.put('/reservas/1/estado', json={'estado': 'cancelada', 'x': 1}), 400)

    def test_expected_not_found_conflict_and_internal_error_responses(self):
        with patch('src.routes.canchas_routes.procesar_nueva_cancha', return_value=({}, 404)):
            self.assert_status(self.client.post('/canchas', json={'nombre': 'x'}), 404)
        with patch('src.routes.canchas_routes.procesar_nueva_cancha', side_effect=RuntimeError()):
            self.assert_status(self.client.post('/canchas', json={'nombre': 'x'}), 500)
        with patch('src.routes.canchas_routes.consultar_cancha', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/canchas/1'), 500)
        with patch('src.routes.canchas_routes.procesar_actualizacion_cancha', side_effect=RuntimeError()):
            self.assert_status(self.client.patch('/canchas/1', json={'nombre': 'x'}), 500)
        with patch('src.routes.canchas_routes.procesar_eliminacion_cancha', side_effect=RuntimeError()):
            self.assert_status(self.client.delete('/canchas/1'), 500)

        with patch('src.routes.socios_routes.filtrar_socios', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/socios'), 500)
        with patch('src.routes.socios_routes.procesar_nuevo_socio', side_effect=RuntimeError()):
            self.assert_status(self.client.post('/socios', json={'nombre': 'x', 'email': 'x@y.com'}), 500)
        with patch('src.routes.socios_routes.consultar_socio', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/socios/1'), 500)
        with patch('src.routes.socios_routes.procesar_actualizacion_socio', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.patch('/socios/1', json={'nombre': 'x'}), 404)
        with patch('src.routes.socios_routes.procesar_actualizacion_socio', side_effect=RuntimeError()):
            self.assert_status(self.client.patch('/socios/1', json={'nombre': 'x'}), 500)

        with patch('src.routes.reservas_routes.filtrar_reservas', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/reservas'), 500)
        with patch('src.routes.reservas_routes.procesar_nueva_reserva', return_value=({'errors': []}, 404)):
            self.assert_status(self.client.post('/reservas', json={'id_socio': 1}), 404)
        with patch('src.routes.reservas_routes.procesar_nueva_reserva', side_effect=RuntimeError()):
            self.assert_status(self.client.post('/reservas', json={'id_socio': 1}), 500)
        with patch('src.routes.reservas_routes.consultar_reserva', side_effect=RuntimeError()):
            self.assert_status(self.client.get('/reservas/1'), 500)
        with patch('src.routes.reservas_routes.procesar_estado_reserva', return_value=({'errors': []}, 409)):
            self.assert_status(self.client.put('/reservas/1/estado', json={'estado': 'cancelada'}), 409)
        with patch('src.routes.reservas_routes.procesar_estado_reserva', side_effect=RuntimeError()):
            self.assert_status(self.client.put('/reservas/1/estado', json={'estado': 'cancelada'}), 500)


if __name__ == '__main__':
    unittest.main()
