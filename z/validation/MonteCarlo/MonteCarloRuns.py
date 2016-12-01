# -*- coding: utf-8 -*-
"""
MonteCarloRuns.py, Sam Murphy (2016-11-30)

Run 6S for a random selection of input variables:
  - day of year (doy)
  - solar zenith angle (solar_z)
  - water vapour (H2O)
  - ozone (O3)
  - aerosol optical thickness (AOT)

as well as over a few fixed variables:
  - target altitude (sea-level)
  - wavebands (landsat oli)
  - aerosol profile (continental)
  - view zenith (0)

and save the percentage difference (pd) between 
i) true surface reflectance and
ii) model surface reflectance

model SR is calculated as follows: 
  6S forward model from true SR to at-sensor radiance, then using iLUT inverse 
  model from at-sensor radiance to model SR.
  
"""

import sys
import os
import pickle
import time
import datetime
import math
import random
import numpy as np
from Py6S import *

def Landsat8_channels(name, bandnum=False, wavelength=False):
  
  if bandnum:
    switch = {
              'blue' :'B2',
              'green':'B3',
              'red'  :'B4',
              'nir'  :'B5',
              'swir1':'B6',
              'swir2':'B7'}
  
  if wavelength:
    switch = {
              'blue' :Wavelength(PredefinedWavelengths.LANDSAT_OLI_B2),
              'green':Wavelength(PredefinedWavelengths.LANDSAT_OLI_B3),
              'red'  :Wavelength(PredefinedWavelengths.LANDSAT_OLI_B4),
              'nir'  :Wavelength(PredefinedWavelengths.LANDSAT_OLI_B5),
              'swir1':Wavelength(PredefinedWavelengths.LANDSAT_OLI_B6),
              'swir2':Wavelength(PredefinedWavelengths.LANDSAT_OLI_B7)
    }
    
  return switch[name]

def forward_model(ref,SixS_output):
  """
  Forward model takes true surface reflectance and atmospheric conditions 
  (i.e. 6S outputs: Edir, Edif, tau2 and Lp) to calculate at-sensor radiance
  
  """

  Edir = SixS_output['Edir']
  Edif = SixS_output['Edif']
  tau2 = SixS_output['tau2']
  Lp   = SixS_output['Lp']

  # at-sensor radiance  
  return ref*tau2*(Edir + Edif)/np.pi + Lp
  

def inverse_model(rad,iLUT_output, doy):
  """
  Inverse model takes at-sensor radiance and converts to model surface
  reflectance. It takes the inputs that 6S used to produce the 
  outputs that were used in the forward model. However, this time, we use
  an iLUT to estimate the 6S outputs, and use these estimated outputs to invert
  from at-sensor radiance to surface reflectance.
  """
  
  # iLUT outputs at perihelion (Jan 4th)
  Edir = iLUT_output[0]
  Edif = iLUT_output[1]
  tau2 = iLUT_output[2]
  Lp   = iLUT_output[3]

  # elliptical orbit correction (ie. function of day-of-year)
  def elliptical_correction(doy, Edir, Edif, Lp):
    
      # harmonic correction coefficient
      a = 0.03275
      b = 18.992
      c = 0.968047
      coeff =  a*np.cos(doy/(b*math.pi)) + c
     
      # correct for orbital eccentricity
      Edir = Edir*coeff
      Edif = Edif*coeff
      Lp   = Lp*coeff
      
      return Edir, Edif, Lp

  # corrected values
  Edir, Edif, Lp = elliptical_correction(doy, Edir, Edif, Lp)
  
  # model surface_reflectance
  model_ref = np.pi*(rad-Lp) / (tau2*(Edir+Edif))  
 
  return model_ref
    
def performance_statistics(iLUT, doy, ins, outs, refs):
  """
  Performace of iLUT is measured by 'dref' which is the difference in the model 
  surface reflectance from the true surface reflectance. 
  
  The model surface reflectance is derived by inverting at-sensor radiance. The
  at-sensor radiance is calculated using 6S and inputs that we define. Therefore,
  if the inversion behaves exactly like 6S, then the true and model surface 
  reflectances will be exactly the same. However, there will be differences 
  because the model is derived using an iLUT as opposed to 6S inverison.
  
  In essence, we are saying "in the case that we know exactly how 6S will 
  behave what does the iLUT do?"
  """
  
  pstats = []
  
  for ref in refs:
  
    # 6S outputs
    SixS_output = outs
    
    # iLUT-estimated 6S outputs
    iLUT_output = iLUT(ins['solar_z'], ins['H2O'], ins['O3'], ins['AOT'], 0) 
    #                                                                     ^
    #                                                                     |
    #                                  this '0' is target altitude at sea-level 
    
    # forward and inverse models
    radiance  = forward_model(ref,SixS_output)
    model_ref = inverse_model(radiance,iLUT_output, doy)  
    
    # stats
    dref = model_ref - ref
    #pd = 100*dref/ref
    
    # add to dictionary
    pstats.append(dref)
  
  return pstats
    
def run_6S_monteCarlo(iLUT, channel, n):
  """
  Runs 6S over a collection of randomized (and some fixed) input variables
  and calculates stats on iLUT performance
  """
  
  inputs = []
  outputs = []
  stats = []
  
  for i in range(0,n):
    
    # progress report
    print('{} of {}'.format(i+1,n))
  
    # random variables
    doy = random.randint(1,366)   # integer between 1-366
    solar_z = random.random()*60  # float between 0-60
    H2O = random.random()*3 + 1   # float between 1-4 
    O3 = random.random()*0.4 + 0.2# float between 0.2-0.6
    AOT = random.random()*2       # float between 0-2
    
    # convert doy to month-day
    date = datetime.datetime(2000, 1, 1) + datetime.timedelta(doy - 1)
    month = date.month
    day = date.day
          
    # 6S object configuration
    s = SixS()
    s.altitudes.set_sensor_satellite_level()
    s.aero_profile = AeroProfile.Continental
    s.geometry = Geometry.User()
    s.geometry.view_z = 0
    s.geometry.month = month
    s.geometry.day = day
    s.geometry.solar_z = solar_z
    s.atmos_profile = AtmosProfile.UserWaterAndOzone(H2O,O3)
    s.aot550 = AOT
    s.altitudes.set_target_custom_altitude(0)
    s.wavelength = Landsat8_channels(channel,wavelength=True)
    
    # run 6S
    s.run()
    
    # format 6S outputs
    Edir = s.outputs.direct_solar_irradiance             #direct solar irradiance
    Edif = s.outputs.diffuse_solar_irradiance            #diffuse solar irradiance
    Lp   = s.outputs.atmospheric_intrinsic_radiance      #path radiance
    absorb  = s.outputs.trans['global_gas'].upward       #absorption transmissivity
    scatter = s.outputs.trans['total_scattering'].upward #scattering transmissivity
    tau2 = absorb*scatter                                #transmissivity (from surface to sensor)
    
    # input/output dictionaries 
    ins = {'doy':doy,
           'month':month,
           'day':day,
           'solar_z':solar_z,
           'H2O':H2O,
           'O3':O3,
           'AOT':AOT}
    
    outs = {'Edir':Edir,
            'Edif':Edif,
            'tau2':tau2,
            'Lp':Lp}
    
    # performance statistics
    refs = np.linspace(0.05,0.5,10) # reflectance range
    pstats = performance_statistics(iLUT, doy, ins, outs, refs)

    # append to lists
    inputs.append(ins)
    outputs.append(outs)
    stats.append(pstats)

    
  monteCarlo = {'inputs':inputs,'outputs':outputs,'stats':stats,'refs':refs}  

  return monteCarlo

def saveToFile(file_dir, channel, monteCarlo):
  """
  Saves..
  1) input/outputs (for future reference, filtering, etc.)
  2) performance statistics
  ..separately for reduced file sizes and loading times  
  """
  
  # extract 6S input/outputs
  SixS_IO = {}
  SixS_IO['inputs'] = monteCarlo['inputs']
  SixS_IO['outputs'] = monteCarlo['outputs']
  
  # extract performance statistics
  stats = np.array(monteCarlo['stats'])# convert to array for smaller file size
  refs = monteCarlo['refs']

  # create output directories
  SixS_IO_dir = os.path.join(file_dir,('SixS_IO/{}').format(channel))
  if not os.path.exists(SixS_IO_dir):
    os.makedirs(SixS_IO_dir)
  stats_dir = os.path.join(file_dir,('stats/{}').format(channel))
  if not os.path.exists(stats_dir):
    os.makedirs(stats_dir)

  # full output path (filenames based on integer time)
  t = int(time.time())
  SixS_IO_out = os.path.join(SixS_IO_dir,'SixS_IO_{}.p'.format(t))
  stats_out = os.path.join(stats_dir,'stats_{}.p'.format(t))
  
  # pickle
  pickle.dump(SixS_IO, open(SixS_IO_out, 'wb'))  
  pickle.dump((stats,refs), open(stats_out, 'wb'))  
  
def main():
  
  # read user-defined variable
  args = sys.argv[1:]
  if len(args) != 1:
    print('usage: $ python3 MonteCarloRuns.py Landsat8_channel_name')
    sys.exit(1)
  
  # check it is a valid Landsat 8 channel name
  channel = args[0]
  if not channel in ['red','green','blue','nir','swir1','swir2']:
    print('channel not recognized: {}'.format(channel))
    sys.exit(1)
    
  # Landsat 8 channel name
  # channel = 'red'
  
  # number of runs
  n = 25000
          
  # load interpolated look up table
  file_dir = os.path.dirname(os.path.abspath(__file__)) 
  base_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_dir)))
  iLUT_dir = os.path.join(base_dir,'iLUTs','LANDSAT_OLI_CO','viewz_0')
  fid = 'LANDSAT_OLI_CO_0_'+Landsat8_channels(channel,bandnum=True)
  iLUT_path = os.path.join(iLUT_dir,fid+'.ilut')
  iLUT = pickle.load(open(iLUT_path,"rb"))

  # run MonteCarlo experiment
  monteCarlo = run_6S_monteCarlo(iLUT, channel, n) 

  # save to file  
  saveToFile(file_dir, channel, monteCarlo)
      
if __name__ == '__main__':
  t0 = time.time()
  main()
  print('done in {} mins'.format((time.time()-t0)/60))
