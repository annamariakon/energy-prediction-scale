from building_class import Building

"""Main code file to run Energyplus simulations."""

# Insert BAG Adres ID (BAG Adres ID is a unique identifier for each unit (e.g. single family house, apartment) inside a building.)
bag_adres_id = 599200000445576

# Create class instance
building = Building(bag_adres_id)

idf = building.initiate_idf() # Create IDF file

path_to_epw = './epw_file/NLD_ZH_Rotterdam.The.Hague.AP.063440_TMYx.2009-2023.epw' #download epw file from https://climate.onebuilding.org/EnergyPlus_Weather_Files/Europe_North/Netherlands/
ddypath = './epw_file/NLD_ZH_Rotterdam.The.Hague.AP.063440_TMYx.2009-2023.ddy'
idf.epw = path_to_epw
idf.save()

building.apply_retrofit_action(0,0,0,0,0,0) # Wall, Floor, Roof, Window U-value, SHGC, Infiltration
building.get_retrofit_data()

idf = building.modify_idf(idf, ddypath)

building.run_simulation(idf)
building.get_heating_cooling_m2()

print(building.__dict__)
print("Heating demand:", building.heating_m2, "kWh/m2")
print("Cooling demand:", building.cooling_m2, "kWh/m2")
