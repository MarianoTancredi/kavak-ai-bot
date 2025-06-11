import pandas as pd
from typing import List, Optional
from fuzzywuzzy import fuzz, process
from ..models.car import Car, CarFilter


class CarService:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.cars = [Car(**row.to_dict()) for _, row in self.df.iterrows()]
    
    def get_all_cars(self) -> List[Car]:
        return self.cars
    
    def search_cars(self, filters: CarFilter, limit: int = 10) -> List[Car]:
        filtered_df = self.df.copy()
        
        if filters.make:
            makes = filtered_df['make'].unique()
            best_match = process.extractOne(filters.make, makes, scorer=fuzz.ratio)
            if best_match and best_match[1] >= 70:
                filtered_df = filtered_df[filtered_df['make'] == best_match[0]]
        
        if filters.model:
            models = filtered_df['model'].unique()
            best_match = process.extractOne(filters.model, models, scorer=fuzz.ratio)
            if best_match and best_match[1] >= 70:
                filtered_df = filtered_df[filtered_df['model'] == best_match[0]]
        
        if filters.min_price:
            filtered_df = filtered_df[filtered_df['price'] >= filters.min_price]
        
        if filters.max_price:
            filtered_df = filtered_df[filtered_df['price'] <= filters.max_price]
        
        if filters.max_km:
            filtered_df = filtered_df[filtered_df['km'] <= filters.max_km]
        
        if filters.min_year:
            filtered_df = filtered_df[filtered_df['year'] >= filters.min_year]
            
        if filters.max_year:
            filtered_df = filtered_df[filtered_df['year'] <= filters.max_year]
        
        filtered_df = filtered_df.sort_values('price')
        
        return [Car(**row.to_dict()) for _, row in filtered_df.head(limit).iterrows()]
    
    def get_car_by_id(self, stock_id: str) -> Optional[Car]:
        car_data = self.df[self.df['stock_id'] == stock_id]
        if not car_data.empty:
            return Car(**car_data.iloc[0].to_dict())
        return None
    
    def get_popular_makes(self) -> List[str]:
        return self.df['make'].value_counts().head(10).index.tolist()
    
    def get_price_range(self) -> dict:
        return {
            'min': float(self.df['price'].min()),
            'max': float(self.df['price'].max()),
            'avg': float(self.df['price'].mean())
        }