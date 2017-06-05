# -*- coding: utf-8 -*-
"""
LUT_build.py, Sam Murphy (2017-04-26)

Builds a collection of lookup tables (LUT) for atmospheric correction. 
______________________________________________________________________

Purpose: Radiative transfer (RT) code is computationally expensive. 
Lookup tables can be used to create an emulator of radiative transfer 
code that is much more efficient.

This module runs the 6S radiative transfer code via a Python wrapper, 
Py6S: https://github.com/robintw/Py6S

WARNING! It takes a long time to build look up tables (typically hours),
i.e. there is a trade off between fast execution and long set-up time,
fortunately this repo comes with a bunch of pre-built LUTs to save time.

Usage
------

$ python3 LUT_build.py {options}

{options} include:

--channel     : name of predefined sensor channel, see..
              : https://github.com/robintw/Py6S/blob/master/Py6S/Params/wavelength.py
              : includes most Earth Observing satellites launched by space agencies

--wavelength  : a scalar (central) or a pair (min, max) wavelength value(s) in microns

--filter      : a spectral filter function (only valid if wavelength pair defined)

--aerosol     : aerosol profile to use (default = Continental), for options see..
              : https://github.com/robintw/Py6S/blob/master/Py6S/Params/aeroprofile.py

--build_type  : defines parameter space of input variables (default = test)
              : options are: test, test2, validation and full
              : ! MUST use full to build functioning LUT but this can take hours !

Example Usage
-------------

1) a central wavelength of 0.42 microns:

  $ python3 LUT_build.py --wavelength 0.42

2) a wavelength range from 0.42 to 0.72 microns

  $ python3 LUT_build.py --wavelength 0.42 0.72

3) a wavelength range from 0.42 to 0.43 with a spectral filter function (must be 2.5 nm internals)

  $ python3 LUT_build.py --wavelength 0.42 0.43 --filter [0.1, 0.8, 0.95, 0.87, 0.05]

4) Sentinel 2, channel 1

  $ python3 LUT_build.py --channel S2A_MSI_01

5) Landsat 8, channel 1

  $ python3 LUT_build.py --channel LANDSAT_OLI_B8

6) Build a full LUT for Sentinel 2, channel 1

  $ py LUT_build.py --channel S2A_MSI_01 --build_type full
  
"""

import os
import sys
import argparse
import time
import numpy as np
import math
from itertools import product
import pickle
from Py6S import *

def mid_points(elements):
  x = np.array(elements)
  return (x[1:] + x[:-1]) / 2

def input_variables(build_type):
  """
  Defines the input variables (i.e. parameter space) for
  a given build_type
  
  The input variables are:
  - solar zenith angle (degrees)
  - water vapour column (g/m2)
  - ozone column (cm-atm)
  - aerosol optical thickness
  - altitude (km above sealevel)
  """
 
  test = {
    'solar_zs':[0],
    'H2Os':[0],
    'O3s':[0],
    'AOTs':[0],
    'alts':[0]
  }
  
  test2 = {
    'solar_zs':[0,10,20],
    'H2Os':[0,2,3],
    'O3s':[0,0.4,0.8],
    'AOTs':[0,1.0],
    'alts':[0,2,4]
  }
  
  full = {
    'solar_zs': [0, 10, 20, 30, 40, 50, 60, 65, 70, 75],  
    'H2Os': [0, 0.25, 0.5, 1, 1.5, 2, 3, 5, 8.5],  
    'O3s': [0.0, 0.8],  
    'AOTs': [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.25, 3],
    'alts': [0,1,4,7.75]
  }
  # Maximum altitude is set to 7.75 km to avoid 6S's 8 km scale height. 
  # Note, only 30 mountain peaks in the world are higher than 7.75 km:
  # https://en.wikipedia.org/wiki/List_of_highest_mountains
  # and can probably safely model targets >7.75 km as being at 7.75 km
  
  validation = {
    'solar_zs':mid_points(full['solar_zs']),  
    'H2Os':mid_points(full['H2Os']),  
    'O3s':mid_points(full['O3s']),  
    'AOTs':mid_points(full['AOTs']),
    'alts':mid_points(full['alts'])
  }
  # This 'validation' parameter space uses the midpoints between the 
  # normal, i.e. 'full', build because we expect it to be the toughest test.
  # We also test using a Monte Carlo approach (an easier test).

  build_selector = {
    'test':test,
    'test2':test2,
    'validation':validation,
    'full':full    
  }

  return build_selector[build_type]

def permutate_invars(invars):
  """
  permutation of input variables for LUT
  """
  return list(product(invars['solar_zs'],
                      invars['H2Os'],
                      invars['O3s'],
                      invars['AOTs'],
                      invars['alts']))  

def build_LUT(config):
  """
  Builds a lookup table for a given configuration
  """

  # initiate 6S object with constants
  s = SixS()
  s.altitudes.set_sensor_satellite_level()
  s.aero_profile = AeroProfile.__dict__[config['aerosol_profile']]
  s.geometry = Geometry.User()
  s.geometry.view_z = config['view_zenith']
  s.geometry.month = 1 # Earth-sun distance correction is later
  s.geometry.day = 4   # applied from perihelion, i.e. Jan 4th.

  # calculate permutation of input variables
  perms = permutate_invars(config['invars']) 
                       
  #run 6S for each permutation
  outputs = []
  for perm in perms:      
    print('{0}: solar_z = {1[0]:02}, H2O = {1[1]:.2f}, O3 = {1[2]:.1f},'
          'AOT = {1[3]:.2f}, alt = {1[4]:.2f}'.format(config['filename'],perm))
    
    # update input variables
    s.geometry.solar_z = perm[0]
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(perm[1],perm[2])
    s.aot550 = perm[3]
    s.altitudes.set_target_custom_altitude(perm[4])
    s.wavelength = config['spectrum']
    
    # run 6S
    s.run()
    
    # solar irradiance
    Edir = s.outputs.direct_solar_irradiance             # direct solar irradiance
    Edif = s.outputs.diffuse_solar_irradiance            # diffuse solar irradiance
    E = Edir + Edif                                      # total solar irraduance
    # transmissivity
    absorb  = s.outputs.trans['global_gas'].upward       # absorption transmissivity
    scatter = s.outputs.trans['total_scattering'].upward # scattering transmissivity
    tau2 = absorb*scatter                                # transmissivity (from surface to sensor)
    # path radiance
    Lp   = s.outputs.atmospheric_intrinsic_radiance      # path radiance
    
    # correction coefficients for this configuration
    # i.e. surface_reflectance = (L - a) / b,
    #      where, L is at-sensor radiance
    a = Lp
    b = (tau2*E)/math.pi
    outputs.append((a,b))
  
  # LUT built! save to pickle file =)
  LUT = {'config':config,'outputs':outputs}
  pickle.dump( LUT, open(config['filepath'], 'wb') )
  
  return

def IO_handler(config,args):
  """
  Handles output directory and filename
  """
      
  # user-defined wavelength filename
  filename = []
  if args.wavelength:
    filename.append('wavelength_')
    filename.append('_'.join(args.wavelength))
  if args.filter:
    filename.append('_f')
  filename = ''.join(filename)
  
  # predefined sensor channel filename
  if args.channel:
    filename = args.channel
  
  # sensor name
  if args.channel:
    sensor_name = '_'.join(filename.split('_')[:-1])
  else:
    sensor_name = 'user-defined-sensor'

  # outdir
  base_path = os.path.dirname(os.path.abspath(__file__))
  outdir = os.path.join(base_path,'files','LUTs',sensor_name,
  config['aerosol_profile'],'view_zenith_{}'.format(config['view_zenith']))
  if not os.path.exists(outdir):
    print('\nCreating new output directory!\n'+outdir+'\n')
    os.makedirs(outdir)
  os.chdir(outdir)

  # update config
  config['outdir'] = outdir
  config['filename'] = filename+'.lut'
  config['filepath'] = os.path.join(outdir,filename+'.lut')

  return 
  
def main():
  
  # parse arguments
  parser = argparse.ArgumentParser() 
  parser.add_argument('--channel','-c')
  parser.add_argument('--wavelength','-w', nargs='*')
  parser.add_argument('--filter','-f', nargs='*')
  parser.add_argument('--aerosol','-a')
  parser.add_argument('--build_type','-b')
  args = parser.parse_args()
  channel = args.channel
  wavelength = args.wavelength
  spectral_filter = args.filter
  aerosol_profile = args.aerosol
  build_type = args.build_type
  
  # user-defined wavelengths
  if wavelength:
    
    if len(wavelength) > 2:
      print('wavelength can be scalar or 2-tuple only, was given wavelength: ',wavelength)
      sys.exit(1)

    start_wavelength = float(wavelength[0])
    
    if len(wavelength) == 2:
      end_wavelength = float(wavelength[1])
      
      # (optional) spectral filter function
      if spectral_filter:
        # sampling must be in 2.5 nm intervals (i.e. 0.0025 microns)
        n = (end_wavelength - start_wavelength) / 0.0025 + 1
        l = len(spectral_filter)
        if abs(l-n) > 1e-6:
          print('Filter must be in 2.5 nm intervals, expected {} samples, got {}'.format(round(n),l))
          sys.exit(1)
        else:
          spectrum = Wavelength(start_wavelength,end_wavelength=end_wavelength,filter=spectral_filter)
      else:
        spectrum = Wavelength(start_wavelength,end_wavelength=end_wavelength)
    else:
      spectrum = Wavelength(start_wavelength)


  # predefined sensor channel, for complete list see Py6S 'PredefinedWavelengths':
  # https://github.com/robintw/Py6S/blob/master/Py6S/Params/wavelength.py
  if channel:
    try:
      spectrum = Wavelength(PredefinedWavelengths.__dict__[channel])
    except:
      print('Satellite sensor channel not recognized: ',channel)
      sys.exit(1)

  # check wavelength or sensor channel spectrum was successfully assigned
  try:
    spectrum
  except NameError:
    print('must define wavelength(s) or sensor channel, returning..')
    sys.exit(1)

  # aerosol profile (default to Continental)
  if aerosol_profile:
    try:
      test = AeroProfile.__dict__[aerosol_profile]
    except:
      print('Aerosol profile not recognized: ',aerosol_profile)
      sys.exit(1)
  else:
    aerosol_profile = 'Continental'
  
  # build type (default to smallest test build)
  if build_type:
    if build_type not in ['test','test2','full','validation']:
      print('Build type not recognized: ',build_type)
      sys.exit(1)
  else:
    print('\nBuild type not defined!  .. will use test build ..\n')
    build_type = 'test'

  # configuration for this build
  config = {
  'spectrum':spectrum,
  'aerosol_profile':aerosol_profile,
  'view_zenith':int(0),
  'build_type':build_type,
  'invars':input_variables(build_type)
  }
   
  # handle output directory and filename
  IO_handler(config, args)
  
  # time check
  time0 = time.time()
  
  # BUILD the look up table!
  if os.path.isfile(config['filepath']):
    print('LUT file already exists, skipping build for: '+config['filepath'])
  else:
    print('Building LUT:\n'+config['filepath'])
    build_LUT(config)
    # .. this might take a while ..
      
  # time check
  T = time.time() - time0
  print('time: {:.1f} secs, {:.1f} mins,{:.1f} hours'.format(T,T/60,T/3600) )

if __name__ == '__main__':
  main()
