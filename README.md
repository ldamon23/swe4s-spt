# swe4s-spt
SWE4S Project: Single Particle Tracking

**Project goal:** develop a Python-based pipeline to process single molecule movies, generate particle trajectories, and calculate properties such as diffusion coefficients and dwell times.

**Inputs**
TIF or ND2 (proprietary from NIS-Elements) movie with fluorescently labeled proteins of interest.

**Outputs**
* feature overlay movie (extracted features are drawn to frames)
* processed movie
* particle trajectories
* diffusion coefficients & particle dwell times 


**Updates**

* Week of 11/23/2020:
 - generated function for calculating particle dwell time, and for getting particle xy coordinates
 - updated testing to be more robust
 - wrote scripts to plot diffusion and dwell time data
 
* 11/09/2020
- improved documentation and imports using guidance from project review and removed unused variables in the cv functions
* 11/07/2020
- fixed testing for process_image by adding a directory creation for out/ and re-developed process_frame output file as a tif stack instead of multiple .pngs
* 11/06/2020:
- fixed process_image function so that it uses pims library to handle stacked tifs
* 11/04/2020:
 - created process_image function that will open a file as a numpy array and then process that file using opencv
* 11/03/2020:
 - generated code to convert ND2 to a TIF, for simplicity. Scaling looks to be a bit off compared to the original ND2, but for now it should suffice.
  
 
