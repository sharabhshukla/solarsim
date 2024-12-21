import pytest
from datetime import datetime
import pandas as pd
from solarsim import Location, PlantSpecs, SolarPlant, SolarSimulator

@pytest.fixture
def sample_simulator():
    location = Location(latitude=40.7128, longitude=-74.0060)
    specs = PlantSpecs(capacity_kw=1000, tilt_angle=30, azimuth_angle=180)
    plant = SolarPlant(location, specs)
    return SolarSimulator(plant)


def test_simulator_creation(sample_simulator):
    assert isinstance(sample_simulator, SolarSimulator)
    assert isinstance(sample_simulator.plant, SolarPlant)

def test_generate_timeseries_hourly(sample_simulator):
    start_date = datetime(2024, 3, 20, 0, 0)
    end_date = datetime(2024, 3, 20, 23, 0)
    
    df = sample_simulator.generate_timeseries(
        start_date=start_date,
        end_date=end_date,
        freq='1H'
    )
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 24
    assert 'power_kw' in df.columns
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.freq == '1h'
    assert all(0 <= power <= 1000 for power in df['power_kw'])

def test_generate_timeseries_15min(sample_simulator):
    start_date = datetime(2024, 3, 20, 0, 0)
    end_date = datetime(2024, 3, 20, 1, 0)
    
    df = sample_simulator.generate_timeseries(
        start_date=start_date,
        end_date=end_date,
        freq='15min'
    )
    
    assert len(df) == 5  # 0:00, 0:15, 0:30, 0:45, 1:00
    assert df.index.freq == '15min'

def test_generate_timeseries_daily(sample_simulator):
    start_date = datetime(2024, 3, 20)
    end_date = datetime(2024, 3, 27)
    
    df = sample_simulator.generate_timeseries(
        start_date=start_date,
        end_date=end_date,
        freq='1D'
    )
    
    assert len(df) == 8  # 8 days inclusive
    assert df.index.freq == '1D'

def test_invalid_frequency(sample_simulator):
    start_date = datetime(2024, 3, 20)
    end_date = datetime(2024, 3, 21)
    
    with pytest.raises(ValueError):
        sample_simulator.generate_timeseries(
            start_date=start_date,
            end_date=end_date,
            freq='invalid'
        )

def test_end_before_start(sample_simulator):
    start_date = datetime(2024, 3, 20)
    end_date = datetime(2024, 3, 19)  # End before start
    
    with pytest.raises(ValueError):
        sample_simulator.generate_timeseries(
            start_date=start_date,
            end_date=end_date,
            freq='1H'
        )