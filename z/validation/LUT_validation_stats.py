# -*- coding: utf-8 -*-
"""

'LUT_validation_stats.py', Sam Murphy (2016-11-18)

Initial validation of the iLUT approach to atmospheric correction.

The LUTs define a discrete parameter space that the iLUTs interpolate between.
This raises the question: 'How do we know if this interpolation is reasonable?'

To answer this question (at least initially) we have defined a set of parameter
values that are as far away as possible (i.e. in the middle) of the increments
used to create the LUTs (and iLUTs). The idea being that these would be the 
'most difficult' points for the iLUT to estimate.

The validation parameter space was create by setting the --validation key to
the 'LUT_build.py' module.

Statistics are in terms of how well the iLUT can calculate surface
reflectance of a Lambertian surface
"""


import os
import glob
import sys
import pickle
import numpy as np


def simple_stats(array):
  return (np.mean(array),np.std(array),np.min(array),np.max(array))  
  
def parameter_stats(true,interp):
  """
  Statistics of the atmcorr parameters (i.e. Edir, Edif, tau2, Lp)
  """
  
  #percentage difference of the parameters
  percent_diff = 100*(interp-true)/true
  
  #statistics on  of
  stats = {
  'percent_diff': percent_diff,
  'Edir': simple_stats(percent_diff[:,0]),# direct solar irradiance
  'Edif': simple_stats(percent_diff[:,1]),# diffuse solar irradiance
  'tau2': simple_stats(percent_diff[:,2]),# transmissivity from surface to sensor
  'Lp'  : simple_stats(percent_diff[:,3]) # path radiance
  }
  return stats
  
def reflectance_stats(true,interp):
  """
  Statistics of the atmcorr product (i.e. surface reflectance)
  """
  
  def at_sensor_radiance(ref,Edir,Edif,tau2,Lp):
    return ref*tau2*(Edir + Edif)/np.pi + Lp
  
  def surface_reflectance(rad,Edir,Edif,tau2,Lp):
    return np.pi*(rad-Lp) / (tau2*(Edir+Edif))
  
  #'standard' Lambertian surface with reflectance of 0.1
  ref = 0.1
  
  #true at-sensor radiance for standard surface
  true_rad = at_sensor_radiance(ref,true[:,0],true[:,1],true[:,2],true[:,3])
  
  #interpolated reflectance value
  interp_ref = surface_reflectance(true_rad,interp[:,0],interp[:,1],interp[:,2],interp[:,3])
  
  #percentage difference from standad reflectance
  pd = 100*(interp_ref-ref)/ref
  
  #ignore NaNs
  pd = pd[np.where(pd==pd)]
  
  #simple statistics (mean, std, min, max)  
  simple = simple_stats(pd)
  
  #result  
  return {'simple':simple,'pd_ref':pd}
  
def get_stats(fname,iLUT_filepath):
  """
  Get parameter statistics (pstats) and reflectance statistics (rstats)
  """
  
  #validation LUT and interpolated LUT  
  vLUT = pickle.load(open(fname,"rb"))
  iLUT = pickle.load(open(iLUT_filepath,"rb"))
  
  #known test values
  test_inputs = vLUT['inputs']['permutations']
  true_outputs = vLUT['outputs']
  
  #interpolated estimates
  interp_outputs = []
  for test_input in test_inputs:
    interp_outputs.append(iLUT(test_input))

  #array format
  true = np.array(true_outputs)
  interp = np.array(interp_outputs)
  
  #parameter statistics (i.e. Edir, Edif, tau2, Lp)
  pstats = parameter_stats(true,interp)
  
  #reflectance statistics (i.e. for Lambertian reflectance of 0.3)
  rstats = reflectance_stats(true,interp)
  
  # result
  return {'pstats':pstats,'rstats':rstats}

def main():
  
  # configure this test
  sensor = 'LANDSAT_OLI'
  aero_profile = 'CO'
  view_z = 0 
  config = sensor+'_'+aero_profile
  
  # input paths
  validation_path = os.path.dirname(os.path.abspath(__file__))
  base_path =  os.path.dirname(os.path.dirname(validation_path))
  vLUT_path = '{}/vLUTs/{}/viewz_{}'.format(validation_path,config,view_z)
  iLUT_path = '{}/iLUTs/{}/viewz_{}'.format(base_path,config,view_z)
  
  # output paths
  stats_path = '{}/stats/{}/viewz_{}'.format(validation_path,config,view_z)
  plots_path = '{}/plots/{}/viewz_{}'.format(validation_path,config,view_z)
  if not os.path.exists(stats_path):
    os.makedirs(stats_path)
  if not os.path.exists(plots_path):
    os.makedirs(plots_path)
  
  try:
    os.chdir(vLUT_path)
  except:
    print('Path not recognized :',vLUT_path)
    sys.exit(1)
  
  # read validation LUT
  fnames = glob.glob('*.lut')
  fnames.sort()
  if len(fnames) == 0:
    print('Did not find vLUT files in :',vLUT_path)
    sys.exit(1)
  
  # find corresponding iLUT values and get statistics
  for fname in fnames:
    fid = fname.split('.')[0]  
    iLUT_filepath = os.path.join(iLUT_path,fid+'.ilut')
    if os.path.isfile(iLUT_filepath):
      stats_filepath = os.path.join(stats_path,fid+'.p')
      if os.path.isfile(stats_filepath) == False:
        print('calculating stats for:'+fid)
        stats = get_stats(fname,iLUT_filepath)
        pickle.dump(stats,open(stats_filepath,'wb'))
    else:
      print('iLUT filepath not recognized: ', iLUT_filepath)
  
if __name__ == '__main__':
  main()