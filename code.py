#! /usr/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import metpy as mp
from metpy.units import units
from metpy.plots import SkewT

s1 = pd.read_csv('data/RICARDO_001_TSPOTINT_DGF20220425_2024UTC.txt',comment='#',sep = '\s+',decimal=',')
s2 = pd.read_csv('data/RICARDO_002_TSPOTINT_DGF20220426_2034UTC.txt',comment='#',sep = '\s+',decimal=',')

s1 = s1.drop([1783,1784])

### Parte a ####

def removeOutliers(array,tol = 10):
  diff = np.diff(array)
  maxdiffIdx = diff.argmax()
  
  if diff[maxdiffIdx] > tol:
    new_array = np.delete(array,maxdiffIdx+1)
    
    return removeOutliers(new_array,tol)
  
  else:
    return array

def scale_X_axis(skew,array,tol = 10):
  if isinstance(array,mp.units.units.Quantity):
    array = array.magnitude
  
  array = removeOutliers(array,tol)
   
  axmin = (array.min() - 5).round(-1)
  axmax = (array.max() + 5).round(-1)
  skew.ax.set_xlim(axmin,axmax)

def plot_skewT(df,xlim = [],xlabel=None,ylabel=None,output=None,size=None):
  p = df['Press'].values * units.hPa
  T = df['Temp'].values * units.degC
  HR = df['RelHum'].values * units.percent
  #wind_speed = df['WSpeed'].values * units.meter_per_second
  #wind_dir = df['WDirn'].values * units.degree_north
  #u,v = mp.calc.wind_components(wind_speed.to('knot'),wind_dir)

  # Calculamos la T. punto de rocio
  Td = mp.calc.dewpoint_from_relative_humidity(T,HR)
  
  if size == None:
    size = (9,9)

  fig = plt.figure(figsize = size)
  skew = SkewT(fig, rotation=45)

  skew.plot(p,T,'black')
  skew.plot(p,Td,'blue')
  
  skew.plot_dry_adiabats()
  skew.plot_moist_adiabats()
  skew.plot_mixing_lines()
  
  if xlim != []:
    skew.ax.set_xlim(*xlim)
  else:
    scale_X_axis(skew,mp.units.concatenate([T,Td]))
  
  if xlabel != None:
    skew.ax.set_xlabel(xlabel)
    
  if ylabel != None:
    skew.ax.set_ylabel(ylabel)
  
  
  
  if output != None:
    plt.savefig(output)
  else:
    plt.show()
    
###
   
plot_skewT(s1,[-60,30], '°C','hPa','skweT_25.png',(8,7.5))
plot_skewT(s2,[-20,30], '°C','hPa','skweT_26.png')
    
    
#######################

def plus360(x):
  if x < 180:
    return x + 360
  else:
    return x
  
w = np.array([plus360(x) for x in wind_dir.magnitude])


###

Tpe = mp.calc.equivalent_potential_temperature(p,T,Td)

precipWater = mp.calc.precipitable_water(p,Td)

###

fig = plt.figure(figsize = (27,9))
skew1 = SkewT(fig, rotation=0,subplot=(1,3,1),aspect='auto')
skew2 = SkewT(fig, rotation=0,subplot=(1,3,2),aspect='auto')
skew3 = SkewT(fig, rotation=0,subplot=(1,3,3),aspect='auto')
skew = SkewT(fig, rotation=0,aspect='auto')

skew.plot(p,T,'black')
skew.plot(p,Td,'blue')
skew1.plot(p,wind_speed.magnitude,'black')
skew2.plot(p,w,'blue')
skew3.plot(p,Tpe.magnitude,'red')

###

ls = np.linspace(np.log(p.magnitude.max()),np.log(p.magnitude.min()),20)
ls_exp = np.exp(ls)
barbs_rows_idx = [np.absolute(p-i).argmin() for i in np.linspace(p.max(),p.min(),11)]

skew.plot_barbs(p[barbs_rows_idx],u[barbs_rows_idx],v[barbs_rows_idx], xloc=1.1)
skew.ax.set_ylim(1000,100)



scale_X_axis(skew1,wind_speed)
scale_X_axis(skew2,w * units.degreesN)
scale_X_axis(skew3,Tpe)


plt.show()

####

mp.calc.mixed_layer_cape_cin(p,T,Td)
mp.calc.most_unstable_cape_cin(p,T,Td)

len(p)
non_dups = np.concatenate(([True], np.diff(p) != 0))
