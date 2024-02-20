"""Binary sensors for myUplink."""

from dataclasses import dataclass
from typing import cast

from myuplink import DevicePoint, System

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MyUplinkDataCoordinator
from .const import DOMAIN
from .entity import MyUplinkEntity, MyUplinkSystemEntity
from .helpers import find_matching_platform

CATEGORY_BASED_DESCRIPTIONS: dict[str, dict[str, BinarySensorEntityDescription]] = {
    "NIBEF": {
        "43161": BinarySensorEntityDescription(
            key="elect_add",
            icon="mdi:electric-switch",
        ),
    },
}


@dataclass(frozen=True)
class MyUplinkSystemBinarySensorDescription(BinarySensorEntityDescription):
    """Class describing Miele binary sensor entities."""

    attribute: str | None = None


SYSTEM_DESCRIPTIONS: dict[str, MyUplinkSystemBinarySensorDescription] = {
    "alarm": MyUplinkSystemBinarySensorDescription(
        key="alarm",
        name="Alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        attribute="hasAlarm",
    ),
}


def get_description(device_point: DevicePoint) -> BinarySensorEntityDescription | None:
    """Get description for a device point.

    Priorities:
    1. Category specific prefix e.g "NIBEF"
    2. Default to None
    """
    prefix, _, _ = device_point.category.partition(" ")
    description = CATEGORY_BASED_DESCRIPTIONS.get(prefix, {}).get(
        device_point.parameter_id
    )

    return description


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up myUplink binary_sensor."""
    entities: list[BinarySensorEntity] = []
    coordinator: MyUplinkDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Setup device point sensors
    for device_id, point_data in coordinator.data.points.items():
        for point_id, device_point in point_data.items():
            if find_matching_platform(device_point) == Platform.BINARY_SENSOR:
                description = get_description(device_point)

                entities.append(
                    MyUplinkDevicePointBinarySensor(
                        coordinator=coordinator,
                        device_id=device_id,
                        device_point=device_point,
                        entity_description=description,
                        unique_id_suffix=point_id,
                    )
                )
    for system in coordinator.data.systems:
        for description in SYSTEM_DESCRIPTIONS.values():
            entities.append(
                MyUplinkSystemBinarySensor(
                    coordinator=coordinator,
                    system=system,
                    entity_description=description,
                    unique_id_suffix=description.key,
                )
            )
    async_add_entities(entities)


class MyUplinkDevicePointBinarySensor(MyUplinkEntity, BinarySensorEntity):
    """Representation of a myUplink device point binary sensor."""

    def __init__(
        self,
        coordinator: MyUplinkDataCoordinator,
        device_id: str,
        device_point: DevicePoint,
        entity_description: BinarySensorEntityDescription | None,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the binary_sensor."""
        super().__init__(
            coordinator=coordinator,
            device_id=device_id,
            unique_id_suffix=unique_id_suffix,
        )

        # Internal properties
        self.point_id = device_point.parameter_id
        self._attr_name = device_point.parameter_name

        if entity_description is not None:
            self.entity_description = entity_description

    @property
    def is_on(self) -> bool:
        """Binary sensor state value."""
        device_point = self.coordinator.data.points[self.device_id][self.point_id]
        return cast(int, device_point.value) != 0


class MyUplinkSystemBinarySensor(MyUplinkSystemEntity, BinarySensorEntity):
    """Representation of a myUplink System binary sensor."""

    def __init__(
        self,
        coordinator: MyUplinkDataCoordinator,
        system: System,
        entity_description: MyUplinkSystemBinarySensorDescription,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the binary_sensor."""
        super().__init__(
            coordinator=coordinator,
            system=system,
            unique_id_suffix=unique_id_suffix,
        )

        self.entity_description: MyUplinkSystemBinarySensorDescription = (
            entity_description
        )

    @property
    def is_on(self) -> bool:
        """Binary sensor state value."""
        return not getattr(System, cast(str, self.entity_description.attribute))
