import pandas as pd
import numpy as np
import ast
import torch
import joblib

from run_surrogate_files.nn_class import NeuralNet_2
from geomeppy import IDF
from idf_functions.getdata_functions_building import getNieman_data, get3DBAG_data, getpp_data
from idf_functions.getdata_functions_apartment import modify_apartment_geometry
from idf_functions.create_idf_file import create_idf, assign_adiabatic_surfaces, add_spaces
from idf_functions.modify_idf_for_simulation import add_ventilation_from_window_opening, add_location_design_days, add_year_long_run_period, update_idf_for_fenestration, add_design_flow_rate
from idf_functions.modify_idf_for_simulation import add_schedules, add_people_lighting_equipment, create_temperature_schedule_type_limits, add_output_variables, add_simulation_control, add_thermostat_and_ideal_loads, assign_constructions_to_surfaces, make_eplaunch_options
from idf_functions.get_retrofit_data import update_construction_materials, get_initial_r_values, get_retrofits

"""Main code file to run the Energyplus simulation"""

class Building:

    nieman_path = './ep_nieman_tudelft_18_10.csv' # path to the Nieman database 
    
    rw_retr, rf_retr, rr_retr, ru_retr, shgc_retr, inf_retr = (0,) * 6 # Retrofits (0: current condition, 1/2/3: Retrofits)
    r_wall_ins, r_floor_ins, r_roof_ins, u_window, shgc, inf_rate = (0,) * 6

    def __init__(self, bag_adres_id):
        
        self.bag_adres_id = bag_adres_id
        self.wwr = 0.3
        self.bool_ad = False
        self.heat_setp = 20
        self.cool_setp = 24
        self.ventilation_rate = 0.0009
        self.batch_number = 0
        self.output_dir = './simulation_files'
        self.watts_per_zone = 2 # Watts per zone floor area for lighting and equipment
        self.heating_m2, self.cooling_m2 = (0,) * 2
        
        """Querying information at building unit level from the Nieman database."""
        self.bag_pand_id, self.n_archetype, self.n_num_floor, self.n_total_floor_area = getNieman_data(self.bag_adres_id, self.nieman_path)
        
        """Querying information at *building* (not building unit) level from the 3DBAG database."""
        self.bag_ground_floor_area, self.bag_area_walls_exp, self.bag_area_walls_adiab, self.bag_vertices, self.bag_building_height, self.bag_num_floor, self.bag_roof_type = get3DBAG_data(ast.literal_eval(self.bag_pand_id)[0]) # Uses the numeric ID from the string

        """Post-processing the data to extract other information."""
        self.pp_ht_floor, self.pp_compactness_ratio, self.pp_orientation = getpp_data(self.bag_vertices, self.bag_building_height, self.bag_num_floor, self.bag_area_walls_exp, self.bag_ground_floor_area, self.n_total_floor_area)

        """If the archetype corresponds to an apartment, then the geometry is modified."""
        if self.n_archetype in [2, 3, 4, 5, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20]:
            self.bag_area_walls_exp, self.bag_area_walls_adiab, self.bag_ground_floor_area, self.pp_orientation, self.pp_compactness_ratio, self.bool_ad = modify_apartment_geometry(self.bag_pand_id, self.bag_num_floor, self.n_num_floor, self.nieman_path, self.bag_vertices, self.n_archetype, self.pp_ht_floor, self.n_total_floor_area, self.pp_compactness_ratio)

        one_hot_encoder_archetype = joblib.load('./run_surrogate_files/one_hot_encoder_archetype.joblib')
        encoded = one_hot_encoder_archetype.transform([[self.n_archetype]])
        self.one_hot_enc_archetype = encoded[0].tolist() # One-hot encoding of the archetype

    def initiate_idf(self):

        output_dir = f'{self.output_dir}/{self.batch_number}'
        if self.n_archetype in [6, 7, 8, 21]:
            idf = create_idf(self.bag_adres_id, self.bag_vertices, self.bag_building_height, self.n_num_floor, output_dir)
        else:
            unit_height = self.pp_ht_floor*self.n_num_floor
            idf = create_idf(self.bag_adres_id, self.bag_vertices, unit_height, self.n_num_floor, output_dir)
        
        idf = assign_adiabatic_surfaces(idf, self.n_archetype, self.bool_ad) 
        idf = add_spaces(idf)
        idf.save()

        return idf
    
    def get_retrofit_data(self):
        
        components = ['r_wall_ins', 'r_floor_ins', 'r_roof_ins', 'u_window', 'shgc', 'inf_rate']
        retrofits = [self.rw_retr, self.rf_retr, self.rr_retr, self.ru_retr, self.shgc_retr, self.inf_retr]
        
        for comp, retr in zip(components, retrofits):
            if retr == 0:
                val = get_initial_r_values(self.n_archetype, comp)
            else:
                val = get_retrofits(comp, retr)
        
            setattr(self, comp, val)

    def modify_idf(self, idf, ddypath):
            
        add_location_design_days(idf, ddypath) # Specify location, design days, run period and ground temperatures
        add_year_long_run_period(idf)

        update_construction_materials(idf, self.n_archetype, self.r_wall_ins, self.r_floor_ins, self.r_roof_ins, self.u_window, self.shgc)         
        update_idf_for_fenestration(idf, self.wwr) # Add windows to the model 
        assign_constructions_to_surfaces(idf) # Assign constructions to the building surfaces

        add_thermostat_and_ideal_loads(idf, self.heat_setp, self.cool_setp) # Add an ideal loads air system with infinite capacity (operates based on the thermostat settings)
        create_temperature_schedule_type_limits(idf) # limits for fraction and temperature schedules

        add_schedules(idf) # Create schedules	
        add_design_flow_rate(idf, self.inf_rate, self.ventilation_rate)
        add_people_lighting_equipment(idf, self.watts_per_zone) # Add people, equipment and lighting loads
        add_ventilation_from_window_opening(idf)

        add_simulation_control(idf)
        add_output_variables(idf)

        #IDF.view_model(idf) # View final model
        idf.save()

        return idf

    def run_simulation(self, idf):
        theoptions = make_eplaunch_options(idf)
        idf.run(**theoptions)

    def apply_retrofit_action(self, rw_retr, rf_retr, rr_retr, ru_retr, shgc_retr, inf_retr):
        self.rw_retr, self.rf_retr, self.rr_retr, self.ru_retr, self.shgc_retr, self.inf_retr = rw_retr, rf_retr, rr_retr, ru_retr, shgc_retr, inf_retr

    def get_heating_cooling_m2(self):
        
        iddfile  = "C:/EnergyPlusV23-1-0/Energy+.idd"
        IDF.setiddname(iddfile)    

        idf_path = f"{self.output_dir}/{self.batch_number}/{self.bag_adres_id}.idf"
        csv_path = f"{self.output_dir}/{self.batch_number}/Outputs/{self.bag_adres_id}Table.csv"
        results_new = pd.read_csv(csv_path, header=None, names=range(12))

        idf = IDF(idf_path)

        surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
        floors = [surface for surface in surfaces if surface.Surface_Type =='floor']

        building_area = sum(floor.area for floor in floors) 

        zones = idf.idfobjects["ZONE"]
        cooling_sum = 0
        heating_sum = 0
        
        for j in range(len(zones)):
            
            cooling_zone = sum(results_new.iloc[12 + j*21 : 18 + j*21, 2].astype(float)) # For cooling, take only values between April and September
            heating_zone = sum(results_new.iloc[9+(len(zones)+j)*21:12+(len(zones)+j)*21,2].astype(float))+sum(results_new.iloc[18+(len(zones)+j)*21:21+(len(zones)+j)*21,2].astype(float)) # For heating, take only values between October and March
            
            cooling_sum += cooling_zone
            heating_sum += heating_zone

            #print(cooling_zone/(3600000*(building_area/len(floors))))
            #print(heating_zone/(3600000*(building_area/len(floors))))

        self.heating_m2 = heating_sum/(3600000*building_area) # sum the energy of all floors, convert to kWh/m2 and normalize by the total area
        self.cooling_m2 = cooling_sum/(3600000*building_area)

    @staticmethod
    def get_heating_cooling_multi(df_building_database):
        
        output_dir = './simulation_files'
        for i, building_data in df_building_database.iterrows():
            
            iddfile  = "C:/EnergyPlusV23-1-0/Energy+.idd"
            IDF.setiddname(iddfile)    

            bag_adres_id = building_data['bag_adres_id']
            batch_number = building_data['batch_number']
            
            idf_path = f"{output_dir}/{batch_number}/{bag_adres_id}.idf"
            csv_path = f"{output_dir}/{batch_number}/Outputs/{bag_adres_id}Table.csv"
            results_new = pd.read_csv(csv_path, header=None, names=range(12))

            idf = IDF(idf_path)

            surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
            floors = [surface for surface in surfaces if surface.Surface_Type =='floor']

            building_area = sum(floor.area for floor in floors) 

            zones = idf.idfobjects["ZONE"]
            cooling_sum = 0
            heating_sum = 0
            
            for j in range(len(zones)):
                
                cooling_zone = sum(results_new.iloc[12 + j*21 : 18 + j*21, 2].astype(float)) # For cooling, take only values between April and September
                heating_zone = sum(results_new.iloc[9+(len(zones)+j)*21:12+(len(zones)+j)*21,2].astype(float))+sum(results_new.iloc[18+(len(zones)+j)*21:21+(len(zones)+j)*21,2].astype(float)) # For heating, take only values between October and March
                
                cooling_sum += cooling_zone
                heating_sum += heating_zone

                #print(cooling_zone/(3600000*(building_area/len(floors))))
                #print(heating_zone/(3600000*(building_area/len(floors))))

            heating_m2 = heating_sum/(3600000*building_area) # sum the energy of all floors, convert to kWh/m2 and normalize by the total area
            cooling_m2 = cooling_sum/(3600000*building_area)

            df_building_database.loc[i, heating_m2] = heating_m2
            df_building_database.loc[i, cooling_m2] = cooling_m2
        
        df_building_database.to_csv('building_database.csv', index=False)

    def predict_heating_cooling_surrogate(self):

        input_size = 31
        hidden_size = 64 # 64 neurons in each hidden layer
        output_size = 2

        model = NeuralNet_2(input_size, hidden_size, hidden_size, output_size)

        model.load_state_dict(torch.load('./run_surrogate_files/surrogate_heating_cooling_2.pth'))
        model.eval() # set model to evaluation mode

        input_scaler = joblib.load('./run_surrogate_files/input_scaler_2.pkl') # scale input
        output_scaler = joblib.load('./run_surrogate_files/output_scaler_2.pkl') # scale output

        inputs = [self.one_hot_enc_archetype, self.n_num_floor, self.pp_ht_floor, self.pp_orientation,
                  self.n_total_floor_area, self.bag_ground_floor_area, self.bag_area_walls_exp, self.bag_area_walls_adiab, self.pp_compactness_ratio,
                  self.r_wall_ins, self.r_roof_ins, self.r_floor_ins, self.u_window, self.inf_rate]
        
        input_features = []

        for input in inputs:
    
            if isinstance(input, list):  # flatten list in case of one-hot encoding or array
                input_features.extend(input)
            else:
                input_features.append(input)

        input_scaled = input_scaler.transform([input_features])

        with torch.no_grad():
            y_pred_scaled = model(torch.tensor(input_scaled, dtype=torch.float32)) # run model for prediction

        y_pred = output_scaler.inverse_transform(y_pred_scaled.numpy())

        self.heating_m2 = y_pred[0, 0] # extract heating demand
        self.cooling_m2 = y_pred[0, 1] # extract cooling demand

            
                
                

