# nexrad-extract
 Extract data from NEXRAD Doppler Radar NetCDFs

A Python tool for extracting and/or plotting data from the NEXRAD (WSR-88D) Doppler weather radar network operated by the US National Weather Service. This can be used for inputs to models that require a meteorologic component.
 
 The basic command-line options are as follows:
 ```
  Options:
   -h, --help         show this help message and exit
   -v                 If selected, turns on verbosity
   -w                 Write the value at the given lat/lon to file
   -p                 Plots radar output
   --ncfile=NCFILE    NetCDF filename
   --varname=VARNAME  NetCDF variable to get, e.g., 'Precip1hr'
   --lat=LAT          Latitude of point to get data. Optional, default = none
   --lon=LON          Longitude of point to get data. Optional, default = none
   --outfile=OUTFILE  Output file for lat/lon data on precip. Optional: only
                      used if lat/lon are defined, default = NEXRAD_ll_out.txt.
 ```
 
 For more information, see http://csdms.colorado.edu/wiki/Model:NEXRAD-extract.
