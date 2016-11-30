#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LUT_validation_plot.py, Sam Murphy (2016-11-21)

The overview of LUT_validation_stats. Displays results for all surface reflectance
values (0.01 to 0.3) as lines that represent the 95% confidence limit for each
waveband

"""

import os
import glob
import sys
import pickle
import numpy as np
from matplotlib import pylab as plt



def read_confidence(fname,confidence_level,sr=False):
  """
  Reads confidence interval for given filename and confidence level (e.g. 95%)
  
  Optionally convert from '% difference' to 'surface refletance' interval
  
  """
  
  # percentage difference statistics
  pd = pickle.load(open(fname,'rb'))
  
  # pd interval
  interval = pd['confidence'][confidence_level]

  # surface reflectance interval?
  if sr:
    interval = sr * interval/100
  
  return interval
  
  
def read_stats(refs,stats_dir,confidence_level,sr_interval=False):
    
  # confidence arrays
  b = []# blue
  g = []# green
  r = []# red
  n = []# nir
  s1 =[]# swir1
  s2 =[]# swir2

  # fill confidence arrays for each surface reflectance value
  for ref in refs:
    refdir = '{}/{:.2f}'.format(stats_dir,ref)
    try:
      os.chdir(refdir)
    except:
      print('Path not recognized :',refdir)
      sys.exit(1)
    # find stat files
    fnames = glob.glob('*.stats')
    fnames.sort()
    # append results to confidence arrays
    if sr_interval:
      sr=ref
    else:
      sr=False
    b.append(read_confidence(fnames[0],confidence_level,sr=sr))
    g.append(read_confidence(fnames[1],confidence_level,sr=sr))
    r.append(read_confidence(fnames[2],confidence_level,sr=sr))
    n.append(read_confidence(fnames[3],confidence_level,sr=sr))
    s1.append(read_confidence(fnames[4],confidence_level,sr=sr))
    s2.append(read_confidence(fnames[5],confidence_level,sr=sr))
  
  return {'b':b,'g':g,'r':r,'n':n,'s1':s1,'s2':s2}      
      

def plot_stats(refs,stats_dir,confidence_level,sr_interval=False):
    
  stats = read_stats(refs,stats_dir,confidence_level,sr_interval=sr_interval)
  
  plt.plot(refs,stats['b'],'b',linewidth=2)
  plt.plot(refs,stats['g'],'g',linewidth=2)
  plt.plot(refs,stats['r'],'r',linewidth=2)
  plt.plot(refs,stats['n'],'c',linewidth=2)
  plt.plot(refs,stats['s1'],'y',linewidth=2)
  plt.plot(refs,stats['s2'],'m',linewidth=2)
  
  plt.title('{}% confidence level'.format(confidence_level))
  if sr_interval:
    plt.ylabel('reflectance interval')
  else:
    plt.ylim(0,50)
    plt.ylabel('percentage interval (%)')
  plt.xlabel('surface reflectance')
  
  
      
def main():
  
  # plot configuration
  config = 'LANDSAT_OLI_CO'
  
  # confidence_level
  confidence_level = '95'# i.e. 95 percentile 
  
  # reflectance values
  refs = np.linspace(0.01,0.3,30)
  
  # statistic dir
  validation_dir = os.path.dirname(os.path.abspath(__file__))
  stats_dir = '{}/stats/{}/viewz_0/'.format(validation_dir,config)
    
  # plot stats: either i) percent difference (default) or ii) SR difference
  plot_stats(refs, stats_dir,confidence_level,sr_interval = True)
  
if __name__ == '__main__':
  main()