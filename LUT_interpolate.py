# -*- coding: utf-8 -*-
"""
LUT interpolate

Reads lookup table (.lut) files and executes a piecewise linear interpolant
in N dimensions. 

Purpose: Allows discrete look up tables to be used to calulate continuous
solutions for atmospheric correction :)

Output: Pickled interpolator object with file extension (.ilut)

"""

import glob
import os
import pickle
import sys
import time
import re

from LUT_build import permutate_invars

import numpy as np
from scipy.interpolate import LinearNDInterpolator

def create_interpolator(filename):
  """
  Loads a LUT file and creates an interpolated LUT object.
  The interpolant is constructed by triangulating the input data using Qhull
  and performing linear barycentric interpolation on each triangle
  
  """
  
  #load LUT
  LUT = pickle.load(open(filename,"rb"))

  # LUT inputs (H2O, O3, etc.) and outputs (i.e. atmcorr coeffs)
  inputs = permutate_invars(LUT['config']['invars'])
  outputs = LUT['outputs']

  # piecewise linear interpolant in N dimensions
  t = time.time()
  interpolator = LinearNDInterpolator(inputs,outputs)
  print('Interpolation took {:.2f} (secs) = '.format(time.time()-t))

  # sanity check
  print('Quick check..')
  i = 0
  true   = (outputs[i][0],outputs[i][1])
  interp = interpolator(inputs[i][0],inputs[i][1],inputs[i][2],inputs[i][3],inputs[i][4]) 
  print('true   = {0[0]:.2f} {0[1]:.2f}'.format(true))
  print('interp = {0[0]:.2f} {0[1]:.2f}'.format(interp))
  
  return interpolator


def main():
  
  args = sys.argv[1:]
  
  if len(args) != 1:
    print('usage: $ python3 LUT_interpolate.py  path/to/LUT_directory')
    sys.exit(1)
  else:
    lut_path = args[0]

  try:
    os.chdir(lut_path)
  except:
    print('invalid directory: ' + lut_path)
    sys.exit(1)
    
  # create iLUTs directory (i.e. swap '/LUTs/' with '/iLUTs/')
  match = re.search('LUTs',lut_path)
  base_path = lut_path[0:match.start()]
  end_path = lut_path[match.end():]
  ilut_path = base_path+'iLUTs'+end_path

  fnames = glob.glob('*.lut')
  fnames.sort()
  if len(fnames) == 0:
    print('could not find .lut files in path: ' + lut_path)
    sys.exit(1)
  
  if not os.path.exists(ilut_path):
    os.makedirs(ilut_path)
    
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
