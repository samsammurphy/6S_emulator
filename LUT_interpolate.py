# -*- coding: utf-8 -*-
"""
LUT interpolate

Reads lookup table (.lut) files and executes a piecewise linear interpolant
in N dimensions. 

Saves the interpolator as a python pickle object with file extension (.ilut)

"""

import glob
import os
import pickle
import sys
import time
import re

import numpy as np
from scipy.interpolate import LinearNDInterpolator

def create_interpolator(filename):
  """
  Loads a LUT file and creates an interpolated LUT object.
  The interpolant is constructed by triangulating the input data with Qhull
  and performing linear barycentric interpolation on each triangle
  
  """
  
  #load LUT
  LUT = pickle.load(open(filename,"rb"))
  
  #read LUT
  inputs = LUT['inputs']['permutations']
  outputs = LUT['outputs']
  
  #input variable permutation
  solar_z = [i[0] for i in inputs]
  H2O     = [i[1] for i in inputs]
  O3      = [i[2] for i in inputs]
  AOT     = [i[3] for i in inputs]
  alt     = [i[4] for i in inputs]
  
  #output variables
  Edir = [o[0] for o in outputs]
  Edif = [o[1] for o in outputs]
  tau2 = [o[2] for o in outputs]
  Lp   = [o[3] for o in outputs]
  
  #convert to the correct format (i.e. an array of tubles)
  inputs = np.array(list(zip(solar_z,H2O,O3,AOT,alt)))
  outputs = np.array(list(zip(Edir,Edif,tau2,Lp)))
  
  # piecewise linear interpolant in N dimensions
  t = time.time()
  interpolator = LinearNDInterpolator(inputs,outputs)
  print('Interpolation took {:.2f} (secs) = '.format(time.time()-t))
  
  # sanity check
  i = 0
  true   = (Edir[i],Edif[i],tau2[i],Lp[i])
  interp = interpolator(solar_z[i],H2O[i],O3[i],AOT[i],alt[i])
  
  print('Quick check..')
  print('true   = {0[0]:.2f} {0[1]:.2f} {0[2]:.2f} {0[3]:.2f}'.format(true))
  print('interp = {0[0]:.2f} {0[1]:.2f} {0[2]:.2f} {0[3]:.2f}'.format(interp))
  
  return interpolator


def main():
  
  args = sys.argv[1:]
  
  if len(args) != 1:
    print('usage: $ python3 LUT_interpolation.py luts_path')
    sys.exit(1)
  else:
    lut_path = args[0]

  #create outdir (use regular expressions to rename ../LUT/.. to ../iLUT/..)
  s = re.search('/LUTs/',lut_path)
  base_path = lut_path[:s.start()]
  satellite_config = lut_path[s.end():]
  ilut_path = base_path+'/iLUTs/'+satellite_config
  if not os.path.exists(ilut_path):
    os.makedirs(ilut_path)
  
  # find LUT files
  try:
    os.chdir(lut_path)
  except:
    print('invalid LUT directory: ' + lut_path)
    sys.exit(1)
  fnames = glob.glob('*.lut')
  fnames.sort()
  if len(fnames) == 0:
    print('could not find .lut files in path: ' + lut_path)
    sys.exit(1)
  
  # interpolate LUT files
  for fname in fnames:
    
    fid, ext = os.path.splitext(fname)
    ilut_filepath = os.path.join(ilut_path,fid+'.ilut')
    
    if os.path.isfile(ilut_filepath):
      print('iLUT file already exists (skipping interpolation): {}'
      .format(os.path.basename(ilut_filepath)))
    else:
      print('Interpolating: '+fname)
      interpolator = create_interpolator(fname)
      
      pickle.dump(interpolator, open(ilut_filepath, 'wb' ))

if __name__ == '__main__':
  main()
