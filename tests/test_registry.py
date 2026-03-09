import pytest
from core.registry import EntityRegistry
from core.entities import Municipality, Department, Region, Parcel, Section

def test_registry_contains_entities():
    """Vérifie que le registre contient toutes les entités déclarées."""
    # Les entités sont enregistrées au moment du subclassing grâce à __init_subclass__
    registered = {cls.API_ENDPOINT: cls for cls in EntityRegistry.list_entities()}
    expected = {
        Municipality.API_ENDPOINT: Municipality,
        Department.API_ENDPOINT: Department,
        Region.API_ENDPOINT: Region,
        Parcel.API_ENDPOINT: Parcel,
        Section.API_ENDPOINT: Section,
    }
    assert registered == expected
