from core.registry import EntityRegistry
from core.entities import Municipality, Department, Region, Parcel, Section

def test_registry_contains_entities():
    """Verify that the registry contains all declared entities."""
    # Entities are registered at subclassing time via __init_subclass__
    registered = {cls.API_ENDPOINT: cls for cls in EntityRegistry.list_entities()}
    expected = {
        Municipality.API_ENDPOINT: Municipality,
        Department.API_ENDPOINT: Department,
        Region.API_ENDPOINT: Region,
        Parcel.API_ENDPOINT: Parcel,
        Section.API_ENDPOINT: Section,
    }
    assert registered == expected
