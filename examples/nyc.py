from datetime import datetime
from solarsim import Location, PlantSpecs, SolarPlant, SolarSimulator

# Create a solar plant
location = Location(
    latitude=40.7128,    # New York City
    longitude=-74.0060,
    elevation=10
)

specs = PlantSpecs(
    capacity_kw=1000,    # 1MW plant
    tilt_angle=30,       # 30-degree tilt
    azimuth_angle=180,   # Facing south
    efficiency=0.18      # 18% efficient panels
)

plant = SolarPlant(location, specs)

# Create simulator
simulator = SolarSimulator(plant)

# Generate hourly data for a week
start_date = datetime(2024, 3, 20)
end_date = datetime(2024, 3, 27)

# Get hourly simulation
hourly_data = simulator.generate_timeseries(
    start_date=start_date,
    end_date=end_date,
    freq='1h'
)

# Print first few rows
print(hourly_data.head())

# Get 15-minute simulation
quarter_hourly_data = simulator.generate_timeseries(
    start_date=start_date,
    end_date=end_date,
    freq='15T'
)

# Basic statistics
print("\nHourly Statistics:")
print(hourly_data.describe())

# Plot if matplotlib is available
hourly_data.plot(y='power_kw', title='Solar Power Generation')