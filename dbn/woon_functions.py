import pandas as pd
import numpy as np
import bisect
import math
import os

def map_building_year(constr_year):
    years = [1905, 1925, 1945, 1955, 1965, 1975, 1985, 1995, 2005, 2015, 2020, 2025, 2030, 2035]
    year_mapped = bisect.bisect_left(years, constr_year)+1

    return year_mapped

def map_energy_label(energy_label):
    energy_labels = {'G':1, 'F':2, 'E':3, 'D':4, 'C':5, 'B':6, 'A':7, 'A+':8, 'A++':9, 'A+++':10, 'A++++':11, 'A+++++':12, 'Unknown':99}
    if type(energy_label) == str:
        energy_label_mapped = energy_labels[energy_label]
    else:
        energy_label_mapped = 99
    
    return energy_label_mapped

def map_archetype(archetype):
    archetype_mapped = 1 if archetype in [21] else \
                       2 if archetype in [7] else \
                       3 if archetype in [6,8] else \
                       4 if archetype in [9, 11, 15, 17, 19] else \
                       5 if archetype in [10, 12, 16, 18, 20] else 6
    
    return archetype_mapped

def get_typical_retrofits(comp_index):
    
    # Wall insulation typical retrofits
    # <1965: 0.24, 0.18, <1975: 0.24, 0.18, <1991: 0.20, 0.15, <2005: 0.16, 0.13, <2015: 0.14, 0.11, >2015: 0.14, 0.10
    r_wall_retrofits = [
        (1991, [4, 5.5]),
        (2005, [5, 6.7]),
        (2015, [6.2, 7.7]),
        (float("inf"), [7.1, 8.3])
    ]

    # Roof insulation typical retrofits
    # <1965: 0.24, 0.15, <1975: 0.22, 0.14, <1991: 0.20, 0.13, <2005: 0.16, 0.11, <2015: 0.13, 0.10, >2015: 0.13, 0.08
    r_roof_retrofits = [
        (1975, [4.2, 6.7]),
        (1991, [4.5, 7.1]),
        (2005, [5, 7.7]),
        (2015, [6.25, 8.3]), 
        (float("inf"), [7.7, 8.3])
    ]

    # Floor insulation typical retrofits
    # <1965: 0.25, 0.18, <1975: 0.25, 0.18, <1991: 0.20, 0.15, <2005: 0.16, 0.13, <2015: 0.14, 0.11, >2015: 0.14, 0.11
    r_floor_retrofits = [
        (1991, [4, 5.5]),
        (2005, [5, 5.7]),
        (2015, [5, 5.7]),
        (float("inf"), [5, 5.7]) 
    ] 

    # Glazing typical retrofits
    # All construction years have the same possible retrofits
    # emissivity of uncoated soda lime glass: 0.837, hard coating: 0.2, low-e: 0.08  
    u_glazing_retrofits = [[0.837, 0.837, 0, 1, 0.01, 0.016], # single glass
                         [0.837, 0.837, 1, 2, 0.004, 0.016], # double glass
                         [0.837, 0.08, 1, 2, 0.004, 0.016], # double low-e glass
                         [0.837, 0.08, 2, 3, 0.004, 0.016]] # triple low-e glass

    shgc_glazing_retrofits = [0.81, 0.7, 0.58, 0.5]
    
    infiltration_retrofits = {2: 0.0015, 3: 0.0018, 4: 0.00195, 5: 0.00195, 6: 0.003,
                    7: 0.00252, 8: 0.003, 9: 0.0021, 10: 0.0015, 11: 0.00175, 
                    12: 0.00125, 15: 0.0018, 16: 0.0015, 17: 0.0021, 18: 0.0015, 
                    19: 0.0014, 20: 0.001, 21: 0.0028}
    
    retrofit_sets = [r_wall_retrofits, r_roof_retrofits, r_floor_retrofits, u_glazing_retrofits, shgc_glazing_retrofits, infiltration_retrofits]
    return retrofit_sets[comp_index]  

def get_ins_type_age(comp_index, df_probs_component, df_probs_ad_ins, df_probs_last_5, archetype, year_cat, energy_label, constr_year):

    r_retrofits = get_typical_retrofits(comp_index)

    if math.isnan(energy_label)==False:
        retr_status = np.random.choice([0,1], p = df_probs_component.loc[archetype, year_cat, energy_label].iloc[:, 1].values)
    else:
        retr_status = np.random.choice([0,1], p = [np.mean([df_probs_component.loc[archetype, year_cat,i+1].iloc[0, 1] for i in range(12)]), 
                                               np.mean([df_probs_component.loc[archetype, year_cat,i+1].iloc[1, 1] for i in range(12)])])
    
    if retr_status == 0:
        ins_value_comp = 0  
        degr_year_comp = 2025 - constr_year
    else:   
        if math.isnan(energy_label)==False:
            ad_ins_wall_status = np.random.choice([0,1], p = df_probs_ad_ins.loc[archetype, year_cat, energy_label, comp_index+1].values)
            last_5_wall_status = np.random.choice([0,1], p = df_probs_last_5.loc[archetype, year_cat, energy_label, comp_index+1].values)
        else:
            ad_ins_wall_status = np.random.choice([0,1], p = [np.mean([df_probs_ad_ins.loc[archetype, year_cat,i+1, comp_index+1] for i in range(12)]), 
                                                    np.mean([df_probs_ad_ins.loc[archetype, year_cat,i+1, comp_index+1] for i in range(12)])])
            last_5_wall_status = np.random.choice([0,1], p = [np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, comp_index+1] for i in range(12)]), 
                                                    np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, comp_index+1] for i in range(12)])])

        if last_5_wall_status == 1:
            degr_year_comp = np.random.choice([0, 1, 2, 3, 4])
        elif ad_ins_wall_status == 1:
            degr_year_comp = np.random.choice(range(5, 2025-constr_year)) # put this max 35 as well
        else:
            degr_year_comp = 2025-constr_year
        
        degr_year_comp = min(degr_year_comp, 35)
        for cutoff, values in r_retrofits:
            if constr_year < cutoff:
                ins_value_comp = np.random.choice(values, p=[0.7, 0.3])
                break
    
    ageing_factor = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "09_12_2025_init_ageing_factor_ins.npz"))    
    age_factor = ageing_factor["arr0"][degr_year_comp-1]
    degr_rate_comp = np.random.normal(loc=age_factor, scale=age_factor/3, size=1)
    degr_state_comp = find_ins_degr_state_from_rate(degr_rate_comp)

    return ins_value_comp, degr_year_comp, degr_rate_comp, degr_state_comp, retr_status

def find_ins_degr_state_from_rate(degr_rate_comp):
    bin_size = 0.05
    n_bins = int(1/bin_size)
    
    for j in range(0, n_bins+1):
        if (degr_rate_comp < (j+1)*bin_size) and (degr_rate_comp >= j*bin_size):
            return j

def make_df_set_index(npz_file, arr, columns, column_indices):
    df = pd.DataFrame(npz_file[arr], columns=columns)
    return df.set_index(column_indices)

def get_heat_system_type_age(archetype, year_cat, energy_label, df_probs_heating, df_probs_last_5, constr_year):
    
    if math.isnan(energy_label)==False:
        heating_type = np.random.choice([0,1,2,3], p=df_probs_heating.loc[archetype, year_cat, energy_label].iloc[:,1].values)
    else:
        heating_type = np.random.choice([0,1,2,3], p=[np.mean([df_probs_heating.loc[archetype, year_cat,i+1].iloc[0, 1] for i in range(12)]), 
                                                    np.mean([df_probs_heating.loc[archetype, year_cat,i+1].iloc[1, 1] for i in range(12)]),
                                                    np.mean([df_probs_heating.loc[archetype, year_cat,i+1].iloc[2, 1] for i in range(12)]),
                                                    np.mean([df_probs_heating.loc[archetype, year_cat,i+1].iloc[3, 1] for i in range(12)]),
                                                    ])
        
    if heating_type in [0,3]:
        last_5_heating_status = 0
    elif heating_type == 1:
        if math.isnan(energy_label)==False:
            last_5_heating_status = np.random.choice([0,1], p = df_probs_last_5.loc[archetype, year_cat, energy_label, 5].values)
        else:
            last_5_heating_status = np.random.choice([0,1], p = [np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 5] for i in range(12)]), 
                                                        np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 5] for i in range(12)])])
    else:
        if math.isnan(energy_label)==False:
            last_5_heating_status = np.random.choice([0,1], p = df_probs_last_5.loc[archetype, year_cat, energy_label, 6].values)
        else:
            last_5_heating_status = np.random.choice([0,1], p = [np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 6] for i in range(12)]), 
                                                        np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 6] for i in range(12)])])
    
    if last_5_heating_status == 1:
        degr_year_heat = np.random.choice([0, 1, 2, 3, 4])
    else:
        degr_year_heat = np.random.choice(range(5, 2025-constr_year))
        degr_year_heat = min(degr_year_heat, 35)
    
    return (heating_type, degr_year_heat)

def get_cool_system_type_age(archetype, year_cat, energy_label, df_probs_cooling, constr_year):

    cooling_type = np.random.choice([0,1], p=df_probs_cooling.loc[archetype, year_cat, energy_label].iloc[:,1].values)
    degr_year_cool = np.random.choice(range(5, 2025-constr_year))
    degr_year_cool = min(degr_year_cool, 35)

    return (cooling_type, degr_year_cool)

def glaz_type_age(archetype, year_cat, energy_label, constr_year, df_probs_u, df_probs_last_5): 
    
    if math.isnan(energy_label)==False:
        retr_glazing = np.random.choice([0,1,2,3,4], p = df_probs_u.loc[archetype, year_cat, energy_label].iloc[:, 1].values)
    else:
        retr_glazing = np.random.choice([0,1,2,3,4], p = [np.mean([df_probs_u.loc[archetype, year_cat,i+1].iloc[0, 1] for i in range(12)]), 
                                                np.mean([df_probs_u.loc[archetype, year_cat,i+1].iloc[1, 1] for i in range(12)]),
                                                np.mean([df_probs_u.loc[archetype, year_cat,i+1].iloc[2, 1] for i in range(12)]),
                                                np.mean([df_probs_u.loc[archetype, year_cat,i+1].iloc[3, 1] for i in range(12)]),
                                                np.mean([df_probs_u.loc[archetype, year_cat,i+1].iloc[4, 1] for i in range(12)])
                                                ])

    if retr_glazing == 0:
        degr_year_u = min(2025 - constr_year, 35)
    elif retr_glazing in [1,2,3]:
        if math.isnan(energy_label)==False:
            last_5_u_status = np.random.choice([0,1], p = df_probs_last_5.loc[archetype, year_cat, energy_label, 4].values)
        else:
            last_5_u_status = np.random.choice([0,1], p = [np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 4] for i in range(12)]), 
                                                    np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 4] for i in range(12)])])
        if last_5_u_status == 1:
            degr_year_u = np.random.choice([0, 1, 2, 3, 4])
        else:
            degr_year_u = min(2025 - constr_year, 35)
    else:
        retr_glazing = np.random.choice([0,1,2,3], p=[0.25,0.25,0.25,0.25]) 
        if math.isnan(energy_label)==False:
            last_5_u_status = np.random.choice([0,1], p = df_probs_last_5.loc[archetype, year_cat, energy_label, 4].values)
        else:
            last_5_u_status = np.random.choice([0,1], p = [np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 4] for i in range(12)]), 
                                                    np.mean([df_probs_last_5.loc[archetype, year_cat,i+1, 4] for i in range(12)])])
        if last_5_u_status == 1:
            degr_year_u = np.random.choice([0, 1, 2, 3, 4])
        else:
            degr_year_u = np.random.choice(range(5, 2025-constr_year))
            degr_year_u = min(degr_year_u, 35)

    degr_year_u = min(degr_year_u, 35)

    return(retr_glazing, degr_year_u)

def calc_u_glazing(glaz_type, per_arg):
    
    glaz_data = get_typical_retrofits(3)
    ems1, ems2, n_gaps, n_glass, d_glass, d_gap = glaz_data[glaz_type]

    sigma = 5.67*(10**-8)  # Stefan-Boltzmann constant
    Tm = 283 # mean temperature in K
    A = 0.035
    n = 0.38
    D_T = 15
    if n_gaps > 1:
        D_T = D_T/n_gaps
    per_air = 1 - per_arg

    rho_arg = 1.699
    mu_arg = 2.164*(10**-5)
    lambda_arg = 1.684*(10**-2)
    c_arg = 0.519*(10**3)

    rho_air = 1.232
    mu_air = 1.761*(10**-5)
    lambda_air = 2.496*(10**-2)
    c_air = 1.008*(10**3)

    rho_mix = per_arg*rho_arg + per_air*rho_air
    mu_mix = per_arg*mu_arg + per_air*mu_air
    lambda_mix = per_arg*lambda_arg + per_air*lambda_air
    c_mix = per_arg*c_arg + per_air*c_air
    
    Nu = A*((((9.81*(d_gap**3)*D_T*(rho_mix**2))/(Tm*(mu_mix**2)))*(mu_mix*c_mix/lambda_mix))**n)
    
    h_g = Nu*lambda_mix/d_gap 
    h_r = 4 * sigma * ((1/ems1 + 1/ems2 - 1)**(-1))*(Tm**3)
    hs = h_r + h_g

    heat_transf = 1/(n_gaps/hs+n_glass*d_glass*1) # 1 is resistivity of soda-lime glass    
    h_int = 4.1*ems2/0.837+3.6

    u_value = 1/(1/25 + 1/heat_transf + 1/h_int)

    return round(u_value, 2)
