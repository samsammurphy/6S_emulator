# -*- coding: utf-8 -*-
"""

'LUT_validation_stats.py', Sam Murphy (2016-11-18)

The validation parameter space was create by setting the --validation key to
the 'LUT_build.py' module.

Statistics are calculated in terms surface reflectance difference between 
i) 6S forward model ('truth') and ii) interpolated 6S inverse model.

"""


import os
import glob
import sys
import pickle
import numpy as np
    
def reflectance_stats(ref, sixs_outputs, estimated_outputs):
  """
  Surface reflectance statistics. Compares 6S outputs to the estimated 
  (i.e. interpolated) outputs in terms of difference in surface reflectance.
  """
  
  def at_sensor_radiance(ref,Edir,Edif,tau2,Lp):
    return ref*tau2*(Edir + Edif)/np.pi + Lp
  
  def surface_reflectance(rad,Edir,Edif,tau2,Lp):
    return np.pi*(rad-Lp) / (tau2*(Edir+Edif))
    
  
  # convert to arrays (i.e. process input/output lists in one go with no loops)
  SixS = np.array(sixs_outputs)
  est = np.array(estimated_outputs)    
    
  # at-sensor radiance using 6S outputs
  radiance = at_sensor_radiance(ref,SixS[:,0],SixS[:,1],SixS[:,2],SixS[:,3])
  
  # reflectance value from estimated (i.e. interpolated) output
  interp_ref = surface_reflectance(radiance,est[:,0],est[:,1],est[:,2],est[:,3])
  
  # percentage difference from 6S reflectance
  pd = 100*(interp_ref-ref)/ref
  pd = pd[np.where(pd==pd)]    #ignore NaNs  
  
  # mean, std, min, max
  stats = (np.mean(pd),np.std(pd),np.min(pd),np.max(pd)) 
  
  # confidence percentiles (i.e. 90, 95 and 99%)
  q = np.percentile(abs(pd),[90,95,99])
  confidence = {'90':q[0],'95':q[1],'99':q[2]}
  
  # result  
  return {'ref':ref,'pd':pd,'stats':stats,'confidence':confidence}
  


def get_stats(vLUT_path,iLUT_path, ref):
  """
  Loads the validation LUT (i.e. discrete table). Goes through each set
  of input/output pairs. The output is the 6S result, the input will be interpolated
  to create an estimate 6S output. The two types of output will be compared. 
  
  """
  
  # validation LUT (a discrete table)
  vLUT = pickle.load(open(vLUT_path,"rb")) 
  
  # interpolated LUT (interpolator object)  
  iLUT = pickle.load(open(iLUT_path,"rb"))
  
  # validation inputs
  inputs = vLUT['inputs']['permutations']

  # 6S outputs (i.e. validation truth)
  sixs_outputs = vLUT['outputs']  
  
  # estimated outputs (i.e. interpolation to be tested) 
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
  file_dir = os.path.dirname(os.path.abspath(__file__))
  base_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_dir)))
  vLUT_dir = os.path.join(file_dir,'vLUTs',config,'viewz_0')
  iLUT_dir = os.path.join(base_dir,'iLUTs',config,'viewz_0')
  vLUT_paths = glob.glob(vLUT_dir+'/*.lut')
  if vLUT_paths == []:
    print('Validation LUTs not found at: '+vLUT_dir)
    sys.exit(1)
  
  # output (i.e. for each surface reflectance value)
  refs = [0.01]# np.linspace(0.01,0.3,30)
  for ref in refs:
    stats_dir = os.path.join(file_dir,'stats',config,'viewz_0',\
                             '{:.2f}'.format(ref))
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