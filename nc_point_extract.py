# Written by Andrew Wickert, started a little before 29 May 2012

# This is a class to obtain a time series of Nexrad reflectivity outputs at a single 
# point in space, and needs a front-end interface code to access it

"""
Copyright 2012 Andrew D. Wickert
 
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
 
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from Scientific.IO.NetCDF import NetCDFFile
import numpy as np
from matplotlib import pyplot as plt
import sys
from matplotlib.pyplot import *

class radarout(object):

  def __init__(self,xi,yi,filename,radius):
    self.filename = filename
    self.x0 = xi
    self.y0 = yi
    self.radius = radius # Search radius - may eventually limit search to within wedges
    
  def setup(self):
    self.ncfile = NetCDFFile(self.filename)
    self.reflectivity = self.ncfile.variables['Reflectivity'].getValue()[:,:360,:]

  def coordinates(self):
    # Raw inputs
    self.azimuth = self.ncfile.variables['azimuthR'].getValue()[:,:360]
    self.r = self.ncfile.variables['distanceR'].getValue()
    # We will reorder everything to this set of azimuths
    self.theta = np.arange(0.5,360.) # We will shift all of the reflectivities to match this
    self.thetarad = self.theta * np.pi/180.
    # Cartesian
    #self.x = self.r * np.cos(self.thetarad)
    #self.y = self.r * np.sin(self.thetarad)
    # Grid - get x,y at every r,theta
    self.thetarad2d, trash = np.meshgrid(self.thetarad, np.ones(len(self.r)))
    self.thetarad2d = self.thetarad2d.transpose()
    # Azimuth to polar coords - shift 0 angle and reverse direction
    #self.x = self.r * np.cos(self.thetarad2d)
    #self.y = self.r * np.sin(self.thetarad2d)
    #self.thetarad2d = 2.*np.pi - (self.thetarad2d - np.pi/2.)
    #self.x = self.r * np.cos(self.thetarad2d - np.pi/2.)
    #self.y = -1* self.r * np.sin(self.thetarad2d- np.pi/2.)
    #self.x = (-2**.5/2.) * self.r * np.cos(self.thetarad2d)
    #self.y = (-2**.5/2.) * self.r * np.sin(self.thetarad2d)
    self.y = self.r * np.cos(self.thetarad2d)
    self.x = self.r * np.sin(self.thetarad2d)

  def makeComposite(self):
    # Now do all angles and combine
    # They try to hit the half-degree, so start by assuming that they all stack
    theta_unsorted = np.round(self.azimuth*2)/2.
    # Sort and stack - checked this and I transformed everything correctly
    self.composite = np.zeros(self.reflectivity[0,:,:].shape)
    for i in range(self.reflectivity.shape[0]): #3,4):# Temporarily have it just look at one elev
      index0_5 = (theta_unsorted[i,:] == .5).nonzero()[0][0]
      ref = np.zeros(self.reflectivity[0,:,:].shape)
      ref[:len(self.theta)-index0_5,:] = self.reflectivity[i,index0_5:,:] # Beginning
      ref[len(self.theta)-index0_5:,:] = self.reflectivity[i,:index0_5,:] # End
      self.composite+=ref

  def findNearestPoints(self):
    # Find cell that is closest to the weather radar point
    # Radius in meters but dist in km
    dist = np.sqrt((self.x-self.x0)**2 + (self.y-self.y0)**2)
    self.points_selected = dist<self.radius

  def reflectivityAtLoc(self):
    refAtLoc = self.composite[self.points_selected]
    # Doesn't quite work - probably because precip and clear air (?) modes not comparable
    self.meanCompRef = np.mean(refAtLoc) / self.reflectivity.shape[0] # Mean in x,y, then divide by shape for mean in z
    return self.meanCompRef
    
  def close(self):
    # Forgot this earlier: was crashing with too many files open
    self.ncfile.close()

  def run(self):
    try:
      self.setup()
      self.coordinates()
      self.makeComposite()
      self.findNearestPoints()
      ralv = self.reflectivityAtLoc()
      self.close()
      return ralv
    except:
      print "     Maybe problem in input file? Printing variable list. If empty, problem!"
      print self.ncfile.variables
      return 'error'

  def plot(self):
    # Local variables only here
    thetarad2d, trash = np.meshgrid(self.thetarad, np.ones(len(self.r)))
    thetarad2d = thetarad2d.transpose()
    x = self.r * np.cos(thetarad2d) / 1000.
    y = self.r * np.sin(thetarad2d) / 1000.
    # Sample Z-R relationship
    rain = (composite/300)*(1./1.4)
    # Plot
    figure(1)
    contourf(x,y,rain,50,colors=None,cmap=None)
    show()



