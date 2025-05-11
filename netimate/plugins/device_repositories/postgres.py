# SPDX-License-Identifier: MPL-2.0
import os
from typing import Dict

import psycopg2

from netimate.interfaces.plugin.device_repository import DeviceRepository
from netimate.models.device import Device


class PostgresDeviceRepository(DeviceRepository):
    def __init__(self, plugin_settings: Dict):
        super().__init__(plugin_settings)
        if not self.plugin_settings:
            raise ValueError("Settings file missing postgres config!")
        self._postgres_config: Dict = plugin_settings

    @staticmethod
    def plugin_name() -> str:
        return "postgres"

    def list_devices(self) -> list[Device]:
        conn = psycopg2.connect(
            dbname=self._postgres_config.get("dbname", "netimate"),
            user=self._postgres_config.get("user", "netimate"),
            password=self._postgres_config.get("password")
            or os.getenv("NETIMATE_PG_PASSWORD", "netimate"),
            host=self._postgres_config.get("host", "localhost"),
            port=self._postgres_config.get("port", "5432"),
        )
        try:
            cur = conn.cursor()
            cur.execute(
                self._postgres_config.get(
                    "query",
                    "SELECT name, host, username, password, protocol, platform, site FROM devices",
                )
            )
            rows = cur.fetchall()
            return [
                Device(
                    name=row[0],
                    host=row[1],
                    username=row[2],
                    password=row[3],
                    protocol=row[4],
                    platform=row[5],
                    site=row[6],
                )
                for row in rows
            ]
        finally:
            conn.close()
