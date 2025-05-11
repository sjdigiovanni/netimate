# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch, MagicMock
from netimate.plugins.device_repositories.postgres import PostgresDeviceRepository
from netimate.models.device import Device


class FakeSettings:
    @property
    def plugin_configs(self):
        return {
            "postgres": {
                "dbname": "netimate",
                "user": "user",
                "password": "pass",
                "host": "localhost",
                "port": "5432",
            }
        }


def test_list_devices_returns_devices():
    fake_rows = [
        ("r1", "10.0.0.1", "admin", "adminpass", "ssh", "ios", "lab1"),
        ("r2", "10.0.0.2", "admin", "adminpass", "ssh", "ios", "lab1"),
    ]

    with patch("netimate.plugins.device_repositories.postgres.psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = fake_rows
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        repo = PostgresDeviceRepository(FakeSettings().plugin_configs.get("postgres"))
        devices = repo.list_devices()

        assert isinstance(devices, list)
        assert all(isinstance(d, Device) for d in devices)
        assert devices[0].name == "r1"
        assert devices[1].host == "10.0.0.2"
