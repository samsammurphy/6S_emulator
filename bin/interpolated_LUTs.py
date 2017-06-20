"""
interpolated_LUTs.py

The Interpolated_LUTs class handles loading, downloading and interpolating
of LUTs (look up tables) used by the 6S emulator 

"""

import os
import glob
import pickle
import urllib.request
import zipfile
import time
from itertools import product
from scipy.interpolate import LinearNDInterpolator


class Interpolated_LUTs:
  """
  The Interpolated_LUTs class handles loading, downloading and interpolating
  of LUTs (look up tables) used by the 6S emulator.
  """
  
  def __init__(self, mission):
    
    # satellite mission
    self.mission = mission

    # Earth Engine mission to Py6S sensor name
    self.py6S_sensor_names = {
      'COPERNICUS/S2':'S2A_MSI',
      'LANDSAT/LC8_L1T':'LANDSAT_OLI',
      'LANDSAT/LE7_L1T':'LANDSAT_ETM',
      'LANDSAT/LT5_L1T':'LANDSAT_TM',
      'LANDSAT/LT4_L1T':'LANDSAT_TM'
    }
    self.py6S_sensor = self.py6S_sensor_names[self.mission]
    
    # files directory (i.e. where (i)LUTs are/will be stored)
    self.bin_path = os.path.dirname(os.path.abspath(__file__))
    self.base_path = os.path.dirname(self.bin_path)
    self.files_dir = os.path.join(self.base_path,'files')
    if not os.path.isdir(self.files_dir):
      print('files directory not found, will create at:\n{}'.format(self.files_dir))
      os.makedirs(self.files_dir)

    # absolute path to iLUTs directory
    self.iLUTs_dir = os.path.join(self.files_dir,'iLUTs',self.py6S_sensor,\
    'Continental','view_zenith_0')

    # absolute path to LUTs directory
    self.LUTs_dir = os.path.join(self.files_dir,'LUTs',self.py6S_sensor,\
    'Continental','view_zenith_0')
    
    # Earth Engine Sentinel 2 bandName from Py6S bandName switch
    self.ee_sentinel2_bandNames = {
      '01':'B1',
      '02':'B2',
      '03':'B3',
      '04':'B4',
      '05':'B5',
      '06':'B6',
      '07':'B7',
      '08':'B8',
      '09':'B8A',
      '10':'B9',
      '11':'B10',
      '12':'B11',
      '13':'B12',
    }

  def get(self):
    """
    Loads interpolated look up tables from local files (if they exist)
    """
      
    self.iLUTs = {}
    
    # load iLUTs
    filepaths = glob.glob(self.iLUTs_dir+os.path.sep+'*.ilut')
    if filepaths:
      
      try:
        for f in filepaths:
          bandName = os.path.basename(f).split('.')[0][-2:]
          
          # Sentinel 2 band names vary between Earth Engine and Py6S
          if self.mission == 'COPERNICUS/S2':
            bandName = self.ee_sentinel2_bandNames[bandName]

          self.iLUTs[bandName] = pickle.load(open(f,'rb'))
      except:
        print('problem loading interpolated look up table (.ilut) files from:\n'+self.iLUTs_dir)      
    else:
      print('Looked for iLUTs but did not find in:\n{}'.format(self.iLUTs_dir))
    
    return self.iLUTs

  def interpolate_LUTs(self):
    """
    interpolate look up tables
    """
    
    filepaths = sorted(glob.glob(self.LUTs_dir+os.path.sep+'*.lut'))

    if filepaths:
      
      print('running n-dimensional interpolation may take a few minutes...')
      
      try:

        for fpath in filepaths:
          
          fname = os.path.basename(fpath)
          fid, ext = os.path.splitext(fname)
          ilut_filepath = os.path.join(self.iLUTs_dir,fid+'.ilut')
          
          if os.path.isfile(ilut_filepath):
            print('iLUT file already exists (skipping interpolation): {}'.format(fname))
          else:
            print('Interpolating: '+fname)

            # load look up table
            LUT = pickle.load(open(fpath,"rb"))

            # input variables (all permutations)
            invars = LUT['config']['invars']
            inputs = list(product(invars['solar_zs'],
                                  invars['H2Os'],
                                  invars['O3s'],
                                  invars['AOTs'],
                                  invars['alts']))  
            
            # output variables (6S correction coefficients)
            outputs = LUT['outputs']

            # piecewise linear interpolant in n-dimensions
            t = time.time()
            interpolator = LinearNDInterpolator(inputs,outputs)
            print('Interpolation took {:.2f} (secs) = '.format(time.time()-t))
            
            # save new interpolated LUT file
            pickle.dump(interpolator, open(ilut_filepath, 'wb' ))

      except:

        print('interpolation error')

    else:
      
      print('LUTs directory: ',self.LUTs_dir)
      print('LUT files (.lut) not found in LUTs directory, try downloading?')
      

  def download_LUTs(self):
    
    # directory for zip file
    zip_dir = os.path.join(self.files_dir,'LUTs')
    if not os.path.isdir(zip_dir):
      os.makedirs(zip_dir)

    # URLs for Sentinel 2 and Landsats (dl=1 is important)
    getURL = {
      'S2A_MSI':"https://www.dropbox.com/s/aq873gil0ph47fm/S2A_MSI.zip?dl=1",
      'LANDSAT_OLI':'https://www.dropbox.com/s/49ikr48d2qqwkhm/LANDSAT_OLI.zip?dl=1',
      'LANDSAT_ETM':'https://www.dropbox.com/s/z6vv55cz5tow6tj/LANDSAT_ETM.zip?dl=1',
      'LANDSAT_TM':'https://www.dropbox.com/s/uyiab5r9kl50m2f/LANDSAT_TM.zip?dl=1',
      'LANDSAT_TM':'https://www.dropbox.com/s/uyiab5r9kl50m2f/LANDSAT_TM.zip?dl=1'
    }

    # download LUTs data
    print('Downloading look up table (LUT) zip file..')
    url = getURL[self.py6S_sensor]
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()
    
    # save to zip file
    zip_filepath = os.path.join(zip_dir,self.py6S_sensor+'.zip')
    with open(zip_filepath, "wb") as f :
        f.write(data)

    # extract LUTs directory
    print('Extracting zip file..')
    with zipfile.ZipFile(zip_filepath,"r") as zip_ref:
        zip_ref.extractall(zip_dir)

    # delete zip file
    os.remove(zip_filepath)

    print('Done: LUT files available locally')


# debugging
# iLUTs = Interpolated_LUTs('LANDSAT/LT5_L1T')
# iLUTs.download_LUTs()
# iLUTs.interpolate_LUTs()
# iLUTs.get()
# print(iLUTs.iLUTs)
