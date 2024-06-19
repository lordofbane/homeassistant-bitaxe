import logging
import subprocess
import json
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    config = entry.data
    name = config["name"]
    ip_address = config["ip_address"]
    stratum_url = config["stratum_url"]
    stratum_port = config["stratum_port"]

    async_add_entities([
        BitaxePowerSensor(name, ip_address),
        BitaxeVoltageSensor(name, ip_address),
        BitaxeCurrentSensor(name, ip_address),
        BitaxeFanSpeedSensor(name, ip_address),
        BitaxeTempSensor(name, ip_address),
        BitaxeHashRateSensor(name, ip_address)
    ], True)

class BitaxeSensor(SensorEntity):
    def __init__(self, name, unit, key, ip_address):
        self._attr_name = f"{name} {key.capitalize()}"
        self._unit = unit
        self._key = key
        self._ip_address = ip_address
        self._state = None

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    async def async_update(self):
        try:
            url = f'http://{self._ip_address}/api/system/info'
            result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
            data = json.loads(result.stdout)

            if self._key in data:
                self._state = data[self._key]
            else:
                _LOGGER.error(f"Key {self._key} not found in Bitaxe response")
        except Exception as e:
            _LOGGER.error("Error retrieving data from Bitaxe: %s", e)

class BitaxePowerSensor(BitaxeSensor):
    def __init__(self, name, ip_address):
        super().__init__(name, "W", "power", ip_address)

class BitaxeVoltageSensor(BitaxeSensor):
    def __init__(self, name, ip_address):
        super().__init__(name, "V", "voltage", ip_address)

class BitaxeCurrentSensor(BitaxeSensor):
    def __init__(self, name, ip_address):
        super().__init__(name, "A", "current", ip_address)

class BitaxeFanSpeedSensor(BitaxeSensor):
    def __init__(self, name, ip_address):
        super().__init__(name, "RPM", "fanSpeed", ip_address)

class BitaxeTempSensor(BitaxeSensor):
    def __init__(self, name, ip_address):
        super().__init__(name, TEMP_CELSIUS, "temp", ip_address)

class BitaxeHashRateSensor(BitaxeSensor):
    def __init__(self, name, ip_address):
        super().__init__(name, "H/s", "hashRate", ip_address)
