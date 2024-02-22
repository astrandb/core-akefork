"""Helper collection for myuplink."""
import re

from myuplink import Device, DevicePoint, System

from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import Platform


def find_matching_platform(
    device_point: DevicePoint,
    description: SensorEntityDescription | NumberEntityDescription | None = None,
) -> Platform:
    """Find entity platform for a DevicePoint."""
    if (
        len(device_point.enum_values) == 2
        and device_point.enum_values[0]["value"] == "0"
        and device_point.enum_values[1]["value"] == "1"
    ):
        if device_point.writable:
            return Platform.SWITCH
        return Platform.BINARY_SENSOR

    if (
        description
        and description.native_unit_of_measurement == "DM"
        or (device_point.raw["maxValue"] and device_point.raw["minValue"])
    ):
        if device_point.writable:
            return Platform.NUMBER
        return Platform.SENSOR

    return Platform.SENSOR


MAP_NIBEF = {"manufacturer": "Nibe", "series": "F"}
MAP_NIBES = {"manufacturer": "Nibe", "series": "S"}
NAME_MAP = {
    "F1145": MAP_NIBEF,
    "F1155": MAP_NIBEF,
    "F1245": MAP_NIBEF,
    "F1255": MAP_NIBEF,
    "F1345": MAP_NIBEF,
    "F1355": MAP_NIBEF,
    "F370": MAP_NIBEF,
    "F470": MAP_NIBEF,
    "F730": MAP_NIBEF,
    "F750": MAP_NIBEF,
    "SMO20": MAP_NIBEF,
    "SMO40": MAP_NIBEF,
    "VVM225": MAP_NIBEF,
    "VVM310": MAP_NIBEF,
    "VVM320": MAP_NIBEF,
    "VVM325": MAP_NIBEF,
    "VVM500": MAP_NIBEF,
    "S1155": MAP_NIBES,
    "S1255": MAP_NIBES,
    "S1256": MAP_NIBES,
    "S320": MAP_NIBES,
    "S325": MAP_NIBES,
    "S735": MAP_NIBES,
    "S2125": MAP_NIBES,
    "SMOS40": MAP_NIBES,
}


def get_system_names(system: System, device: Device) -> dict[str, str]:
    """Find out system, model and manufacturer from meta-data and override tables."""
    _model: str | None = None
    _name: str | None = None
    _series: str | None = None
    _manufacturer: str | None = None

    _name = system.name
    for model in NAME_MAP:
        if re.search(model, device.raw["product"]["name"]):
            break
    _model = model
    _manufacturer = NAME_MAP[model]["manufacturer"]
    _series = NAME_MAP[model]["series"]
    return {
        "name": _name,
        "model": _model,
        "manufacturer": _manufacturer,
        "series": _series,
    }
