from dataclasses import dataclass
from datetime import datetime, timedelta
import math
from typing import List, Tuple

@dataclass
class Location:
    """     Geographic location.     """
    latitude: float  # Latitude in degrees
    longitude: float  # Longitude in degrees
    elevation: float = 0  # Elevation in meters

@dataclass
class PlantSpecs:
    "" "Specifications for a solar power plant." ""
    capacity_kw: float  # Nameplate capacity in kilowatts
    tilt_angle: float  # Panel tilt angle in degrees
    azimuth_angle: float  # Panel azimuth angle in degrees (0 = North, 90 = East, 180 = South, 270 = West)
    efficiency: float = 0.15  # Panel efficiency (typical range: 0.15-0.20)
    temperature_coefficient: float = -0.0035  # Power temperature coefficient (%/°C)

class SolarPlant:
    """ Solar plant simulator. """
    def __init__(self, location: Location, specs: PlantSpecs):
        self.location = location
        self.specs = specs

    def _calculate_solar_position(self, dt: datetime) -> Tuple[float, float]:
        """Calculate solar altitude and azimuth angles."""
        day_of_year = dt.timetuple().tm_yday
        
        # Calculate declination angle
        declination = 23.45 * math.sin(math.radians(360/365 * (day_of_year - 81)))
        
        # Calculate hour angle
        solar_hour = dt.hour + dt.minute/60 + dt.second/3600
        hour_angle = (solar_hour - 12) * 15
        
        # Calculate solar altitude
        lat_rad = math.radians(self.location.latitude)
        decl_rad = math.radians(declination)
        hour_rad = math.radians(hour_angle)
        
        sin_altitude = (math.sin(lat_rad) * math.sin(decl_rad) +
                       math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_rad))
        altitude = math.degrees(math.asin(sin_altitude))
        
        # Calculate solar azimuth
        cos_azimuth = ((math.sin(decl_rad) - math.sin(lat_rad) * sin_altitude) /
                      (math.cos(lat_rad) * math.cos(math.asin(sin_altitude))))
        azimuth = math.degrees(math.acos(min(1, max(-1, cos_azimuth))))
        
        if hour_angle > 0:
            azimuth = 360 - azimuth
            
        return altitude, azimuth

    def _calculate_incident_angle(self, solar_altitude: float, solar_azimuth: float) -> float:
        """Calculate angle of incidence on tilted surface."""
        tilt_rad = math.radians(self.specs.tilt_angle)
        azimuth_rad = math.radians(solar_azimuth - self.specs.azimuth_angle)
        altitude_rad = math.radians(solar_altitude)
        
        cos_incident = (math.sin(altitude_rad) * math.cos(tilt_rad) +
                       math.cos(altitude_rad) * math.sin(tilt_rad) * math.cos(azimuth_rad))
        return math.degrees(math.acos(min(1, max(-1, cos_incident))))

    def simulate(self, start_time: datetime, duration_hours: int = 24,
                interval_minutes: int = 60) -> List[Tuple[datetime, float]]:
        """
        Simulate solar power generation for a given time period.
        
        Args:
            start_time: Starting datetime for simulation
            duration_hours: Duration of simulation in hours
            interval_minutes: Time interval between calculations in minutes
            
        Returns:
            List of tuples containing (datetime, power_kw)
        """
        results = []
        current_time = start_time
        end_time = start_time + timedelta(hours=duration_hours)
        
        while current_time <= end_time:
            # Calculate solar position
            altitude, azimuth = self._calculate_solar_position(current_time)
            
            # If sun is below horizon, power output is 0
            if altitude <= 0:
                results.append((current_time, 0.0))
                current_time += timedelta(minutes=interval_minutes)
                continue
            
            # Calculate incident angle
            incident_angle = self._calculate_incident_angle(altitude, azimuth)
            
            # Calculate basic insolation (simplified model)
            # Assuming clear sky conditions and standard atmospheric conditions
            air_mass = 1 / math.sin(math.radians(altitude))
            insolation = 1000 * math.pow(0.7, air_mass) * math.cos(math.radians(incident_angle))
            
            # Apply efficiency factors
            power_kw = (insolation * self.specs.capacity_kw * self.specs.efficiency) / 1000
            
            # Apply temperature derating (simplified)
            ambient_temp = 25  # Assumed constant ambient temperature
            power_kw *= (1 + self.specs.temperature_coefficient * (ambient_temp - 25))
            
            # Ensure power is non-negative and doesn't exceed capacity
            power_kw = max(0, min(power_kw, self.specs.capacity_kw))
            
            results.append((current_time, power_kw))
            current_time += timedelta(minutes=interval_minutes)
        
        return results 