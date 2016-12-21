#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonteCarlo_Histoplot.py

Plots histogram of percentage difference for a single surface reflectance
"""

import os
import glob
import sys
import pickle
import numpy as np
from matplotlib import pylab as plt
from matplotlib import rcParams


def load_performance_stats(channel):
  """
  Loads all available MonteCarlo stats for a given channel of Landsat 8
  """
  file_dir = os.path.dirname(os.path.abspath(__file__)) 
  stat_dir = os.path.join(file_dir,'stats',channel)
  try:
    os.chdir(stat_dir)
    stat_files = glob.glob('*p')
    drefs = []
    for stat_file in stat_files:
      these_drefs, refs = pickle.load(open(stat_file,'rb'))
      these_drefs[np.where(these_drefs != these_drefs)] = 0 # NaN = 0
      drefs.append(these_drefs)
    return np.concatenate((drefs),axis=0), refs
  except:
    print('statistics loading error for: '+stat_dir)
    sys.exit(1)  
  
    
def dref_slice(drefs, refs, ref):
  """
  Performance metric is delta reflectance (dref). It was calculated for a 
  range of true relfectance values. This returns stats for single true ref.
  """
  index = np.where(ref == refs)[0]
  if len(index) == 0:
    print('ref not available: {}'.format(ref))
    sys.exit()
  return np.array([ds[index][0] for ds in drefs])

def color_from_channel(channel):
  switch = {
            'blue':'blue',
            'green':'green',
            'red':'red',
            'nir':'yellow',
            'swir1':'cyan',
            'swir2':'magenta'
            }
  return switch[channel]
  

def plot_histograms(ref,channels):
  """
  Plots delta surface reflectance histograms
  """
  
  # plot setup (style = nice and clean)
  rcParams['xtick.direction'] = 'out' #xticks that point down
  plt.xlabel('delta surface reflectance')
  plt.xlim([-0.02,0.02])
  #plt.xticks(np.linspace(-0.05,0.05,11))
  ax = plt.axes()
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  ax.get_xaxis().tick_bottom()
  ax.get_yaxis().set_visible(False)
  
  for channel in channels:
    
    # load performance statistics (all reflectances)
    drefs, refs = load_performance_stats(channel)
      
    # stats for this reflectance
    dref = dref_slice(drefs,refs,ref)
  
    # color for this channel
    color = color_from_channel(channel)
    
    # percentage difference histogram
    #pd = 100*dref/ref
    bins = np.linspace(-0.05,0.05,201)
    plt.hist(dref, bins, normed=1, facecolor=color)
      
    print('{} 95% confidence = {}'.format(channel,np.percentile(abs(dref),95)))
  
    
def main():
  
  # surface reflectance (SR)
  ref = 0.1

  # channel name
  channels = ['blue','green','red','nir','swir1','swir2']

  # histogram plot
  plot_histograms(ref,channels)

  
if __name__ == '__main__':
  main()