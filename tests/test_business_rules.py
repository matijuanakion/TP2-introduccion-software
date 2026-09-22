import unittest
from unittest.mock import MagicMock, patch

from src.services import canchas_services, reservas_services
from src.validators.reservas_validators import validar_nueva_reserva


class BusinessRulesTestCase(unittest.TestCase):
    def reserva(self, inicio='2099-10-20T10:00:00.000000-03:00', fin='2099-10-20T12:00:00.000000-03:00'):
        return {
            'id_socio': 1,
            'id_cancha': 2,
            'fecha_hora_inicio': inicio,
            'fecha_hora_fin': fin,
        }

    def test_reservation_interval_boundaries(self):
        valid, data = validar_nueva_reserva(self.reserva())
        self.assertIsNone(valid)
        self.assertEqual(data['duracion_horas'], 2)

        cases = [
            ('2099-10-20T07:00:00.000000-03:00', '2099-10-20T08:00:00.000000-03:00'),
            ('2099-10-20T22:00:00.000000-03:00', '2099-10-21T00:00:00.000000-03:00'),
            ('2099-10-20T10:00:00.000000-03:00', '2099-10-20T10:30:00.000000-03:00'),
            ('2099-10-20T10:00:00.000000-03:00', '2099-10-20T14:00:00.000000-03:00'),
            ('2099-10-20T10:00:00.000001-03:00', '2099-10-20T12:00:00.000000-03:00'),
            ('2020-10-20T10:00:00.000000-03:00', '2020-10-20T12:00:00.000000-03:00'),
        ]
        for inicio, fin in cases:
            with self.subTest(inicio=inicio, fin=fin):
                errores, _ = validar_nueva_reserva(self.reserva(inicio, fin))
                self.assertTrue(errores)

    @patch('src.services.reservas_services.guardar_reserva_en_transaccion')
    @patch('src.services.reservas_services.obtener_reservas_relacionadas_en_cursor', return_value=[])
    @patch('src.services.reservas_services.obtener_cancha_por_id_en_cursor')
    @patch('src.services.reservas_services.obtener_socio_por_id_en_cursor')
    @patch('src.services.reservas_services.obtener_cursor')
    def test_reservation_checks_entities_overlap_and_historical_price(
        self, cursor_get, socio_get, cancha_get, related_get, save
    ):
        cursor_get.return_value = (MagicMock(), MagicMock())
        socio_get.return_value = {'id': 1, 'activo': True}
        cancha_get.return_value = {'id': 2, 'activa': True, 'precio_hora': 1500}
        save.side_effect = lambda data, connection, cursor: {**data, 'id': 8}

        response, status = reservas_services.procesar_nueva_reserva(self.reserva())
        self.assertEqual(status, 201)
        self.assertEqual(response['reserva']['estado'], 'confirmada')
        self.assertEqual(response['reserva']['precio_hora'], 1500)
        self.assertEqual(response['reserva']['precio_total'], 3000)

        related_get.return_value = [{
            'id_socio': 1,
            'id_cancha': 2,
            'estado': 'confirmada',
            'fecha_hora_inicio': '2099-10-20 11:00:00',
            'fecha_hora_fin': '2099-10-20 13:00:00',
        }]
        _, status = reservas_services.procesar_nueva_reserva(self.reserva())
        self.assertEqual(status, 409)

        socio_get.return_value = {'id': 1, 'activo': False}
        _, status = reservas_services.procesar_nueva_reserva(self.reserva())
        self.assertEqual(status, 409)

    @patch('src.services.canchas_services.obtener_bloqueos_por_fecha', return_value=[])
    @patch('src.services.canchas_services.obtener_reservas_por_fecha')
    @patch('src.services.canchas_services.obtener_canchas_para_disponibilidad')
    def test_available_courts_excludes_inactive_reserved_and_returns_pagination(
        self, courts_get, reservations_get, blocks_get
    ):
        courts_get.return_value = [
            {'id': 1, 'activa': 1},
            {'id': 2, 'activa': 0},
            {'id': 3, 'activa': 1},
        ]
        reservations_get.return_value = [{
            'id_cancha': 1,
            'estado': 'confirmada',
            'fecha_hora_inicio': '2099-10-20 11:00:00',
            'fecha_hora_fin': '2099-10-20 13:00:00',
        }]
        filtros = {
            'fecha': '2099-10-20',
            'hora_inicio': '10:00:00',
            'hora_fin': '12:00:00',
        }
        result, total = canchas_services.filtrar_canchas_disponibles(filtros, 1, 0)
        self.assertEqual(total, 1)
        self.assertEqual(result[0]['id'], 3)

    @patch('src.services.canchas_services.eliminar_cancha_en_transaccion')
    @patch('src.services.canchas_services.contar_reservas_de_cancha_en_cursor', return_value=2)
    @patch('src.services.canchas_services.obtener_cancha_por_id_en_cursor', return_value={'id': 1})
    @patch('src.services.canchas_services.obtener_cursor')
    def test_court_delete_rejects_associated_reservations(self, cursor_get, get, count, delete):
        cursor_get.return_value = (MagicMock(), MagicMock())
        _, status = canchas_services.procesar_eliminacion_cancha(1)
        self.assertEqual(status, 409)
        delete.assert_not_called()

    @patch('src.services.reservas_services.actualizar_estado_reserva')
    @patch('src.services.reservas_services.obtener_reserva_por_id')
    def test_reservation_state_transitions(self, get_reservation, update):
        get_reservation.return_value = {
            'id': 1,
            'estado': 'confirmada',
            'fecha_hora_inicio': '2099-10-20 10:00:00',
            'fecha_hora_fin': '2099-10-20 12:00:00',
        }
        _, status = reservas_services.procesar_estado_reserva(1, 'cancelada')
        self.assertEqual(status, 204)
        update.assert_called_once_with(1, 'cancelada')

        get_reservation.return_value['estado'] = 'cancelada'
        _, status = reservas_services.procesar_estado_reserva(1, 'finalizada')
        self.assertEqual(status, 409)

        get_reservation.return_value['estado'] = 'confirmada'
        _, status = reservas_services.procesar_estado_reserva(1, 'confirmada')
        self.assertEqual(status, 204)


if __name__ == '__main__':
    unittest.main()
