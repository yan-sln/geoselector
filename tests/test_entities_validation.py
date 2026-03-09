import pytest
from core.entities import Municipality, Department, Region, Parcel, Section

# ---------- Valid cases (should not raise) ----------

def test_municipality_valid():
    data = {"code": "75056", "name": "Paris", "department_code": "75"}
    m = Municipality.from_dict(data)
    assert isinstance(m, Municipality)
    assert m.code == "75056"
    assert m.department_code == "75"

def test_department_valid():
    data = {"code": "75", "name": "Paris", "region_code": "11"}
    d = Department.from_dict(data)
    assert isinstance(d, Department)
    assert d.region_code == "11"

def test_parcel_valid():
    data = {"code": "12345", "name": "Parcel-1", "commune_code": "75056", "section": "A"}
    p = Parcel.from_dict(data)
    assert isinstance(p, Parcel)
    assert p.commune_code == "75056"
    assert p.section == "A"

def test_section_valid():
    data = {"code": "A1", "name": "Section A1", "commune_code": "75056"}
    s = Section.from_dict(data)
    assert isinstance(s, Section)
    assert s.commune_code == "75056"

# ---------- Invalid cases (should raise ValueError) ----------

def test_municipality_invalid_department_code():
    data = {"code": "75056", "name": "Paris", "department_code": 75}
    with pytest.raises(ValueError):
        Municipality.from_dict(data)

def test_department_invalid_region_code():
    data = {"code": "75", "name": "Paris", "region_code": 11}
    with pytest.raises(ValueError):
        Department.from_dict(data)

def test_parcel_missing_commune_code():
    data = {"code": "12345", "name": "Parcel-1"}
    with pytest.raises(ValueError):
        Parcel.from_dict(data)

def test_parcel_invalid_section():
    data = {"code": "12345", "name": "Parcel-1", "commune_code": "75056", "section": 1}
    with pytest.raises(ValueError):
        Parcel.from_dict(data)

def test_section_missing_commune_code():
    data = {"code": "A1", "name": "Section A1"}
    with pytest.raises(ValueError):
        Section.from_dict(data)
