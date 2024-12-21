from datetime import datetime
import pandas as pd
from .plant import SolarPlant

class SolarSimulator:
    """ Simulate solar power generation """
    def __init__(self, plant: SolarPlant):
        self.plant = plant

    def generate_timeseries(
        self,
        start_date: datetime,
        end_date: datetime,
        freq: str = "1h"
    ) -> pd.DataFrame:
        """
        Generate a time series of solar power production.
        
        Args:
            start_date: Start datetime for simulation
            end_date: End datetime for simulation
            freq: Frequency string (e.g., '1H' for hourly, '15T' for 15 minutes)
                 See pandas frequency strings for more options
        
        Returns:
            DataFrame with datetime index and power_kw column
        """
        
        # Calculate duration in hours and interval in minutes
        total_hours = (end_date - start_date).total_seconds() / 3600
        interval_minutes = pd.Timedelta(freq).total_seconds() / 60
        
        # Run simulation
        results = self.plant.simulate(
            start_time=start_date,
            duration_hours=int(total_hours),
            interval_minutes=int(interval_minutes)
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=['datetime', 'power_kw'])
        df.set_index('datetime', inplace=True)
        df.index.freq = pd.infer_freq(df.index)
        
        return df 