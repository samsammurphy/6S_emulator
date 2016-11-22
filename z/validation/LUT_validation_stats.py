# -*- coding: utf-8 -*-
"""

'LUT_validation_stats.py', Sam Murphy (2016-11-18)

This module creates validation look up tables (vLUTs). It is for an initial 
validation of the iLUT approach for atmospheric correction. The LUTs 
used for atmospheric correction define a discrete parameter space, which is then
interpolated to obtain continuous results. This raises the question: 
  
  'How do we know if the interpolation is reasonable?'

To answer this question we (at least initially) have defined a set of parameter
values that are as far away as possible (i.e. in the middle) of the increments
used to create the atmcorr LUTs (and iLUTs). The idea is that these mid-points
are the 'most difficult' points for the iLUT to estimate.

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
    
def reflectance_stats(ref, sixs_outputs, estimated_outputs):
  """
  Surface reflectance statistics. Compares 6S outputs to the estimated 
  (i.e. interpolated) outputs.
  """
  
  def at_sensor_radiance(ref,Edir,Edif,tau2,Lp):
    return ref*tau2*(Edir + Edif)/np.pi + Lp
  
  def surface_reflectance(rad,Edir,Edif,tau2,Lp):
    return np.pi*(rad-Lp) / (tau2*(Edir+Edif))
    
  
  # convert to arrays for speed
  true = np.array(sixs_outputs)
  est = np.array(estimated_outputs)    
    
  # at-sensor radiance (i.e. for given surface reflectance and atmosphere)
  radiance = at_sensor_radiance(ref,true[:,0],true[:,1],true[:,2],true[:,3])
  
  # reflectance value from estimated (i.e. interpolated) output
  interp_ref = surface_reflectance(radiance,est[:,0],est[:,1],est[:,2],est[:,3])
  
  # percentage difference from true reflectance
  pd = 100*(interp_ref-ref)/ref
  pd = pd[np.where(pd==pd)]    #ignore NaNs  
  
  # mean, std, min, max
  stats = (np.mean(pd),np.std(pd),np.min(pd),np.max(pd)) 
  
  # confidence percentiles (i.e. 90, 95 and 99%)
  confidence = np.percentile(abs(pd),[90,95,99])
  
  # result  
  return {'ref':ref,'pd':pd,'stats':stats,'confidence':confidence}
  


def get_stats(vLUT_path,iLUT_path, ref):
  """
  Loads the validation LUT (i.e. discrete table) and the interpolated LUT 
  (i.e. a linear interpolator object). Calculates interpolated output values
  for each set of validation input parameters. Then passes this interpolated 
  output, as well as the validation (i.e. true) output, to reflectance_stats().  
  
  """
  
  # validation LUT (a discrete table)
  vLUT = pickle.load(open(vLUT_path,"rb")) 
  
  # 6s outputs
  sixs_outputs = vLUT['outputs']  
  
  # estimated 6S outputs (i.e. interpolated from true inputs)
  inputs = vLUT['inputs']['permutations']
  iLUT = pickle.load(open(iLUT_path,"rb"))# interpolated LUT (an interpolator object)  
  estimated_outputs = []
  for i in inputs:
    estimated_outputs.append(iLUT(i))
  
  #reflectance statistics
  return reflectance_stats(ref, sixs_outputs, estimated_outputs)
  
def main():
  
  # configuration
  sensor = 'LANDSAT_OLI'
  aero_profile = 'CO'
  config = sensor+'_'+aero_profile
  
  # input (i.e. validation LUTs and interpolated LUTs)
  validation_dir = os.path.dirname(os.path.abspath(__file__))
  base_dir =  os.path.dirname(os.path.dirname(validation_dir))
  vLUT_dir = os.path.join(validation_dir,'vLUTs',config,'viewz_0')
  iLUT_dir = os.path.join(base_dir,'iLUTs',config,'viewz_0')
  vLUT_paths = glob.glob(vLUT_dir+'/*.lut')
  if vLUT_paths == []:
    print('Validation LUTs not found at: '+vLUT_dir)
    sys.exit(1)
  
  # output (i.e. for each surface reflectance value)
  refs = np.linspace(0.01,0.3,30)
  for ref in refs:
    stats_dir = os.path.join(validation_dir,'stats',config,'viewz_0',str(ref))
    if not os.path.exists(stats_dir):
      os.makedirs(stats_dir)
    
    for vLUT_path in vLUT_paths:
      fid = os.path.basename(vLUT_path).split('.')[0]   
      iLUT_path = os.path.join(iLUT_dir,fid+'.ilut')
      if os.path.isfile(iLUT_path):
        print('Calculating stats for: {}_{}'.format(fid,ref))
        stats = get_stats(vLUT_path,iLUT_path, ref)
        stats_path = os.path.join(stats_dir,fid+'.stats')
        pickle.dump(stats,open(stats_path,'wb'))
      else:
        print('iLUT filepath not recognized: ', iLUT_path)
  
if __name__ == '__main__':
  main()
  print('Done')