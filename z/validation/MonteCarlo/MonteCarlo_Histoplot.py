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
  Plots two histograms 1) percentage difference, 2) delta reflectance
  """
  fig = plt.figure()
  ax1 = fig.add_subplot(211)
  ax2 = fig.add_subplot(212)
  
  for channel in channels:
    
    # load performance statistics (all SRs)
    drefs, refs = load_performance_stats(channel)
      
    # stats for this reflectance
    dref = dref_slice(drefs,refs,ref)
  
    # color of channel
    color = color_from_channel(channel)
    
    # percentage difference histograms
    bins = np.linspace(-10,10,101)
    pd = 100*dref/ref
    ax1.hist(pd, bins, normed=1, facecolor=color)
    ax1.set_title('percentage difference')
    
    # dref histogram
    bins = ref*bins/100 # convert to reflectance values (but in same % range)
    ax2.hist(dref, bins ,normed=1, facecolor=color)
    ax2.set_xlim((min(bins),max(bins)))
    ax2.set_title('delta reflectance')
    
    print('{} 95% confidence = {}'.format(channel,np.percentile(abs(pd),95)))
  
  fig.tight_layout()

  
def main():
  
  # surface reflectance (SR)
  ref = 0.05

  # channel name
  channels = ['blue','green','red','nir','swir1','swir2']

  # histogram plot
  plot_histograms(ref,channels)
  
  
if __name__ == '__main__':
  main()