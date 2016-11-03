# -*- coding: utf-8 -*-
"""
create_time_series.py, Sam Murphy (2016-11-03)

This is part of the 'harmonic investigation'. Essentially, it seems that critical
atmospheric correction parameters (Edir, Edif and Lp) can be well defined using
a simple harmonic function.

x = a.cos(doy / (b.pi)) + c

To test/demonstrate this I ran 6S (via Py6S) for a parameter space that include:
  - Landsat8, B2-B7 (i.e. from blue to swir2)
  - Continental and Maritime aerosol models
  - min, middle, max values for:
    * solar zenith
    * view zenith
    * water vapour column
    * ozone
    * aerosol optical thickness
    * altitude

"""

from Py6S import *
import datetime as dt
import os
import pickle
import time
from itertools import product

def define_parameter_space():
  """
  Defines the parameter space of input variables for the 6S runs that 
  will be investigated (i.e. all permutations of inputs)
  
  """
  
  # 6S input variables to investigate
  bands = [
  ('blue',PredefinedWavelengths.LANDSAT_OLI_B2),  
  ('green',PredefinedWavelengths.LANDSAT_OLI_B3),
  ('red',PredefinedWavelengths.LANDSAT_OLI_B4),
  ('nir',PredefinedWavelengths.LANDSAT_OLI_B5),
  ('swir1',PredefinedWavelengths.LANDSAT_OLI_B6),
  ('swir2',PredefinedWavelengths.LANDSAT_OLI_B7)
  ]
  aeros = [('CO',AeroProfile.Continental),('MA',AeroProfile.Maritime)]
  solar_zs = [0,30,60] # solar zenith
  view_zs = [0,30,60]  # view zenith
  H2Os = [0,4,8]       # water vapour column
  O3s  = [0,0.4,0.8]   # ozone
  AOTs = [0,1.5,3]     # aerosol optical thickness
  alts = [0,3,6]       # altitude
  
  # parameter list
  params = {'bands':bands,'aeros':aeros,'solar_zs':solar_zs,'view_zs':view_zs,
    'H2Os':H2Os,'O3s':O3s,'AOTs':AOTs,'alts':alts}

  # get all permutation of 6S input variables
  perms = product(bands,
                  aeros,
                  solar_zs,
                  view_zs,
                  H2Os,
                  O3s,
                  AOTs,
                  alts)
                       
  # result
  return (params, list(perms))
  
def run6S_thru_year(inputs):
  """
  Runs 6S over multiple days of year using all input permutations
  
  """
  # 6S object
  s = SixS()
  
  # Lambertian analysis
  s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.3)
  
  # input variables
  s.wavelength = Wavelength(inputs['band'][1])
  s.aero_profile = AeroProfile.PredefinedType(inputs['aero'][1])
  s.geometry = Geometry.User()
  s.geometry.solar_z = inputs['solz']
  s.geometry.view_z = inputs['view']
  s.atmos_profile = AtmosProfile.UserWaterAndOzone(inputs['H2O'],inputs['O3'])
  s.aot550 = inputs['AOT']
  s.altitudes.set_target_custom_altitude(inputs['alt']) 
  s.altitudes.set_sensor_satellite_level()     
  
  # loop over these dates
  months = [1,2,3,4,5,6,7,8,9,10,11,12]
  days = [4,20]  # 4th day of month used to cover perihelion and aphelion
                 # two days per month provides sufficient temporal resolution for model fit
  
  # outputs
  doys  = []
  rads  = []
  Edirs = []
  Edifs = []
  Lps   = []
  
  
  for month in months:
    for day in days:
      
      # day of year
      date = dt.date(2000,month,day) # using an abritrary year (i.e. 2000), leap year effect is negligable
      doy = date.timetuple().tm_yday
      doys.append(doy)
      
      # 6S run
      s.geometry.month = month
      s.geometry.day = day
      s.run()
      
      # extract reults
      rad = s.outputs.pixel_radiance                  # at-sensor radiance
      Edir = s.outputs.direct_solar_irradiance        # direct solar irradiance
      Edif = s.outputs.diffuse_solar_irradiance       # diffuse solar irradiance
      Lp   = s.outputs.atmospheric_intrinsic_radiance # path radiance
      
      # append to lists
      rads.append(rad)
      Edirs.append(Edir)
      Edifs.append(Edif)
      Lps.append(Lp)
      
  return(doys,rads,Edirs,Edifs,Lps)

def main():
  """
  Creates a collection of time series of 6S runs to investigate if a
  harmonic function(s) can model Edir, Edif, Lp
  """
  
  base_path = os.path.dirname(os.path.abspath(__file__))
  outpath = os.path.join(base_path,'time_series')
   
  # define the parameter space
  params, perms = define_parameter_space()  
      
  # iterate over each input permutation
  for i, perm in enumerate(perms):
  
    # time this iteration
    t = time.time()
        
    #unpack and save to inputs
    inputs = {
    'band': perm[0],  
    'aero': perm[1],
    'solz': perm[2],
    'view': perm[3],
    'H2O':  perm[4],
    'O3':   perm[5],
    'AOT':  perm[6],
    'alt':  perm[7]
    }
    
    #run 6S
    outputs = run6S_thru_year(inputs)
        
    #pickle results
    filename = 'SixS_time_series_'+str(i)+'.p'
    pickle.dump({'inputs':inputs,'outputs':outputs,'params':params},
                open(outpath+'/'+filename,"wb"))
    
    #track progress
    print('done permutation {} of {} in {:.2f} secs'.format(i,len(perms),time.time()-t))
      
if __name__ == '__main__':
  t0 = time.time()
  main()
  print('ALL DONE in {:.2f} mins'.format((time.time()-t0)/60))
