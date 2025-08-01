from building_class import Building

"""Main code file to run Energyplus simulations."""

# Insert BAG Adres ID (BAG Adres ID is a unique identifier for each unit (e.g. single family house, apartment) inside a building.)
bag_adres_id = 599200000445576

# Create class instance
building = Building(bag_adres_id)

building.apply_retrofit_action(0,0,0,0,0,0) # Wall, Floor, Roof, Window U-value, SHGC, Infiltration
building.get_retrofit_data()

building.predict_heating_cooling_surrogate()
print(building.__dict__)
print("Heating demand:", building.heating_m2, "kWh/m2")
print("Cooling demand:", building.cooling_m2, "kWh/m2")