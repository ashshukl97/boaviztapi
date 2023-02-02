import os
from typing import Optional

import pandas as pd

from boaviztapi.dto.component import ComponentDTO
from boaviztapi.dto.usage.usage import smart_mapper_usage, Usage
from boaviztapi.model.boattribute import Status
from boaviztapi.model.component import ComponentSSD, ComponentHDD
from boaviztapi.utils.fuzzymatch import fuzzymatch_attr_from_pdf

_ssd_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../data/components/ssd_manufacture.csv'))


class Disk(ComponentDTO):
    type: Optional[str] = None
    capacity: Optional[int] = None
    density: Optional[float] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None


def smart_mapper_ssd(disk_dto: Disk) -> ComponentSSD:
    disk_component = ComponentSSD()

    disk_component.usage = smart_mapper_usage(disk_dto.usage or Usage())

    if disk_dto.units is not None:
        disk_component.units.value = disk_dto.units
        disk_component.units.status = Status.INPUT

    corrected_manufacturer = None

    if disk_dto.type.lower() == 'ssd':
        if disk_dto.capacity is not None:
            disk_component.capacity.value = disk_dto.capacity
            disk_component.capacity.status = Status.INPUT

        if disk_dto.density is not None:
            disk_component.density.value = disk_dto.density
            disk_component.density.status = Status.INPUT
        else:
            sub = _ssd_df
            if disk_dto.manufacturer is not None:
                corrected_manufacturer = fuzzymatch_attr_from_pdf(disk_dto.manufacturer, "manufacturer", sub)
                sub = sub[sub['manufacturer'] == corrected_manufacturer]

            if len(sub) == 0 or len(sub) == len(_ssd_df):
                pass
            elif len(sub) == 1:
                disk_component.density.value = float(sub['density'])
                disk_component.density.status = Status.COMPLETED
                disk_component.density.min = float(sub['density'])
                disk_component.density.max = float(sub['density'])
                disk_component.density.source = str(sub['manufacturer'].iloc[0])
            else:
                disk_component.density.value = float(sub['density'].mean())
                disk_component.density.min = float(sub['density'].min())
                disk_component.density.max = float(sub['density'].max())
                disk_component.density.status = Status.COMPLETED
                disk_component.density.source = "Average of " + str(len(sub)) + " rows"

        if disk_dto.manufacturer is not None and corrected_manufacturer is not None:
            if corrected_manufacturer != disk_dto.manufacturer:
                disk_component.manufacturer.value = corrected_manufacturer
                disk_component.manufacturer.status = Status.CHANGED
            else:
                disk_component.manufacturer.value = disk_dto.manufacturer
                disk_component.manufacturer.status = Status.INPUT

    return disk_component


def mapper_hdd(disk_dto: Disk) -> ComponentHDD:
    disk_component = ComponentHDD()

    disk_component.usage = smart_mapper_usage(disk_dto.usage or Usage())

    if disk_dto.units is not None:
        disk_component.units.value = disk_dto.units
        disk_component.units.status = Status.INPUT

    disk_component.capacity.value = disk_dto.capacity

    return disk_component
