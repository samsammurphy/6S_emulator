# -*- coding: utf-8 -*-
"""
LUT_build
_______________________________________________________________________________

This module builds a collection of lookup table (.lut) files for atmospheric
correction. It runs the 6S radiative transfer code in Fortran via a Python
wrapper (Py6S).


Usage
-----

runs at the command using the following syntax

$ python3 LUT_build.py {sensor} {aerosol_profile}

For example, to create LUTs for the Landsat 8 OLI sensor using
a continental aerosol profile:

$ python3 LUT_build.py LANDSAT_OLI CO


Output
------

This module saves a lookup table separately for each waveband into
a '.lut' file.

It will create the following path from the current working direcotry:

./LUTs/{sensor}_{aerosol_profile}/viewz_{view_zenith}

So, for example, the above build would be saved to:

./LUTs/LANDSAT_OLI_MA/viewz_0

"""

import os
import pickle
import sys
import time
from itertools import product

import numpy as np
from Py6S import *


# assign an aerosol profile to a 6S object
def assign_AeroProfile(s,profile):
  switch = {
  'BB':AeroProfile.BiomassBurning,
  'CO':AeroProfile.Continental,
  'DE':AeroProfile.Desert,
  'MA':AeroProfile.Maritime,
  'NO':AeroProfile.NoAerosols,
  'UR':AeroProfile.Urban
  }
  s.aero_profile = switch[profile]

# define VSWIR channels to be used
def define_channels(sensor):
  switch = {
  'LANDSAT_TM' :['B1','B2','B3','B4','B5','B7'],
  'LANDSAT_ETM':['B1','B2','B3','B4','B5','B7'],
  'LANDSAT_OLI':['B2','B3','B4','B5','B6','B7'],
  'ASTER':['B1','B2','B3B','B4','B5','B6','B7','B8','B9']
  }
  channels = switch[sensor]
  return channels
  
# get Py6S spectral filter function (i.e. a 'Wavelength')
def get_predefined_wavelength(config):
  
  if config['sensor'] == 'ASTER':
    channels = {
    'B1':PredefinedWavelengths.ASTER_B1,
    'B2':PredefinedWavelengths.ASTER_B2,
    'B3B':PredefinedWavelengths.ASTER_B3B,
    'B3N':PredefinedWavelengths.ASTER_B3N,
    'B4':PredefinedWavelengths.ASTER_B4,
    'B5':PredefinedWavelengths.ASTER_B5,
    'B6':PredefinedWavelengths.ASTER_B6,
    'B7':PredefinedWavelengths.ASTER_B7,
    'B8':PredefinedWavelengths.ASTER_B8,
    'B9':PredefinedWavelengths.ASTER_B9
    }
  
  if config['sensor'] == 'LANDSAT_TM':
    channels = {
    'B1':PredefinedWavelengths.LANDSAT_TM_B1,
    'B2':PredefinedWavelengths.LANDSAT_TM_B2,
    'B3':PredefinedWavelengths.LANDSAT_TM_B3,
    'B4':PredefinedWavelengths.LANDSAT_TM_B4,
    'B5':PredefinedWavelengths.LANDSAT_TM_B5,
    'B7':PredefinedWavelengths.LANDSAT_TM_B7,
    }
    
  if config['sensor'] == 'LANDSAT_ETM':
    channels = {
    'B1':PredefinedWavelengths.LANDSAT_ETM_B1,
    'B2':PredefinedWavelengths.LANDSAT_ETM_B2,
    'B3':PredefinedWavelengths.LANDSAT_ETM_B3,
    'B4':PredefinedWavelengths.LANDSAT_ETM_B4,
    'B5':PredefinedWavelengths.LANDSAT_ETM_B5,
    'B7':PredefinedWavelengths.LANDSAT_ETM_B7,
    }
    
  if config['sensor'] == 'LANDSAT_OLI':
    channels = {
    'B1':PredefinedWavelengths.LANDSAT_OLI_B1,
    'B2':PredefinedWavelengths.LANDSAT_OLI_B2,
    'B3':PredefinedWavelengths.LANDSAT_OLI_B3,
    'B4':PredefinedWavelengths.LANDSAT_OLI_B4,
    'B5':PredefinedWavelengths.LANDSAT_OLI_B5,
    'B6':PredefinedWavelengths.LANDSAT_OLI_B6,
    'B7':PredefinedWavelengths.LANDSAT_OLI_B7,
    'B8':PredefinedWavelengths.LANDSAT_OLI_B8,
    'B9':PredefinedWavelengths.LANDSAT_OLI_B9,
    'PAN':PredefinedWavelengths.LANDSAT_OLI_PAN
    }
  
  # return a Py6S 'Wavelength'
  return Wavelength(channels[config['channel']])

# calculates midpoints of the values in a list or array (i.e. for LUT validation)
def mid_points(values):
  
  x = np.array(values)
  mid_points = (x[1:] + x[:-1]) / 2
  
  return mid_points

# define input variables
def input_variables(build_type):
  """
  Lookup tables are build using 1) fixed parameters which are user-defined
  and passed to main() via the command line interface, and 2) a set of 
  variable parameters defined here.
  
  Variables
  ---------
  
  solar_zs = solar zenith angles (degrees)
  H2Os = water vapour columns (g/m2)
  O3s = ozone columns (cm-atm)
  AOTs = aerosol optical thicknesses
  alts = altitudes (km above sealevel)
  """
 
  test = {
  'solar_zs':[0,10,20],
  'H2Os':[0,2,3],
  'O3s':[0,0.4,0.8],
  'AOTs':[0,1.0],
  'alts':[0,2,4]
  }
  
  full = {
  'solar_zs': np.linspace(0,60,7),  
  'H2Os': [0, 0.25, 0.5, 1, 1.5, 2, 3, 5, 8.5],  
  'O3s': [0.0, 0.8],  
  'AOTs': [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.25, 3],
  'alts': [0,1,4,7.75]
  }
  # Maximum altitude is set to 7.75 km to avoid 6S's 8 km scale height. 
  # Note, only 30 mountain peaks in the world are higher than 7.75 km 
  # (https://en.wikipedia.org/wiki/List_of_highest_mountains)
  # can *probably* safely model targets >7.75 km as being at 7.75 km
  
  validation = {
  'solar_zs':mid_points(full['solar_zs']),  
  'H2Os':mid_points(full['H2Os']),  
  'O3s':mid_points(full['O3s']),  
  'AOTs':mid_points(full['AOTs']),
  'alts':mid_points(full['alts'])
  }
  # This 'validation' parameter space uses the midpoints between the 
  # normal, i.e. 'full', build because we expect it to be the toughest test.
  # Will also test using a Monte Carlo approach further down the line 
  # (we expect Monte Carlo to be an easier test, as some of the random values
  # will be closer those in 'full'.  
  
  # return user selected values
  switch = {
  '--test':test,
  '--full':full,
  '--validation':validation
  }
  variables = switch[build_type]
  return variables

def create_LUT(config,variables,filename):
  """
  Create a lookup table for a given configuration (i.e. sensor, aerosol profile
  view_z and channel) and set of input variable permutations (i.e. solar_z,
  H2O, O3, AOT and alt) 
  """
  
  # configure a 6S object
  s = SixS()
  s.altitudes.set_sensor_satellite_level()
  assign_AeroProfile(s,config['aerosol_profile'])
  s.geometry = Geometry.User()
  s.geometry.view_z = config['view_zenith']
  s.geometry.month = 1
  s.geometry.day = 4
  # Earth-sun distance correction is applied on execution of atmcorr
  # module using a harmonic function from perihelion = Jan 4th.
  
  # get permutation of input variables
  perms = list(product(variables['solar_zs'],
                       variables['H2Os'],
                       variables['O3s'],
                       variables['AOTs'],
                       variables['alts']))  
                       
  #run 6S for each permutation of input variables
  outputs = [] # output list (Edir, Edif, tau2, Lp)
  LUT = {}     # dictionary of 6S inputs, outputs and configuration
  for perm in perms:
    # print progress         
    print('{0}: solar_z = {1[0]:02}, H2O = {1[1]:.2f}, O3 = {1[2]:.1f},'
          'AOT = {1[3]:.2f}, alt = {1[4]:.2f}'.format(filename,perm))
    # update 6S object
    s.geometry.solar_z = perm[0]
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(perm[1],perm[2])
    s.aot550 = perm[3]
    s.altitudes.set_target_custom_altitude(perm[4])
    s.wavelength = get_predefined_wavelength(config)# i.e. for given sensor and channel
    
    # run 6S
    s.run()
    # extract transmissivity
    absorb  = s.outputs.trans['global_gas'].upward       #absorption transmissivity
    scatter = s.outputs.trans['total_scattering'].upward #scattering transmissivity
    #define output variables
    Edir = s.outputs.direct_solar_irradiance             #direct solar irradiance
    Edif = s.outputs.diffuse_solar_irradiance            #diffuse solar irradiance
    Lp   = s.outputs.atmospheric_intrinsic_radiance      #path radiance
    tau2 = absorb*scatter                                #transmissivity (from surface to sensor)
    #append to outputs list
    outputs.append((Edir,Edif,tau2,Lp))
  
  # pickle LUT
  LUT['inputs'] = {'config':config,'permutations':perms,'variables':variables}
  LUT['outputs'] = outputs
  pickle.dump( LUT, open(filename, 'wb') )
  
  return

def main():
  
  args = sys.argv[1:]
  
  if len(args) != 4:
    print('usage: $ python3 LUT_build.py sensor aeroprofile view_z build_type')
    sys.exit(1)

  # configuration
  config = {
  'sensor':args[0],
  'channels':define_channels(args[0]),
  'aerosol_profile':args[1],
  'view_zenith':int(args[2]),
  'build_type':args[3]
  }
  
  try:
    variables = input_variables(config['build_type'])
  except:
    print('unknown build type: '+config['build_type'])
    sys.exit(1)
  
  # output directory based on user configuration
  base_path = os.path.dirname(os.path.abspath(__file__))
  outdir = ('LUTs/{0[sensor]}_{0[aerosol_profile]}/'
  'viewz_{0[view_zenith]}').format(config)
  out_path = os.path.join(base_path,outdir)
  
  # validation directory (if selected)
  if config['build_type'] == '--validation':
    out_path = os.path.join(base_path,'validation',outdir)
  
  # move to output directory
  if not os.path.exists(out_path):
    os.makedirs(out_path)
  os.chdir(out_path)
  
  # time check
  time0 = time.time()
  
  #run for each channel separately
  for channel in config['channels']:
    
    config['channel'] = channel
          
    # LUT filename
    filename = ('{0[sensor]}_{0[aerosol_profile]}_{0[view_zenith]}_'
                '{0[channel]}.lut').format(config)
    
    if os.path.isfile(filename):
      print('LUT file already exists, skipping build for: '+filename)
    else:
      print('Building LUT: '+filename)
      create_LUT(config,variables,filename)      
      
  # time check (cumulative)
  T = time.time() - time0
  print('cumulative time: {:.1f} secs, {:.1f} mins,'
  '{:.1f} hours'.format(T,T/60,T/3600) )

if __name__ == '__main__':
  main()
