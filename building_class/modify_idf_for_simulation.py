import os
from geomeppy import IDF

def add_location_design_days(idf, ddypath):
    
    # Remove existing data to avoid duplicates that will cause errors during simulation
    idf.idfobjects['SITE:LOCATION'].clear()
    idf.idfobjects['SIZINGPERIOD:DESIGNDAY'].clear()

    # Add site location 
    idf.newidfobject('SITE:LOCATION',
                     Name='Rotterdam.The.Hague.AP',
                     Latitude=51.96,
                     Longitude=4.45,
                     Time_Zone=1,
                     Elevation=-4.50)

    # Add design days from the DDY file
    ddyidf = IDF(ddypath)
    for dd in ddyidf.idfobjects['SIZINGPERIOD:DESIGNDAY']:
        idf.copyidfobject(dd)

def add_year_long_run_period(idf):
    
    # Remove existing data to avoid duplicates that will cause errors during simulation   
    idf.idfobjects['RUNPERIOD'].clear()    
    idf.idfobjects['TIMESTEP'].clear()
    
    # Define how many timesteps per hour to calculate / reduce for smaller time but lower accuracy
    idf.newidfobject("TIMESTEP", Number_of_Timesteps_per_Hour=6)

    # Define simulation run period
    idf.newidfobject(
        "RUNPERIOD",
        Name="RUNPERIOD 1",
        Begin_Month=1,
        Begin_Day_of_Month=1,
        End_Month=12,
        End_Day_of_Month=31,
        Day_of_Week_for_Start_Day="Sunday",
        Use_Weather_File_Holidays_and_Special_Days="No",
        Use_Weather_File_Daylight_Saving_Period="No",
        Apply_Weekend_Holiday_Rule="No",
        Use_Weather_File_Rain_Indicators="Yes",
        Use_Weather_File_Snow_Indicators="Yes"
    )

def add_ground_temperatures(idf):
    
    # Remove existing data to avoid duplicates that will cause errors during simulation 
    idf.idfobjects["SITE:GROUNDTEMPERATURE:BUILDINGSURFACE"].clear()

    # Ground floor temperature is set to 18 degrees Celsius for all months to avoid extreme temperature variations
    idf.newidfobject(
        "SITE:GROUNDTEMPERATURE:BUILDINGSURFACE",
        January_Ground_Temperature=18,
        February_Ground_Temperature=18,
        March_Ground_Temperature=18,
        April_Ground_Temperature=18,
        May_Ground_Temperature=18,
        June_Ground_Temperature=18,
        July_Ground_Temperature=18,
        August_Ground_Temperature=18,
        September_Ground_Temperature=18,
        October_Ground_Temperature=18,
        November_Ground_Temperature=18,
        December_Ground_Temperature=18,
    )

# Add windows to the model
def update_idf_for_fenestration(idf, wwr):
        
    idf.idfobjects['FENESTRATIONSURFACE:DETAILED'].clear()    
    IDF.set_wwr(idf, wwr=wwr, force=True, construction='Window1C')

    windows = idf.idfobjects['FENESTRATIONSURFACE:DETAILED']
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    walls = [surface for surface in surfaces if surface.Surface_Type =='Wall']

    for window in windows: # Delete windows that are on adiabatic walls
        for wall in walls:
            if window.Building_Surface_Name == wall.Name:
                
                if wall.Outside_Boundary_Condition == 'ADIABATIC':
                    del window[:]

# Add an ideal loads air system with infinite capacity (operates based on the thermostat settings)
def add_thermostat_and_ideal_loads(idf, heat_setp, cool_setp):
    
    idf.idfobjects["HVACTEMPLATE:THERMOSTAT"].clear()
    idf.idfobjects["HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM"].clear()

    # Create a thermostat setting object
    stat = idf.newidfobject("HVACTEMPLATE:THERMOSTAT", 
                            Name="Zone Stat", 
                            Constant_Heating_Setpoint=heat_setp, 
                            Constant_Cooling_Setpoint=cool_setp)
    
    # Iterate over each zone in the IDF and add an ideal loads air system linked to the created thermostat
    for zone in idf.idfobjects["ZONE"]: 
        idf.newidfobject("HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM", 
                         Zone_Name=zone.Name, 
                         Template_Thermostat_Name=stat.Name,
                         Heating_Limit="LimitCapacity",
                         Maximum_Sensible_Heating_Capacity=1000000, # artificially high value to account for infinite capacity
                         Cooling_Limit="LimitCapacity",
                         Maximum_Total_Cooling_Capacity=1000000, # artificially high value to account for infinite capacity	
                         Dehumidification_Control_Type="None",
                         Humidification_Control_Type="None")
        
def create_temperature_schedule_type_limits(idf):
    
    idf.idfobjects['SCHEDULETYPELIMITS'].clear()

    idf.newidfobject(
        'SCHEDULETYPELIMITS',
        Name= 'Activity Level',
        Lower_Limit_Value=0,
        Upper_Limit_Value= "",
        Numeric_Type='Continuous',
        Unit_Type='activitylevel'
        )

    idf.newidfobject(
        'SCHEDULETYPELIMITS',
        Name='Fractional',
        Lower_Limit_Value=0,
        Upper_Limit_Value=1,
        Numeric_Type='Continuous',
        Unit_Type='Dimensionless',
        )

    idf.newidfobject(
        'SCHEDULETYPELIMITS',
        Name='Temperature',
        Lower_Limit_Value=-60,  # Adjust based on the lowest expected temperature for your location
        Upper_Limit_Value=200,  # Adjust based on the highest expected temperature for your location
        Numeric_Type='Continuous',
        Unit_Type='Temperature',
    )

def add_schedules(idf):

    idf.idfobjects['SCHEDULE:DAY:INTERVAL'].clear()
    idf.idfobjects['SCHEDULE:WEEK:DAILY'].clear()
    idf.idfobjects['SCHEDULE:YEAR'].clear()

    idf.newidfobject(
        'SCHEDULE:DAY:INTERVAL',
        Name='Occupancy_pattern_gains_daily',
        Schedule_Type_Limits_Name='Fractional',
        Interpolate_to_Timestep='No',
        Time_1='08:00',
        Value_Until_Time_1=0.5,
        Time_2='23:00',
        Value_Until_Time_2=1,
        Time_3='24:00',
        Value_Until_Time_3=0.5
    )

    idf.newidfobject(
        'SCHEDULE:WEEK:DAILY',
        Name='Occupancy_pattern_gains_weekly',
        Sunday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Monday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Tuesday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Wednesday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Thursday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Friday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Saturday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        Holiday_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        SummerDesignDay_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        WinterDesignDay_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        CustomDay1_ScheduleDay_Name='Occupancy_pattern_gains_daily',
        CustomDay2_ScheduleDay_Name='Occupancy_pattern_gains_daily'
    )

    idf.newidfobject(
        'SCHEDULE:YEAR',
        Name='Occupancy_Schedule',
        Schedule_Type_Limits_Name='Fractional',
        ScheduleWeek_Name_1='Occupancy_pattern_gains_weekly',
        Start_Month_1=1,
        Start_Day_1=1,
        End_Month_1=12,
        End_Day_1=31
    )

    idf.newidfobject(
        'SCHEDULE:DAY:INTERVAL',
        Name='Seated Adult Activity_Day Schedule',
        Schedule_Type_Limits_Name='Activity Level',
        Interpolate_to_Timestep='No',
        Time_1='24:00',
        Value_Until_Time_1=120
    )

    idf.newidfobject(
        'SCHEDULE:WEEK:DAILY',
        Name='Seated Adult Activity Week Rule - Jan1-Dec31',
        Sunday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Monday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Tuesday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Wednesday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Thursday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Friday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Saturday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        Holiday_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        SummerDesignDay_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        WinterDesignDay_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        CustomDay1_ScheduleDay_Name='Seated Adult Activity_Day Schedule',
        CustomDay2_ScheduleDay_Name='Seated Adult Activity_Day Schedule'
    )

    idf.newidfobject(
        'SCHEDULE:YEAR',
        Name = 'Seated Adult Activity',
        Schedule_Type_Limits_Name = 'Activity Level',
        ScheduleWeek_Name_1 = 'Seated Adult Activity Week Rule - Jan1-Dec31',
        Start_Month_1 = 1,
        Start_Day_1 = 1,
        End_Month_1 = 12,
        End_Day_1 = 31
    )

def add_people_lighting_equipment(idf, watts_per_zone):
    
    idf.idfobjects['LIGHTS'].clear()
    idf.idfobjects['ELECTRICEQUIPMENT'].clear()

    for zone in idf.idfobjects["ZONE"]:
        
        idf.newidfobject("PEOPLE",
                         Name = f"People_{zone.Name}",
                         Zone_or_ZoneList_or_Space_or_SpaceList_Name = zone.Name,
                         Number_of_People_Schedule_Name = "Occupancy_Schedule",
                         Number_of_People_Calculation_Method = "People/Area",
                         Number_of_People = "",
                         People_per_Floor_Area = 0.035,
                         Floor_Area_per_Person = "",
                         Fraction_Radiant = 0.3,
                         Sensible_Heat_Fraction = 0.66,
                         Activity_Level_Schedule_Name = "Seated Adult Activity"
                         )

        idf.newidfobject("LIGHTS",
                        Name = f"Lighting_{zone.Name}", 
                        Zone_or_ZoneList_or_Space_or_SpaceList_Name = zone.Name,
                        Schedule_Name = "Occupancy_Schedule",
                        Design_Level_Calculation_Method = "Watts/Area",
                        Lighting_Level = "",
                        Watts_per_Zone_Floor_Area = watts_per_zone,  
                        Watts_per_Person = "",
                        Return_Air_Fraction = 0,
                        Fraction_Radiant = 0.32,
                        Fraction_Visible = 0.25,
                        Fraction_Replaceable = 1,
                        EndUse_Subcategory = "General"
                        )
        
        idf.newidfobject("ELECTRICEQUIPMENT",
                        Name = f"Equipment_{zone.Name}",
                        Zone_or_ZoneList_or_Space_or_SpaceList_Name = zone.Name,
                        Schedule_Name = "Occupancy_Schedule",
                        Design_Level_Calculation_Method = "Watts/Area",
                        Design_Level = "",
                        Watts_per_Zone_Floor_Area = watts_per_zone,  
                        Watts_per_Person = "",
                        Fraction_Latent = 0,
                        Fraction_Radiant = 0,
                        Fraction_Lost = 0,                        
                        EndUse_Subcategory = "Electric Equipment"
                        )

def add_ventilation_from_window_opening(idf):

    idf.idfobjects["ZONEVENTILATION:WINDANDSTACKOPENAREA"].clear()

    for window in idf.idfobjects['FENESTRATIONSURFACE:DETAILED']:

        idf.newidfobject("ZONEVENTILATION:WINDANDSTACKOPENAREA",
                         Name = f"{window.Name}_Opening",               
                         Zone_or_Space_Name = " ".join(window.Building_Surface_Name.split("Wall")[0].split()),
                         Opening_Effectiveness = 0.8,
                         Effective_Angle = 118,
                         Minimum_Indoor_Temperature = -100,
                         Maximum_Indoor_Temperature = 24,
                         Minimum_Outdoor_Temperature = 20,
                         Maximum_Outdoor_Temperature = 100,
                         Maximum_Wind_Speed = 40,
                        )

def add_design_flow_rate(idf, infiltration_rate, ventilation_rate):

    idf.idfobjects["SCHEDULE:CONSTANT"].clear()
    idf.idfobjects["ZONEINFILTRATION:DESIGNFLOWRATE"].clear()
    idf.idfobjects["ZONEVENTILATION:DESIGNFLOWRATE"].clear()

    idf.newidfobject("SCHEDULE:CONSTANT",
                     Name = "Infiltration_Schedule",
                     Schedule_Type_Limits_Name="Fractional",
                     Hourly_Value = 1)
    
    for zone in idf.idfobjects["ZONE"]:
        # Construct one Infiltration and Ventilation object per zone
        inf_name = f"ZN INFILTR {zone.Name}"
        vent_name = f"ZN VENT {zone.Name}"

        idf.newidfobject(
            "ZONEINFILTRATION:DESIGNFLOWRATE",
            Name = inf_name,
            Schedule_Name = "Infiltration_Schedule",
            Zone_or_ZoneList_or_Space_or_SpaceList_Name = zone.Name,
            Design_Flow_Rate_Calculation_Method = "Flow/ExteriorWallArea",
            Flow_Rate_per_Exterior_Surface_Area = infiltration_rate
        ) #m3/s*m2         

        idf.newidfobject(
            "ZONEVENTILATION:DESIGNFLOWRATE",
            Name = vent_name,
            Schedule_Name = "Occupancy_Schedule",
            Zone_or_ZoneList_or_Space_or_SpaceList_Name = zone.Name,
            Design_Flow_Rate_Calculation_Method = "Flow/Area",
            Flow_Rate_per_Floor_Area = ventilation_rate,
            Ventilation_Type = "Natural"
        ) #m3/s*m2  

def assign_constructions_to_surfaces(idf):

    # Retrieve lists of all detailed building surfaces from the IDF file
    surfaces = idf.idfobjects['BUILDINGSURFACE:DETAILED']
    
    # Filter surfaces by type
    walls = [surface for surface in surfaces if surface.Surface_Type =='wall']
    floors = [surface for surface in surfaces if surface.Surface_Type =='floor']
    ceilings = [surface for surface in surfaces if surface.Surface_Type =='ceiling']
    roofs = [surface for surface in surfaces if surface.Surface_Type =='roof']

    ext_floors = [f for f in floors if f.Vertex_1_Zcoordinate == 0]
    int_floors = [f for f in floors if f.Vertex_1_Zcoordinate > 0]
    
    #Assign Constructions & Boundary Conditions to Surfaces
    for wall in walls:
        wall.Construction_Name = 'Ext_Walls1C'
    for ext_floor in ext_floors:
        ext_floor.Construction_Name = "GroundFloor1C"
    for int_floor in int_floors:
        int_floor.Construction_Name = 'Int_Floors1C'
    for ceiling in ceilings:
        ceiling.Construction_Name = 'Int_Ceiling1C'
    for roof in roofs:
        roof.Construction_Name = "Roof1C"

def add_simulation_control(idf):
    
    idf.idfobjects['SIMULATIONCONTROL'].clear()
    
    idf.newidfobject(
        'SIMULATIONCONTROL',
        Do_Zone_Sizing_Calculation='Yes',
        Do_System_Sizing_Calculation='Yes',
        Do_Plant_Sizing_Calculation= 'No',
        Run_Simulation_for_Weather_File_Run_Periods= 'Yes', # performs only annual simulations
        Run_Simulation_for_Sizing_Periods= 'Yes',
        Do_HVAC_Sizing_Simulation_for_Sizing_Periods= 'Yes'
    )

def add_output_variables(idf):

    idf.idfobjects['OUTPUT:TABLE:SUMMARYREPORTS'].clear()
    idf.idfobjects['OUTPUT:VARIABLE'].clear()

    # idf.newidfobject('OUTPUT:VARIABLE',
    #                  Variable_Name="Zone Mean Air Temperature",
    #                  Reporting_Frequency="Hourly",)

    idf.newidfobject("OUTPUT:TABLE:SUMMARYREPORTS",
                     Report_1_Name="ZoneCoolingSummaryMonthly",
                     Report_2_Name="ZoneHeatingSummaryMonthly")

def make_eplaunch_options(idf):

    idfversion = idf.idfobjects['VERSION'][0].Version_Identifier.split('.')
    idfversion.extend([0] * (3 - len(idfversion)))
    idfversionstr = '-'.join([str(item) for item in idfversion])
    fname = idf.idfname

    options = {
        'ep_version':idfversionstr, # runIDFs needs the version number
        'output_prefix':os.path.basename(fname).split('.')[0],
        'output_suffix':'C',
        'output_directory':os.path.dirname(fname)+'\Outputs',
        'readvars':True,
        'expandobjects':True
        }

    return options

