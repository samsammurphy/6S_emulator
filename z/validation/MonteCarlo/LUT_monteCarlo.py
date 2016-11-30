# -*- coding: utf-8 -*-
"""
LUT_monteCarlo.py, Sam Murphy (2016-11-29)

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

"""

import os
import pickle
import time
import datetime
from Py6S import *

def Landsat8_wavelengths(channel):
    channels = {
    'blue' :PredefinedWavelengths.LANDSAT_OLI_B2,
    'green':PredefinedWavelengths.LANDSAT_OLI_B3,
    'red'  :PredefinedWavelengths.LANDSAT_OLI_B4,
    'nir'  :PredefinedWavelengths.LANDSAT_OLI_B5,
    'swir1':PredefinedWavelengths.LANDSAT_OLI_B6,
    'swir2':PredefinedWavelengths.LANDSAT_OLI_B7,
    }
    return Wavelength(channels[channel])
    
def run_6S_monteCarlo(out_path, alt, channel, n):
  """
  Runs 6S over a collection of random (and some fixed) input variables
  """
  
  inputs = []
  outputs = []
  
  for i in range(0,n):
  
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
    s.wavelength = Landsat8_wavelengths(channel)
    
    # run 6S
    s.run()
    
    # format 6S outputs
    Edir = s.outputs.direct_solar_irradiance             #direct solar irradiance
    Edif = s.outputs.diffuse_solar_irradiance            #diffuse solar irradiance
    Lp   = s.outputs.atmospheric_intrinsic_radiance      #path radiance
    absorb  = s.outputs.trans['global_gas'].upward       #absorption transmissivity
    scatter = s.outputs.trans['total_scattering'].upward #scattering transmissivity
    tau2 = absorb*scatter                                #transmissivity (from surface to sensor)
    
    # append inputs and outputs to lists
    inputs.append({'doy':doy,
                   'month':month,
                   'day':day,
                   'solar_z':solar_z,
                   'H2O':H2O,
                   'O3':O3,
                   'AOT':AOT})
    
    outputs.append({'Edir':Edir,
                    'Edif':Edif,
                    'tau2':tau2,
                    'Lp':Lp})
  
  monteCarlo = {'inputs':inputs,'outputs':outputs,'n':n}
    
  return monteCarlo

def main(timeZero):
    
  # target altitude
  alt = 0
  
  # Landsat 8 channel name
  channel = 'blue'
  
  # number of runs
  n = 20000
        
  # I/O
  base_path = os.path.dirname(os.path.abspath(__file__))
  outdir = ('randomLUTs/altitude_{}').format(alt)
  out_path = os.path.join(base_path,outdir)
  if not os.path.exists(out_path):
    os.makedirs(out_path)
  os.chdir(out_path)
  
  # Monte Carlo runs of 6S
  monteCarlo = run_6S_monteCarlo(out_path, alt, channel, n)   
  
  # save to pickle file
  pickle.dump(monteCarlo, open('monteCarlo_{}.p'.format(int(timeZero)), 'wb') )  
    
if __name__ == '__main__':
  t = time.time()
  main(t)
  print('done in {} secs'.format(time.time()-t))
