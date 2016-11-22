#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
'LUT_validation_histoplot.py', Sam Murphy (2016-11-18)


Visualize LUT_validation_stats as overlapping histograms from blue to swir2

"""

import os
import sys
import glob
import pickle
import matplotlib.pylab as plt
from matplotlib import rcParams
import numpy as np


def plot_stats(fnames):
  
  # set-up plot space
  rcParams['xtick.direction'] = 'out' #xticks that point down
  plt.xlabel('% difference')
  plt.xlim([-5,5])
  plt.xticks(np.linspace(-5,5,11))
  ax = plt.axes()
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  ax.get_xaxis().tick_bottom()
  ax.get_yaxis().set_visible(False)
  
  # plot histograms
  bins = np.linspace(-10,10,101)
  colors = ['b','g','r','c','y','m']
  for i, fname in enumerate(fnames):
    stats = pickle.load(open(fname,'rb'))
    pd = stats['pd']
    plt.hist(pd, bins, normed=1, facecolor=colors[i])

def main():
  
  # configure this plot
  ref = 0.1 # Lambertian reflectance
  sensor = 'LANDSAT_OLI'
  aero_profile = 'CO'
  config = sensor+'_'+aero_profile
  
  # I/O
  validation_path = os.path.dirname(os.path.abspath(__file__))
  stats_path = '{}/stats/{}/viewz_0/{:.2f}'.format(validation_path,config,ref)
  try:
    os.chdir(stats_path)
  except:
    print('Path not recognized :',stats_path)
    sys.exit(1)
  fnames = glob.glob('*.stats')
  fnames.sort()
  if len(fnames) == 0:
    print('Did not find stats files in :',stats_path)
    sys.exit(1)    
  
  # histogram plot (i.e. overlap each waveband)
  plot_stats(fnames)
  
if __name__ == '__main__':
  main()