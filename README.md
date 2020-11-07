# swe4s-spt
SWE4S Project: Single Particle Tracking

**Project goal:** develop a Python-based pipeline to process single molecule movies, generate particle trajectories, and calculate properties such as diffusion coefficients and dwell times.

**Inputs**
TIF or ND2 (proprietary from NIS-Elements) movie with fluorescently labeled proteins of interest.

**Outputs**
* processed movie (background subtracted & smoothed)
* particle trajectories
* diffusion coefficients & particle dwell times 


**Updates**
* 11/06/2020:
- fixed process_image function so that it uses pims library to handle stacked tifs
* 11/05/2020:
- updated `utils` to reflect changes to calc_diffusion(), with associated testing in `test_utils.py`
- added shell script (`run.sh`) for processing ND2 files (conversion to TIF) and calculating some diffusion coefficients
* 11/04/2020:
 - created process_image function that will open a file as a numpy array and then process that file using opencv
* 11/03/2020:
  - generated code to convert ND2 to a TIF, for simplicity. Scaling looks to be a bit off compared to the original ND2, but for now it should suffice.
