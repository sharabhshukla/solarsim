import pytest
from datetime import datetime
from solarsim import Location, PlantSpecs, SolarPlant

@pytest.fixture
def sample_location():
    return Location(
        latitude=40.7128,    # New York City
        longitude=-74.0060,
        elevation=10
    )

@pytest.fixture
def sample_specs():
    return PlantSpecs(
        capacity_kw=1000,    # 1MW plant
        tilt_angle=30,       # 30-degree tilt
        azimuth_angle=180,   # Facing south
        efficiency=0.18      # 18% efficient panels
    )

@pytest.fixture
def solar_plant(sample_location, sample_specs):
    return SolarPlant(sample_location, sample_specs)

def test_location_creation():
    loc = Location(latitude=40.7128, longitude=-74.0060)
    assert loc.latitude == 40.7128
    assert loc.longitude == -74.0060
    assert loc.elevation == 0  # default value

def test_location_with_elevation():
    loc = Location(latitude=40.7128, longitude=-74.0060, elevation=100)
    assert loc.elevation == 100

def test_plant_specs_creation():
    specs = PlantSpecs(capacity_kw=1000, tilt_angle=30, azimuth_angle=180)
    assert specs.capacity_kw == 1000
    assert specs.tilt_angle == 30
    assert specs.azimuth_angle == 180
    assert specs.efficiency == 0.15  # default value
    assert specs.temperature_coefficient == -0.0035  # default value

def test_plant_specs_with_custom_values():
    specs = PlantSpecs(
        capacity_kw=500,
        tilt_angle=25,
        azimuth_angle=175,
        efficiency=0.20,
        temperature_coefficient=-0.004
    )
    assert specs.efficiency == 0.20
    assert specs.temperature_coefficient == -0.004

def test_solar_plant_creation(sample_location, sample_specs):
    plant = SolarPlant(sample_location, sample_specs)
    assert plant.location == sample_location
    assert plant.specs == sample_specs

def test_solar_position_calculation(solar_plant):
    # Test for noon on summer solstice 2024
    dt = datetime(2024, 6, 21, 12, 0)
    altitude, azimuth = solar_plant._calculate_solar_position(dt)
    
    # Values should be reasonable for NYC at noon on summer solstice
    assert 65 < altitude < 75  # Sun is high in the sky
    assert 150 < azimuth < 210  # Sun is roughly south

def test_incident_angle_calculation(solar_plant):
    # Test with sun directly overhead
    incident_angle = solar_plant._calculate_incident_angle(90, 180)
    assert 20 < incident_angle < 40  # Should be close to tilt angle (30°)

def test_simulation_basic(solar_plant):
    start_time = datetime(2024, 3, 20, 0, 0)
    results = solar_plant.simulate(
        start_time=start_time,
        duration_hours=24,
        interval_minutes=60
    )
    
    assert len(results) == 25  # 24 hours + 1 for inclusive end
    assert all(isinstance(dt, datetime) for dt, _ in results)
    assert all(isinstance(power, float) for _, power in results)
    assert all(0 <= power <= solar_plant.specs.capacity_kw for _, power in results)

def test_simulation_night_hours(solar_plant):
    # Test midnight simulation (should be zero power)
    start_time = datetime(2024, 3, 20, 0, 0)
    results = solar_plant.simulate(
        start_time=start_time,
        duration_hours=1,
        interval_minutes=60
    )
    assert results[0][1] == 0.0  # No power at midnight
 