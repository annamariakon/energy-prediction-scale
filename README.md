# Energy prediction at scale (Rotterdam, Netherlands)

## Short description
A set of Python scripts that provides building-level assessments for heating and cooling energy demand. The scripts are adjusted for Rotterdam (the Netherlands) and can also be used for other cities in the same country. 

The main input is the BAG Adres ID which can be retrieved for each building address from https://bagviewer.kadaster.nl/lvbag/bag-viewer.

## Assessment
There are 3 main ways to run the assessments:
- 'main_run_ep.py': Runs individual energy simulations connecting to EnergyPlus v.23-2-0 (installation of the software is required locally on the computer)
- 'main_run_multi.py': Runs energy simulations in batches using parallel processing
- 'main_run_surr.py': Connects to a surrogate model that has been trained based on synthetic data produced by EnergyPlus

## License
