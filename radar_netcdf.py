#! /usr/bin/python

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np
import optparse
import sys

"""
Syntax: radar_netcdf [-hvwp] --ncfile=$netcdfFileName --varname=$varname \
  [--lat=$lat] [--lon=$lon] [--outfile=$outfile] [--help]
where $lat/$lon are of the point of interest, and are optional, and $outfile
is used only if --lat and --lon are defined

Written by Andy Wickert on 17 August, 2011, to get precipitation values (or 
any value, really) out of a lat/lon cell in a NEXRAD level 3 product grid

Output of radar_netcdf --help:

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
"""


###############
## FUNCTIONS ##
###############

def mindistIndex(scalar,vector):
  """
  Provides the index value of the closest point on a vector to the input scalar
  """
  if (scalar < vector).all() or (scalar > vector).all():
    print "Input lat or lon out of range."
    sys.exit()
  else:
    dist = abs(vector-scalar)
    mindist_i = (dist == min(dist)).nonzero()
    mindist_i_s = out_of_array(mindist_i) # Pull it out of the vector
    return mindist_i_s

def out_of_array(value):
  """
  Get the value out of a single-entry numpy array
  """
  while type(value) == np.ndarray:
    value=value[0]
  return value
  

#########################
## COMMAND-LINE PARSER ##
#########################

parser = optparse.OptionParser ()

# Flags
parser.add_option("-v", action="store_true", dest="verbose", help="If selected, turns on verbosity")
parser.add_option("-w", action="store_true", dest="writeLLdata", help="Write the value at the given lat/lon to file")
parser.add_option("-p", action="store_true", dest="plotfig", help="Plots radar output")

# Inputs
parser.add_option ("--ncfile", action="store", type="string", dest="ncfile", help="NetCDF filename", default=None)
parser.add_option ("--varname", action="store", type="string", dest="varname", help="NetCDF variable to get, e.g., 'Precip1hr'", default=None)
parser.add_option ("--lat", action="store", type="float", dest="lat", help="Latitude of point to get data. Optional, default = %default",  default = None)
parser.add_option ("--lon", action="store", type="float", dest="lon", help="Longitude of point to get data. Optional, default = %default",  default = None)
parser.add_option ("--outfile", action="store", type="string", dest="outfile", help="Output file for lat/lon data on precip. Optional: only used if lat/lon are defined, default = %default.",  default = 'NEXRAD_ll_out.txt')

(opt, args) = parser.parse_args ()

##################
## MAIN PROGRAM ##
##################

if opt.verbose: print "Starting main program."

# Make sure that the appropriate inputs are provided
if opt.ncfile == None:
  print "NetCDF input file not provided; exiting."
  sys.exit()
if opt.varname == None:
  print "Name of variable to retrieve not provided; exiting."
  sys.exit()
if opt.writeLLdata or opt.plotfig:
  pass
else:
  print '  No output will be provided from this run;\n\
  please choose "-w" to write data to a file\n\
  or "-p" to create a plot (or "-wp" for both).'

# Load the netcdf file
ncfile = NetCDFFile(opt.ncfile)
if opt.verbose: print "NetCDF file loaded"

# Get lat/lon bounds
# Not made to work across 180 meridan
# To get attribute list, type "dir(ncfile)"
elon = getattr(ncfile,'geospatial_lon_max')[0]
wlon = getattr(ncfile,'geospatial_lon_min')[0]
nlat = getattr(ncfile,'geospatial_lat_max')[0]
slat = getattr(ncfile,'geospatial_lat_min')[0]
if opt.verbose:
  print "Bounding box (N, S, W, E)"
  print nlat, slat, wlon, elon, wlon

# Get the variable needed
try:
  var = ncfile.variables[opt.varname].getValue()
except:
  print "Variable name provided not recognized; exiting."
  sys.exit()

# Use lat/lon bounds to create lat/lon vectors
nlats,nlons = var.shape
lats = np.linspace(slat,nlat,nlats)
lons = np.linspace(wlon,elon,nlons)

# Data out - not done yet

if opt.writeLLdata:
  if opt.verbose: print "Recording " + str(opt.varname) + " value at " \
    + str(opt.lat) + " N, " + str(opt.lon) + " E"
  if opt.lat == None:
    print "Latitude undefined"
    sys.exit()
  elif opt.lon == None:
    print "Longitude undefined"
    sys.exit()
  else:
    if opt.outfile == 'NEXRAD_ll_out.txt':
      print "Using default output filename, 'NEXRAD_ll_out.txt'"
    # Find the closest coordinates
    # Maybe will replace in future with some sort of averaging / interpolation
    # scheme, but just testing for now
    # Also might get the time from the file
    lati = mindistIndex(opt.lat,lats)
    loni = mindistIndex(opt.lon,lons)
    outval = out_of_array(var[lati,loni])
    
    # Write to file
    outfile = open(opt.outfile, 'a')
    outstr = str(outval) + '\n'
    outfile.write(outstr)
    outfile.close()
    if opt.verbose: print 'Wrote "' + str(outval) + '" to file'
    
# Plot
if opt.plotfig:
  from matplotlib.pyplot import imshow, show, xlabel, ylabel, colorbar, title
  if opt.verbose: print "Plotting..."
  imshow(var,origin='lower',extent=(wlon, elon, slat, nlat),interpolation='nearest')
  colorbar()
  xlabel('Longitude',fontsize=16)
  ylabel('Latitude',fontsize=16)
  if opt.varname == 'Precip1hr':
    title('One-hour precipitation [accumulation?],\nhundredths of mm',fontsize=16)
  show()

if opt.verbose: print "End of program."
