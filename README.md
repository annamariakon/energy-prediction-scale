# Energy prediction at scale (Rotterdam, Netherlands)

## Short description
A set of Python scripts that provides building-level assessments for heating and cooling energy demand. The scripts are adjusted for Rotterdam (the Netherlands) and can also be used for other cities in the same country. The work was produced within the framework of DE-CIST project funded by the ICLEI Action Fund.

### photo with plots

## Get started 

### Create virtual environment

### Install dependencies

## Dataset structure
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
- epw_file: TMY file for Rotterdam/The Hague downloaded from https://climate.onebuilding.org
- idf_functions: functions to download data, create and modify idf files
- run_surrogate_files: files needed for the assessment via the neural network

## How to run the energy assessment
The main input is the BAG Adres ID which can be retrieved for each building address from https://bagviewer.kadaster.nl/lvbag/bag-viewer. (Enter the address and get the BAG Address)

Check that the archetype is available - if not, enter manually

Choose retrofit option / available retrofits from TABULA database

## Retrofit planning

