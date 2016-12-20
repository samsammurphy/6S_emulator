#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonteCarlo_Plot.py, Sam Murphy (2016-12-02)

Plots delta reflectance (dref) intervals at 95 % confidence for all surface 
reflectances
"""

import numpy as np
from matplotlib import pylab as plt
from matplotlib import rcParams
from MonteCarlo_Histoplot import load_performance_stats
from MonteCarlo_Histoplot import dref_slice
from MonteCarlo_Histoplot import color_from_channel

  
    
def plot_confidence95(channels):
  """
  Plots 95% confidence dref intervals for all surface reflectances
  """
  
  for channel in channels:
    
    # color for this channel
    color = color_from_channel(channel)
    
    # load performance statistics (all reflectances)
    drefs, refs = load_performance_stats(channel)
    
    # 95 % confidence interval
    confidence = []
    
    for ref in refs:
      
      # stats for this reflectance
      dref = dref_slice(drefs,refs,ref)
  
      # append 95% interval
      confidence.append(np.percentile(abs(dref),95))
      
    plt.plot(refs,confidence,color,linewidth=2)
    plt.xlabel('surface reflectance')
    plt.ylabel('delta reflectance interval')
    plt.ylim(0,0.012)
        
    
def main():
  
  # channel name
  channels = ['blue','green','red','nir','swir1','swir2']

  # histogram plot
  plot_confidence95(channels)

  
if __name__ == '__main__':
  main()