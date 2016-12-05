#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonteCarlo_countRuns.py, Sam Murphy (2016-12-05)


counts the Monte Carlo runs to make sure there are at least 100,000 for
each waveband

"""

import os
import glob
import pickle

print('\nCounting Monte Carlo runs..')

file_dir = os.path.dirname(__file__)
stat_dir = os.path.join(file_dir,'stats')

for channel in ['blue','green','red','nir','swir1','swir2']:
  
  channel_dir = os.path.join(stat_dir,channel)
  try:
    os.chdir(channel_dir)
    
    count = 0
    stat_files = glob.glob('*.p')
    for stat_file in stat_files:
      drefs, refs = pickle.load(open(stat_file,'rb'))
      count += len(drefs)
    
    print('{} = {}'.format(channel,count))
  except:
    print('channel directory error: '+channel_dir)