# A Repository for building-level energy assessment at scale considering material, equipment & weather uncertainties

This repository contains the codes referring to the paper "Decision support system for urban energy retrofit planning under uncertainties". The code provides building-level assessments of energy demand for many buildings at a time considering material and equipment performance and weather data under different scenarios. The final outcome are plots with heating and cooling demand at building and district level with different probabilities. 

![Plots of heating & cooling demand](images/heating_cooling_demand.png)

Connecting to open-source GIS data, the extraction of building geometry is automated, whereas the connection to probabilities from WoonData provides realistic estimation of properties given the archetype and label of the building. The scripts are adjusted for Rotterdam (the Netherlands) and can also be used for other cities in the same country. ++ description of main workflow

![Graphical abstract](images/graphical_abstract.png)

For more information, please refer to the [paper]().

## Installation 

### 1. Create the virtual environment

### 2. Install the dependencies

### 3. (optional) Test the installation

## Structure
The scripts are made to be able to run fast energy assessments at scale so that the potential at district level can be assessed. There is one alternative which is to automatically generate the IDF files and run EnergyPlus in batches and another one which is to use a surrogate model that is trained based on synthetic data produced by EnergyPlus simulations. 

## Code

Below you can find the directory structure along with a short explanation of the files:

```
Energy_prediction_scale
├── README.md
├── building_class
|   ├── building_class.py
|   ├── getdata_functions_building.py:
|   ├── getdata_functions_apartment.py:
|   ├── create_idf_file.py:
|   ├── modify_idf_for_simulation.py:
|   ├── get_retrofit_data.py:
├── dbn
|   ├── woon_functios.py:
|   ├── degradation_over_years.py:
|   ├── climate_change.py:
|   ├── run_energyplus.py:
|   ├── run_nn:
├── run_simulations_batches
|   ├── run_energyplus_batch.py:
|   ├── run_nn_batch.py:
├── decision_support
|   ├── visualize_data.py:
├── files
|   ├── nieman_data.csv:
|   ├── initial_woon_probs.npz:
|   ├── transitions.npz:
|   ├── retrofits.csv:
|   ├── action_costs.csv:
|   ├── blocks_kralingseveer.csv:
|   ├── bags_training.csv:
|   ├── weather_data
    |   ├── TMY_file.epw: 
```

## Training

Here we show the basic characteristics related to training and the most important features/outcome of the database.

## How to run the energy assessment
The main input is the BAG Adres ID which can be retrieved for each building address from https://bagviewer.kadaster.nl/lvbag/bag-viewer. (Enter the address and get the BAG Address)

Check that the archetype is available - if not, enter manually

Choose retrofit option / available retrofits from TABULA database

![Plot showing time over accuracy for EnergyPlus & Surrogate model]()

## Results (Decision support for retrofit planning)

Here we show some characteristic plots using the decision support system.

## Acknowledgements 
The work was produced within the framework of DE-CIST project funded by the ICLEI Action Fund and Multicare project.

## Citation
The source code in this repository is released under the MIT License. If you would like to refer to our work, please consider citing:

```
@article{
}
```

- Assessment
There are 3 main ways to run the assessments:
- `main_run_ep.py`: Runs individual energy simulations connecting to EnergyPlus v.23-2-0 (installation of the software is required locally on the computer)
- `main_run_multi.py`: Runs energy simulations in batches using parallel processing
- `main_run_surr.py`: Connects to a neural network that has been trained based on synthetic data produced by EnergyPlus

- Project structure
- `main_run_ep.py`: run one energy simulation
- `main_run_multi.py`: run multiple energy simulations using parallel processing
- `main_run_surr.py`: run energy assessments using the neural network
- `building_class.py`: initialization of building class and main functions
- `ep_nieman_tudelft_18_10.csv`: nieman database with detailed information per building
- `bag_adres_ids`: randomly selected BAG Adres IDs to use as example for 'main_run_multi.py'

Folders:

- idf_functions: functions to download data, create and modify idf files
- run_surrogate_files: files needed for the assessment via the neural network


