#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
'LUT_validation_plots.py', Sam Murphy (2016-11-18)


Visualize the output from LUT_validation_stats

"""

import os
import sys
import glob
import pickle
import matplotlib.pylab as plt
from matplotlib import rcParams
import numpy as np


def plot_stats(stats_path):
  
  # find statistic files (in order)
  try:
    os.chdir(stats_path)
  except:
    print('Path not recognized :',stats_path)
    sys.exit(1)
  fnames = glob.glob('*.p')
  fnames.sort()
  
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
  colors = ['b','g','r','grey','grey','grey']
  for i, fname in enumerate(fnames):
    stats = pickle.load(open(fname,'rb'))
    pd_ref = stats['rstats']['pd_ref']
    plt.hist(pd_ref, bins, normed=1, facecolor=colors[i])


def main():
  
  # configure this test
  sensor = 'LANDSAT_OLI'
  aero_profile = 'CO'
  view_z = 0
  config = sensor+'_'+aero_profile

  # statistics directory
  validation_path = os.path.dirname(os.path.abspath(__file__))
  stats_path = '{}/stats/{}/viewz_{}'.format(validation_path,config,view_z)

  # histogram plot (i.e. overlap each waveband)
  plot_stats(stats_path)
  
if __name__ == '__main__':
  main()