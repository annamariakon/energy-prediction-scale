from building_class import Building
import time
import pandas as pd
from eppy.runner.run_functions import runIDFs
from idf_functions.modify_idf_for_simulation import make_eplaunch_options

"""Main code file to run multiple Energyplus simulations in parallel."""

bagdata = pd.read_csv("bag_adres_ids.csv")
runs = []

building_database = []

for i, obj_data in bagdata[:200].iterrows():
    
    bag_adres_id = obj_data['BAG Adres ID']
    print(bag_adres_id,i)
    building = Building(bag_adres_id)

    building.batch_number = i // 1000
    idf = building.initiate_idf() # Create IDF file
    building.apply_retrofit_action(0,0,0,0,0,0) # Wall, Floor, Roof, Window U-value, SHGC, Infiltration
    building.get_retrofit_data()

    path_to_epw = './epw_file/NLD_ZH_Rotterdam.The.Hague.AP.063440_TMYx.2009-2023.epw' #download epw file from https://climate.onebuilding.org/EnergyPlus_Weather_Files/Europe_North/Netherlands/
    ddypath = './epw_file/NLD_ZH_Rotterdam.The.Hague.AP.063440_TMYx.2009-2023.ddy'
    idf.epw = path_to_epw    

    idf = building.modify_idf(idf, ddypath)

    idf.save()
    theoptions = make_eplaunch_options(idf)

    runs.append([idf, theoptions])
    building_database.append(building.__dict__)

df_building_database = pd.DataFrame(building_database)
df_building_database.to_csv('building_database.csv', index=False)

num_CPUs = 4
start_time = time.time()
runIDFs(runs, num_CPUs)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Simulation time: {elapsed_time} seconds")

Building.get_heating_cooling_multi(df_building_database)
