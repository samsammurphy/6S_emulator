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
  - target altitude (user-defined)
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

import os
import pickle
import time
import datetime
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
  

def inverse_model(rad,iLUT_output):
  """
  Inverse model takes at-sensor radiance and converts to 'surface
  reflectance'. It takes the inputs that 6S used to produce the 
  outputs that were used in the forward model. However, this time, we use
  an iLUT to estimate the 6S outputs, and use these estimated outputs to invert
  from at-sensor radiance to surface reflectance.
  """
  
  Edir = iLUT_output[0]
  Edif = iLUT_output[1]
  tau2 = iLUT_output[2]
  Lp   = iLUT_output[3]
  
  # surface_reflectance
  return np.pi*(rad-Lp) / (tau2*(Edir+Edif))  
    
def performance_statistics(iLUT,ins,outs):
  
  pstats = {}
  
  for ref in np.linspace(0.05,0.5,10):
  
    # 6S outputs
    SixS_output = outs
    
    # iLUT-estimated 6S outputs
    iLUT_output = iLUT(ins['solar_z'], ins['H2O'], ins['O3'], ins['AOT'], ins['alt'])
    
    # forward and inverse models
    radiance  = forward_model(ref,SixS_output)
    model_ref = inverse_model(radiance,iLUT_output)  
    
    # stats
    dref = model_ref - ref
    pd = 100*dref/ref
    
    # add to dictionary
    pstats[ref] = (dref, pd)
  
  return pstats
    
def run_6S_monteCarlo(iLUT, alt, channel, n):
  """
  Runs 6S over a collection of randomized (and some fixed) input variables
  and calculate stats on how well iLUT performs
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
    s.altitudes.set_target_custom_altitude(alt)
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
           'AOT':AOT,
           'alt':alt}
    
    outs = {'Edir':Edir,
            'Edif':Edif,
            'tau2':tau2,
            'Lp':Lp}
    
    # performance statistics
    pstats = performance_statistics(iLUT,ins,outs)

    # append to lists
    inputs.append(ins)
    outputs.append(outs)
    stats.append(pstats)

    
  monteCarlo = {'inputs':inputs,'outputs':outputs,'stats':stats,'n':n}

  return monteCarlo

def main():
  t = time.time()
  
  # target altitude
  alt = 0
  
  # Landsat 8 channel name
  channel = 'red'
  
  # number of runs
  n = 20000
          
  # load interpolated look up table
  file_dir = os.path.dirname(os.path.abspath(__file__)) 
  base_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_dir)))
  iLUT_dir = os.path.join(base_dir,'iLUTs','LANDSAT_OLI_CO','viewz_0')
  fid = 'LANDSAT_OLI_CO_0_'+Landsat8_channels(channel,bandnum=True)
  iLUT_path = os.path.join(iLUT_dir,fid+'.ilut')
  iLUT = pickle.load(open(iLUT_path,"rb"))
  
  # create output directory
  out_dir = os.path.join(file_dir,('runs/alt_{}/{}').format(alt,channel))
  if not os.path.exists(out_dir):
    os.makedirs(out_dir)
  os.chdir(out_dir)
  
  # Monte Carlo runs of 6S
  monteCarlo = run_6S_monteCarlo(iLUT, alt, channel, n)   
   
  # done
  pickle.dump(monteCarlo, open('monteCarlo_{}.p'.format(int(t)), 'wb') )  
  print('done in {} secs'.format(time.time()-t))
    
if __name__ == '__main__':
  main()
  
