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


def read_stats(stats_dir,confidence_level):
  
  # reflectance values
  refs = [0.1]#np.linspace(0.01,0.3,30)
  
  for ref in refs:
    refdir = '{}/{:.2f}'.format(stats_dir,ref)
    try:
      os.chdir(refdir)
    except:
      print('Path not recognized :',refdir)
      sys.exit(1)
    fnames = glob.glob('*.stats')
    fnames.sort()
    if len(fnames) == 0:
      print('Did not find stats files in :',refdir)
      sys.exit(1)
    
    for fname in fnames:
      stats = pickle.load(open(fname,'rb'))
      confidence_interval = stats['confidence'][confidence_level]
      print(fname,confidence_interval)

      
      ###
      """
      YOU ARE HERE
      """
      
      ###
      
      

def plot_stats(stats_dir,confidence_level):
  
  read_stats(stats_dir,confidence_level)
      
def main():
  
  # plot configuration
  config = 'LANDSAT_OLI_CO'
  
  # confidence_level
  confidence_level = '95'# i.e. 95 percentile 
  
  # statistic dir
  validation_dir = os.path.dirname(os.path.abspath(__file__))
  stats_dir = '{}/stats/{}/viewz_0/'.format(validation_dir,config)
    
  # plot stats
  plot_stats(stats_dir,confidence_level)
  
if __name__ == '__main__':
  main()