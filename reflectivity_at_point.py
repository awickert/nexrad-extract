#! /usr/bin/python

import nc_point_extract as ncr
import os
from datetime import datetime as dt
from time import strptime
from glob import glob
from matplotlib.pyplot import *
from dateutil import tz

# Should move this into an input parser, file, or getter/setter
xi = 20607.025455#21055.304288
yi = -23873.3124799998#-23429.8191499999
#filename = '/media/grasshd/nexrad/20110712/nc/KFTG20110712_000223_V03.nc'
indir = '/media/grasshd/nexrad/20110712/nc/'
radius = 500. # meters

datestamp = []
reflectivity = []

for filename in sorted(glob(indir + '/*.nc')):
  # First, parse date, crudely (b/c of good organization by NWS, shouldn't be a problem)
  basename = os.path.basename(filename)
  year, month, day = basename[4:8], basename[8:10], basename[10:12]
  hour, minute, second = basename[13:15], basename[15:17], basename[17:19]
  timestr = year + '-' + month + '-' + day + 'T' + hour + ':' + minute + ':' + second
  # And append
  datestamp.append( dt(*strptime(timestr, "%Y-%m-%dT%H:%M:%S")[:6]) )
  print datestamp[-1],
  try:
    print obj.reflectivity.shape[0]
  except:
    pass
  # Then do the radar
  obj = ncr.radarout(xi,yi,filename,radius)
  ref = obj.run()
  if ref == 'error':
    # Shoot! Remove the final time
    datestamp.pop()
  else:
    # Append reflectivity
    reflectivity.append(ref)

plot(datestamp,(np.array(reflectivity)/300)**(1/1.4) * 10)
show()
