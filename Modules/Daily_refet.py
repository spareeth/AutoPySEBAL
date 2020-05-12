#-*- coding: utf-8 -*-

"""
Python script to compute daily ref ET from Meteo data and DEM
Based on PySEBAl 3.3.7.1

@author: Tim Hessels, Jonna van Opstal, Patricia Trambauer, Wim Bastiaanssen, Mohamed Faouzi Smiej, Yasir Mohamed, and Ahmed Er-Raji
         UNESCO-IHE
         September 2017

@author Sajid Pareeth
        December 2019
"""

import pdb
import platform
import sys
import os
import re
import shutil
import click
import numpy as np
import datetime
from osgeo import osr  
import gdal  
from math import sin, cos, pi, tan
import time
import subprocess
import numpy.polynomial.polynomial as poly	
from openpyxl import load_workbook
from pyproj import Proj, transform
import warnings

@click.command()
#General
@click.argument('indir')
@click.argument('outdir')
@click.argument('pathdem')
@click.argument('res')
#meteo
@click.argument('tinst')
@click.argument('t24')
@click.argument('rhinst')
@click.argument('rh24')
@click.argument('winst')
@click.argument('w24')
@click.argument('zx')
@click.argument('rad_method24')
@click.argument('rs24')
@click.argument('transm24')
@click.argument('rad_method_inst')
@click.argument('rsinst')
@click.argument('transminst')
@click.argument('obst_ht')
@click.argument('temp_lapse')

def main(indir, outdir, pathdem, tinst, t24, rhinst, rh24, winst, w24, zx, rad_method24, rs24, transm24, rad_method_inst, rsinst, transminst, obst_ht, temp_lapse, res):

  
    # Do not show warnings
    warnings.filterwarnings('ignore')  
    
    # Open Excel workbook	
    #wb = load_workbook(inputExcel)
			
    # Open the General_Input sheet			
    #ws = wb['General_Input']
 			
    # Extract the input and output folder, and Image type from the excel file			
    input_folder = r"%s" %str(indir)
    output_folder = r"%s" %str(outdir)

    # Create or empty output folder		
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)	
 			
    # Start log file
    filename_logfile = os.path.join(output_folder, 'log.txt')	
    sys.stdout = open(filename_logfile, 'w')
    # Extract the Path to the DEM map from the excel file
    DEM_fileName = r"%s" %str(pathdem) #'DEM_HydroShed_m'  

    # Print data used from sheet General_Input
    print '.................................................................. '
    print '......................SEBAL Model running ........................ '
    print '.................................................................. '
    print 'pySEBAL version 3.3.7.1 Github'
    print 'General Input:'			
    print 'Path to DEM file = %s' %str(DEM_fileName)
    print 'input_folder = %s' %str(input_folder)
    print 'output_folder = %s' %str(output_folder)
    print '......................... Meteo Data ............................. '				
			
    # Open the Meteo_Input sheet	
    #ws = wb['Meteo_Input']	
 
    # ---------------------------- Instantaneous Air Temperature ------------
    # Open meteo data, first try to open as value, otherwise as string (path)	  
    try:
        Temp_inst = float(tinst)                # Instantaneous Air Temperature (°C)

        # If the data is a value than call this variable 0
        Temp_inst_kind_of_data = 0
        print 'Instantaneous Temperature constant value of = %s (Celcius degrees)' %(Temp_inst)
 
    # if the data is not a value, than open as a string	
    except:
        Temp_inst_name = '%s' %str(tinst) 
							
        # If the data is a string than call this variable 1							  
        Temp_inst_kind_of_data = 1
        print 'Map to the Instantaneous Temperature = %s' %(Temp_inst_name)

    # ---------------------------- Daily Average Air Temperature ------------
    # Open meteo data, first try to open as value, otherwise as string (path)	  
    try:
        Temp_24 = float(t24)                # daily average Air Temperature (°C)

        # If the data is a value than call this variable 0
        Temp_24_kind_of_data = 0
        print 'Daily average Temperature constant value of = %s (Celcius degrees)' %(Temp_24)

    # if the data is not a value, than open as a string
    except:
        Temp_24_name = '%s' %str(t24) 
							
        # If the data is a string than call this variable 1							
        Temp_24_kind_of_data = 1
        print 'Map to the Daily average Temperature = %s' %(Temp_24_name)

    # ---------------------------- Instantaneous Relative humidity ------------
    # Open meteo data, first try to open as value, otherwise as string (path)	  							
    try:
        RH_inst = float(rhinst)                # Instantaneous Relative humidity (%)
 
        # If the data is a value than call this variable 0  
        RH_inst_kind_of_data = 0
        print 'Instantaneous Relative humidity constant value of = %s (percentage)' %(RH_inst)
							
    # if the data is not a value, than open as a string							
    except:
        RH_inst_name = '%s' %str(rhinst) 
							
        # If the data is a string than call this variable 1								
        RH_inst_kind_of_data = 1
        print 'Map to the Instantaneous Relative humidity  = %s' %(RH_inst_name)

    # ---------------------------- daily average Relative humidity ------------
    # Open meteo data, first try to open as value, otherwise as string (path)	  														
    try:
        RH_24 = float(rh24)                # daily average Relative humidity (%)
							
        # If the data is a value than call this variable 0  							
        RH_24_kind_of_data = 0
        print 'Daily average Relative humidity constant value of = %s (percentage)' %(RH_24)							

    # if the data is not a value, than open as a string							
    except:
        RH_24_name = '%s' %str(rh24) 
							
        # If the data is a string than call this variable 1								
        RH_24_kind_of_data = 1
        print 'Map to the Daily average Relative humidity = %s' %(RH_24_name)

    # ---------------------------- instantaneous Wind Speed ------------
    # Open meteo data, first try to open as value, otherwise as string (path)	  																					
    try:
        Wind_inst = float(winst)               # instantaneous Wind Speed (m/s) 

        # If the data is a value than call this variable 0  
        Wind_inst_kind_of_data = 0
        print 'Instantaneous Wind Speed constant value of = %s (m/s)' %(Wind_inst)	

    # if the data is not a value, than open as a string							
    except:
        Wind_inst_name = '%s' %str(winst) 
							
        # If the data is a string than call this variable 1								
        Wind_inst_kind_of_data = 1
        print 'Map to the Instantaneous Wind Speed = %s' %(Wind_inst_name)

    # ---------------------------- daily Wind Speed ------------
    # Open meteo data, first try to open as value, otherwise as string (path)	  																												
    try:
        Wind_24 = float(w24)                # daily Wind Speed (m/s)
							
        # If the data is a value than call this variable 0  							
        Wind_24_kind_of_data = 0
        print 'Daily Wind Speed constant value of = %s (m/s)' %(Wind_24)
							
    # if the data is not a value, than open as a string								
    except:
        Wind_24_name = '%s' %str(w24) 
							
        # If the data is a string than call this variable 1							
        Wind_24_kind_of_data = 1
        print 'Map to the Daily Wind Speed = %s' %(Wind_24_name)
   
    # Height of the wind speed measurement
    zx = float(zx)                # Height at which wind speed is measured
    print 'Height at which wind speed is measured = %s (m)' %(zx)
   
    # Define the method of radiation (1 or 2)
    Method_Radiation_24=int(rad_method24)     # 1=Transm_24 will be calculated Rs_24 must be given
                                                         # 2=Rs_24 will be determined Transm_24 must be given
    print 'Method for daily radiation (1=Rs_24, 2=Transm_24) = %s' %(Method_Radiation_24) 

    # if method radiation is 1
    # ---------------------------- daily Surface Solar Radiation ------------
    # Open meteo data, first try to open as value, otherwise as string (path)
    if Method_Radiation_24 == 1:
        try:
            Rs_24 = float(rs24)                # daily Surface Solar Radiation (W/m2) only required when Method_Radiation_24 = 1
  
            # If the data is a value than call this variable 0 
            Rs_24_kind_of_data = 0
            print 'Daily Surface Solar Radiation constant value of = %s (W/m2)' %(Rs_24)

        # if the data is not a value, than open as a string								
        except:
            Rs_24_name = '%s' %str(rs24) 
											
		   # If the data is a string than call this variable 1									
            Rs_24_kind_of_data = 1
            print 'Map to the Daily Surface Solar Radiation = %s' %(Rs_24_name)
 
    # if method radiation is 2
    # ---------------------------- daily transmissivity ------------
    # Open meteo data, first try to open as value, otherwise as string (path)
    if Method_Radiation_24 == 2:   
        try:
            Transm_24 = float(transm24)                # daily transmissivity, Typical values between 0.65 and 0.8 only required when Method_Radiation_24 = 2

            # If the data is a value than call this variable 0  
            Transm_24_kind_of_data = 0
            print 'Daily transmissivity constant value of = %s' %(Transm_24)
											
        # if the data is not a value, than open as a string																			
        except:
            Transm_24_name = '%s' %str(transm24) 
											
		   # If the data is a string than call this variable 1												
            Transm_24_kind_of_data = 1
            print 'Map to the Daily transmissivity = %s' %(Transm_24_name)

    # Define the method of instataneous radiation (1 or 2)		
    Method_Radiation_inst = int(rad_method_inst)    # 1=Transm_inst will be calculated Rs_inst must be given
    print 'Method for instantaneous radiation (1=Rs_inst, 2=Transm_inst) = %s' %(Method_Radiation_inst)                                                           # 2=Rs_24 will be determined Transm_24 must be given
   
    # if method instantaneous radiation is 1
    # ---------------------------- Instantaneous Surface Solar Radiation ------------
    # Open meteo data, first try to open as value, otherwise as string (path)		
    if Method_Radiation_inst == 1:   
        try:
            Rs_in_inst = float(rsinst)                # Instantaneous Surface Solar Radiation (W/m2) only required when Method_Radiation_inst = 1

            # If the data is a value than call this variable 0  
            Rs_in_inst_kind_of_data = 0
            print 'Instantaneous Surface Solar Radiation constant value of = %s (W/m2)' %(Rs_in_inst)
											
        # if the data is not a value, than open as a string											
        except:
            Rs_in_inst_name = '%s' %str(rsinst) 
											
            # If the data is a string than call this variable 1											
            Rs_in_inst_kind_of_data = 1
            print 'Map to the Instantaneous Surface Solar Radiation = %s' %(Rs_in_inst_name)

    # if method instantaneous radiation is 2
    # ---------------------------- Instantaneous transmissivity------------
    # Open meteo data, first try to open as value, otherwise as string (path)		 
    if Method_Radiation_inst == 2:       
        try:
            Transm_inst = float(transminst)                # Instantaneous transmissivity, Typical values between 0.70 and 0.85 only required when Method_Radiation_inst = 2

            # If the data is a value than call this variable 0  
            Transm_inst_kind_of_data=0
            print 'Instantaneous transmissivity constant value of = %s' %(Transm_inst)											

        # if the data is not a value, than open as a string	
        except:
            Transm_inst_name = '%s' %str(transminst) 
		 									
            # If the data is a string than call this variable 1													
            Transm_inst_kind_of_data = 1
            print 'Map to the Instantaneous transmissivity = %s' %(Transm_inst_name) 

     
    # ------------------------------------------------------------------------
    # General constants that could be changed by the user:
    print '...................... General Constants ......................... '	  
                               
    # Data for Module 2 - Spectral and Thermal bands
    L_SAVI = 0.5                          # Constant for SAVI 
    print 'General constants for Module 2:'			
    print 'Constant for SAVI (L) = %s' %(L_SAVI)		
   
    # Data for Module 3 - Vegetation properties
    Apparent_atmosf_transm = 0.89    # This value is used for atmospheric correction of broad band albedo. This value is used for now, would be better to use tsw.
    path_radiance = 0.03             # Recommended, Range: [0.025 - 0.04], based on Bastiaanssen (2000).
    print 'General constants for Module 3:'			
    print 'Atmospheric correction of broad band albedo = %s' %(Apparent_atmosf_transm)	
    print 'Path Radiance = %s' %(path_radiance)	
   
    # Data for Module 4 - Surface temperature, Cloud, Water, and Snow mask
    Rp = 0.91                        # Path radiance in the 10.4-12.5 µm band (W/m2/sr/µm)
    tau_sky = 0.866                  # Narrow band transmissivity of air, range: [10.4-12.5 µm]
    surf_temp_offset = 3             # Surface temperature offset for water 
    Temperature_offset_shadow = -1   # Temperature offset for detecting shadow
    Maximum_shadow_albedo = 0.1      # Minimum albedo value for shadow
    Temperature_offset_clouds = -3   # Temperature offset for detecting clouds
    Minimum_cloud_albedo = 0.4       # Minimum albedo value for clouds
    print 'General constants for Module 4:'			
    print 'Narrow band transmissivity of air = %s' %(tau_sky)	
    print 'Surface temperature offset for water = %s (Kelvin)' %(surf_temp_offset)	
    print 'Temperature offset for detecting shadow = %s (Kelvin)' %(Temperature_offset_shadow)	
    print 'Maximum albedo value for shadow = %s' %(Maximum_shadow_albedo)	
    print 'Temperature offset for detecting clouds = %s (Kelvin)' %(Temperature_offset_clouds)	
    print 'Minimum albedo value for clouds = %s' %(Minimum_cloud_albedo)	

    # ------------------------------------------------------------------------
    # Define the output maps names
    radiation_inst_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Ra_inst_%s_%s_%s_%s_%s.tif' %(res2, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))
    phi_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'phi_%s_%s_%s_%s_%s.tif' %(res2, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))
    radiation_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Ra24_mountain_%s_%s_%s_%s_%s.tif' %(res2, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))
    cos_zn_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'cos_zn_%s_%s_%s_%s_%s.tif' %(res2, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))
    proyDEM_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'proy_DEM_%s.tif' %res2)
    slope_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'slope_%s.tif' %res2)
    aspect_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'aspect_%s.tif' %res2)
    dst_FileName_DEM = os.path.join(output_folder, 'Output_radiation_balance', 'proyDEM_%s.tif' %res1)    
    ETref_24_fileName = os.path.join(output_folder, 'Output_evapotranspiration', '%s_ETref_24_%s_%s_%s_%s_%s.tif' %(sensor1, res2, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))



    print '---------------------------------------------------------'
    print '-------------------- Open DEM ---------------------------'
    print '---------------------------------------------------------'

    pixel_spacing = int(res)

    # Open DEM and create Latitude and longitude files
    lat, lon, lat_fileName, lon_fileName = DEM_lat_lon(DEM_fileName, output_folder)
     
    # Reproject from Geog Coord Syst to UTM -
    # 1) DEM - Original DEM coordinates is Geographic: lat, lon
    dest, ulx_dem, lry_dem, lrx_dem, uly_dem, epsg_to = reproject_dataset(
                DEM_fileName, pixel_spacing, UTM_Zone = UTM_Zone)
    band = dest.GetRasterBand(1)   # Get the reprojected dem band
    ncol = dest.RasterXSize        # Get the reprojected dem column size
    nrow = dest.RasterYSize        # Get the reprojected dem row size
    shape = [ncol, nrow]
       
    # Read out the DEM band and print the DEM properties
    data_DEM = band.ReadAsArray(0, 0, ncol, nrow)
    #data_DEM[data_DEM<0] = 1
    print 'Projected DEM - '
    print '   Size: ', ncol, nrow
    print '   Upper Left corner x, y: ', ulx_dem, ',', uly_dem
    print '   Lower right corner x, y: ', lrx_dem, ',', lry_dem
  
    # 2) Latitude File - reprojection
    # Define output name of the latitude file        					
    lat_fileName_rep = os.path.join(output_folder, 'Output_radiation_balance',
                                        'latitude_proj_%s_%s_%s_%s_%s.tif' %(res1, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))

    # reproject latitude to the landsat projection	 and save as tiff file																																
    lat_rep, ulx_dem, lry_dem, lrx_dem, uly_dem, epsg_to = reproject_dataset(
               lat_fileName, pixel_spacing, UTM_Zone=UTM_Zone)
 
    # Get the reprojected latitude data															
    lat_proy = lat_rep.GetRasterBand(1).ReadAsArray(0, 0, ncol, nrow)
     
    # 3) Longitude file - reprojection
    # Define output name of the longitude file  				
    lon_fileName_rep = os.path.join(output_folder, 'Output_radiation_balance', 
								'longitude_proj_%s_%s_%s_%s_%s.tif' %(res1, year, str(mon).zfill(2), str(day).zfill(2), str(DOY).zfill(3)))

    # reproject longitude to the landsat projection	 and save as tiff file	
    lon_rep, ulx_dem, lry_dem, lrx_dem, uly_dem, epsg_to = reproject_dataset(lon_fileName, pixel_spacing, UTM_Zone)

    # Get the reprojected longitude data	
    lon_proy = lon_rep.GetRasterBand(1).ReadAsArray(0, 0, ncol, nrow)
       
    # Calculate slope and aspect from the reprojected DEM
    deg2rad, rad2deg, slope, aspect = Calc_Gradient(data_DEM, pixel_spacing)

    # Saving the reprojected maps
    save_GeoTiff_proy(dest, data_DEM, proyDEM_fileName, shape, nband = 1)
    save_GeoTiff_proy(dest, slope, slope_fileName, shape, nband = 1)
    save_GeoTiff_proy(dest, aspect, aspect_fileName, shape, nband = 1)
    save_GeoTiff_proy(lon_rep, lon_proy, lon_fileName_rep, shape, nband = 1)
    save_GeoTiff_proy(lat_rep, lat_proy, lat_fileName_rep, shape, nband = 1)

    # Calculation of extraterrestrial solar radiation for slope and aspect   
    Ra_mountain_24, Ra_inst, cos_zn, dr, phi, delta = Calc_Ra_Mountain(lon, DOY, hour, minutes, lon_proy, lat_proy, slope, aspect)

    # Save files created in module 1
    save_GeoTiff_proy(dest, cos_zn, cos_zn_fileName, shape, nband = 1)
    save_GeoTiff_proy(dest, Ra_mountain_24, radiation_fileName, shape, nband = 1)
    save_GeoTiff_proy(dest, Ra_inst, radiation_inst_fileName, shape, nband = 1 )
    save_GeoTiff_proy(dest, phi, phi_fileName, shape, nband = 1 )


    # 2) DEM
    DEM_resh = Reshape_Reproject_Input_data(proyDEM_fileName, dst_FileName_DEM, proyDEM_fileName)
    lsc = gdal.Open(proyDEM_fileName)
    
    #	Get the extend of the remaining landsat file	after clipping based on the DEM file	
    y_size_lsc = lsc.RasterYSize
    x_size_lsc = lsc.RasterXSize    
    shape_lsc = [x_size_lsc, y_size_lsc]   
    
    # 4) Reshaped instantaneous radiation
    Ra_inst = Reshape_Reproject_Input_data(radiation_inst_fileName, dst_FileName_Ra_inst, proyDEM_fileName)
       
    # 5) Reshaped psi
    phi = Reshape_Reproject_Input_data(phi_fileName, dst_FileName_phi, proyDEM_fileName)

    # 6) Reshape meteo data if needed (when path instead of number is input)
      
    # 6a) Instantaneous Temperature
    if Temp_inst_kind_of_data is 1:
        try:
            Temp_inst_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Temp_inst_input.tif')
            Temp_inst = Reshape_Reproject_Input_data(Temp_inst_name, Temp_inst_fileName, proyDEM_fileName)
        except:
            print 'ERROR: Check the instantenious Temperature input path in the meteo excel tab' 
                
    # 6b) Daily Temperature         
    if Temp_24_kind_of_data is 1:
        try:
            Temp_24_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Temp_24_input.tif')
            Temp_24 = Reshape_Reproject_Input_data(Temp_24_name, Temp_24_fileName, proyDEM_fileName)
        except:
            print 'ERROR: Check the daily Temperature input path in the meteo excel tab' 
                
    # 6c) Daily Relative Humidity       
    if RH_24_kind_of_data is 1:
        try:
            RH_24_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'RH_24_input.tif')
            RH_24 = Reshape_Reproject_Input_data(RH_24_name, RH_24_fileName, proyDEM_fileName)
        except:
            print 'ERROR: Check the instantenious Relative Humidity input path in the meteo excel tab' 

     # 6d) Instantaneous Relative Humidity      
    if RH_inst_kind_of_data is 1:
        try:
            RH_inst_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'RH_inst_input.tif')
            RH_inst = Reshape_Reproject_Input_data(RH_inst_name, RH_inst_fileName, proyDEM_fileName)  
        except:
            print 'ERROR: Check the daily Relative Humidity input path in the meteo excel tab' 
 
     # 6e) Daily wind speed      
    if Wind_24_kind_of_data is 1:
        try:
            Wind_24_fileName = os.path.join(output_folder, 'Output_radiation_balance','Wind_24_input.tif')
            Wind_24 = Reshape_Reproject_Input_data(Wind_24_name, Wind_24_fileName, proyDEM_fileName)
            Wind_24[Wind_24 < 1.5] = 1.5
        except:
            print 'ERROR: Check the daily wind input path in the meteo excel tab' 
  
     # 6f) Instantaneous wind speed              
    if Wind_inst_kind_of_data is 1:
        try:
            Wind_inst_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Wind_inst_input.tif')
            Wind_inst = Reshape_Reproject_Input_data(Wind_inst_name, Wind_inst_fileName, proyDEM_fileName)  
            Wind_inst[Wind_inst < 1.5] = 1.5
        except:
            print 'ERROR: Check the instantenious wind input path in the meteo excel tab' 

    # 6g) Daily incoming Radiation      
    if Method_Radiation_24 == 1:    
        if Rs_24_kind_of_data is 1:
            try:
                Net_radiation_daily_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Ra_24_input.tif')
                Rs_24 = Reshape_Reproject_Input_data(Rs_24_name, Net_radiation_daily_fileName, proyDEM_fileName)
            except:
                print 'ERROR: Check the daily net radiation input path in the meteo excel tab' 
 
    # 6h) Instantaneous incoming Radiation    
    if Method_Radiation_inst == 1:            
        if Rs_in_inst_kind_of_data is 1:
            try:
                Net_radiation_inst_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Ra_in_inst_input.tif')
                Rs_in_inst = Reshape_Reproject_Input_data(Rs_in_inst_name, Net_radiation_inst_fileName, proyDEM_fileName)
            except:
                print 'ERROR: Check the instanenious net radiation input path in the meteo excel tab' 
 
    # 6i) Daily Transmissivity
    if Method_Radiation_24 == 2:      
        if Transm_24_kind_of_data is 1:
            try:
                Transm_24_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Transm_24_input.tif')
                Transm_24 = Reshape_Reproject_Input_data(Transm_24_name, Transm_24_fileName, proyDEM_fileName)
            except:
                print 'ERROR: Check the daily transmissivity input path in the meteo excel tab' 

    # 6j) Instantaneous Transmissivity
    if Method_Radiation_inst == 2:     
        if Transm_inst_kind_of_data is 1:
            try:
                Transm_inst_fileName = os.path.join(output_folder, 'Output_radiation_balance', 'Transm_inst_input.tif')
                Transm_inst = Reshape_Reproject_Input_data(Transm_inst_name, Transm_inst_fileName, proyDEM_fileName)
            except:
                print 'ERROR: Check the instantenious transmissivity input path in the meteo excel tab' 

        print '---------------------------------------------------------'
    print '-------------------- Meteo part 1 -----------------------'
    print '---------------------------------------------------------'
   
    # Computation of some vegetation properties
    # 1)
    #constants:
    Temp_lapse_rate = float(temp_lapse)  # Temperature lapse rate (°K/m) - 0.0065(ORI)
    Gsc = 1367        # Solar constant (W / m2)   
    SB_const = 5.6703E-8  # Stefan-Bolzmann constant (watt/m2/°K4)
        
    # Atmospheric pressure for altitude:
    Pair = 101.3 * np.power((293 - Temp_lapse_rate * DEM_resh) / 293, 5.26)
     
    # Psychrometric constant (kPa / °C), FAO 56, eq 8.:
    Psychro_c = 0.665E-3 * Pair
       
    # Saturation Vapor Pressure at the air temperature (kPa):
    esat_inst = 0.6108 * np.exp(17.27 * Temp_inst / (Temp_inst + 237.3))
    esat_24=0.6108 * np.exp(17.27 * Temp_24 / (Temp_24 + 237.3))
      
    # Actual vapour pressure (kPa), FAO 56, eq 19.:
    eact_inst = RH_inst * esat_inst / 100
    eact_24 = RH_24 * esat_24 / 100
    print 'Instantaneous Saturation Vapor Pressure = ', '%0.3f (kPa)' % np.nanmean(esat_inst)
    print 'Instantaneous Actual vapour pressure =  ', '%0.3f (kPa)' % np.nanmean(eact_inst)
    print 'Daily Saturation Vapor Pressure = ', '%0.3f (kPa)' % np.nanmean(esat_24)
    print 'Daily Actual vapour pressure =  ', '%0.3f (kPa)' % np.nanmean(eact_24)

    print '---------------------------------------------------------'
    print '----------------------- Meteo ---------------------------'
    print '---------------------------------------------------------'

       
    # Precipitable water in the atmosphere (mm):
    # W = 0.14 * eact_inst * Pair + 2.1   # Garrison and Adler 1990
       
    # Slope of satur vapour pressure curve at air temp (kPa / °C)
    sl_es_24 = 4098 * esat_24 / np.power(   + 237.3, 2)
    air_dens = 1000 * Pair / (1.01 * (Temp_24 + 273.15) * 287)   
    # Daily 24 hr radiation - For flat terrain only !
    ws_angle = np.arccos(-np.tan(phi)*tan(delta))   # Sunset hour angle ws
       
    # Extraterrestrial daily radiation, Ra (W/m2):
    Ra24_flat = (Gsc/np.pi * dr * (ws_angle * np.sin(phi[nrow/2, ncol/2]) * np.sin(delta) +
                    np.cos(phi[nrow/2, ncol/2]) * np.cos(delta) * np.sin(ws_angle)))
       
    # calculate the daily radiation or daily transmissivity or daily surface radiation based on the method defined by the user
    if Method_Radiation_24==1:
       Transm_24 = Rs_24/Ra_mountain_24     
          
    if Method_Radiation_24==2:
       Rs_24 = Ra_mountain_24 * Transm_24   
       
    # Solar radiation from extraterrestrial radiation
    Rs_24_flat = Ra24_flat * Transm_24       
    print 'Mean Daily Transmissivity = %0.3f (W/m2)' % np.nanmean(Transm_24)
    print 'Mean Daily incoming net Radiation = %0.3f (W/m2)' % np.nanmean(Rs_24)
    print 'Mean Daily incoming net Radiation Flat Terrain = %0.3f (W/m2)' % np.nanmean(Rs_24_flat) 
	 						
    # If method of instantaneous radiation 1 is used than calculate the Transmissivity    
    if Method_Radiation_inst==1:
        Transm_corr=Rs_in_inst/Ra_inst
  
    # If method of instantaneous radiation 2 is used than calculate the instantaneous incomming Radiation        
    if Method_Radiation_inst==2:
        # calculate the transmissivity index for direct beam radiation 
        Transm_corr = Transm_inst + 2e-5 * DEM_resh
        # Instantaneous incoming short wave radiation (W/m2):
        Rs_in_inst = Ra_inst * Transm_corr  
       
    # Atmospheric emissivity, by Bastiaanssen (1995):
    Transm_corr[Transm_corr<0.001]=0.1
    Transm_corr[Transm_corr>1]=1
    atmos_emis = 0.85 * np.power(-np.log(Transm_corr), 0.09) 
      
    # Instantaneous incoming longwave radiation:
    lw_in_inst = atmos_emis * SB_const * np.power(Temp_inst + 273.15, 4) 
    print 'Instantaneous longwave incoming radiation = %0.3f (W/m2)' % np.nanmean(lw_in_inst)    
    print 'Atmospheric emissivity = %0.3f' % np.nanmean(atmos_emis) 
        

    # Net outgoing longwave radiation (W/m2):
    Rnl_24_FAO = (SB_const * np.power(Temp_24 + 273.15, 4) * (0.34-0.14 *
                  np.power(eact_24, 0.5)) * (1.35 * Transm_24 / 0.8 - 0.35))
    
    # calculate reference net radiation
    Rn_ref, rah_grass=Calc_Rn_Ref(Ra_mountain_24,Transm_24,Rnl_24_FAO,Wind_24)
    # calculate reference potential evaporation.
    ETref_24=Calc_Ref_Pot_ET(sl_es_24,Rn_ref,air_dens,esat_24,eact_24,rah_grass,Psychro_c)

    print '---------------------------------------------------------'
    print '------------Removing Intermediary files------------------'
    print '---------------------------------------------------------'

    try:
        shutil.rmtree(os.path.join(output_folder, 'Output_temporary'))
        shutil.rmtree(os.path.join(output_folder, 'Output_radiation_balance'))
    except OSError as e:
        print 'Error: folder does not exist'

    print '...................................................................'
    print '............................DONE!..................................'
    print '...................................................................'


############FUNCTIONS#############
#------------------------------------------------------------------------------
def DEM_lat_lon(DEM_fileName,output_folder):
    """
    This function retrieves information about the latitude and longitude of the
    DEM map. 
    
    """
    # name for output
    lat_fileName = os.path.join(output_folder, 'Output_radiation_balance','latitude.tif')
    lon_fileName = os.path.join(output_folder, 'Output_radiation_balance','longitude.tif')
                                
    g = gdal.Open(DEM_fileName)     # Open DEM
    geo_t = g.GetGeoTransform()     # Get the Geotransform vector:
    x_size = g.RasterXSize          # Raster xsize - Columns
    y_size = g.RasterYSize          # Raster ysize - Rows
    
    # create a longitude and a latitude array 
    lon = np.zeros((y_size, x_size))
    lat = np.zeros((y_size, x_size))
    for col in np.arange(x_size):
        lon[:, col] = geo_t[0] + col * geo_t[1] + geo_t[1]/2
        # ULx + col*(E-W pixel spacing) + E-W pixel spacing
    for row in np.arange(y_size):
        lat[row, :] = geo_t[3] + row * geo_t[5] + geo_t[5]/2
        # ULy + row*(N-S pixel spacing) + N-S pixel spacing,
        # negative as we will be counting from the UL corner
    
    # Define shape of the raster    
    shape = [x_size, y_size]
    
    # Save lat and lon files in geo- coordinates
    save_GeoTiff_proy(g, lat, lat_fileName, shape, nband=1)
    save_GeoTiff_proy(g, lon, lon_fileName, shape, nband=1)
    
    return(lat,lon,lat_fileName,lon_fileName)

#------------------------------------------------------------------------------
def reproject_dataset(dataset, pixel_spacing, UTM_Zone):
    """
    A sample function to reproject and resample a GDAL dataset from within
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:

    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """

    # 1) Open the dataset
    g = gdal.Open(dataset)
    if g is None:
        print 'input folder does not exist'

     # Define the EPSG code...
    EPSG_code = '326%02d' % UTM_Zone
    epsg_to = int(EPSG_code)

    # 2) Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    try:
        proj = g.GetProjection()
        Proj_in=proj.split('EPSG","')
        epsg_from=int((str(Proj_in[-1]).split(']')[0])[0:-1])		  
    except:
        epsg_from = int(4326)    # Get the Geotransform vector:
    geo_t = g.GetGeoTransform()
    
    # Vector components:
    # 0- The Upper Left easting coordinate (i.e., horizontal)
    # 1- The E-W pixel spacing
    # 2- The rotation (0 degrees if image is "North Up")
    # 3- The Upper left northing coordinate (i.e., vertical)
    # 4- The rotation (0 degrees)
    # 5- The N-S pixel spacing, negative as it is counted from the UL corner
    x_size = g.RasterXSize  # Raster xsize
    y_size = g.RasterYSize  # Raster ysize

    epsg_to = int(epsg_to)

    # 2) Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    inProj = Proj(init='epsg:%d' %epsg_from)
    outProj = Proj(init='epsg:%d' %epsg_to)

    nrow_skip = round((0.07*y_size)/2)
    ncol_skip = round((0.04*x_size)/2)
				
    # Up to here, all  the projection have been defined, as well as a
    # transformation from the from to the to
    ulx, uly = transform(inProj,outProj,geo_t[0], geo_t[3] + nrow_skip * geo_t[5])
    lrx, lry = transform(inProj,outProj,geo_t[0] + geo_t[1] * (x_size-ncol_skip),
                                        geo_t[3] + geo_t[5] * (y_size-nrow_skip))

    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName('MEM')

    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    col = int((lrx - ulx)/pixel_spacing)
    rows = int((uly - lry)/pixel_spacing)

    # Re-define lr coordinates based on whole number or rows and columns
    (lrx, lry) = (ulx + col * pixel_spacing, uly -
                  rows * pixel_spacing)
																		
    dest = mem_drv.Create('', col, rows, 1, gdal.GDT_Float32)
    
    if dest is None:
        print 'input folder to large for memory, clip input map'
     
   # Calculate the new geotransform
    new_geo = (ulx, pixel_spacing, geo_t[2], uly,
               geo_t[4], - pixel_spacing)
    
    # Set the geotransform
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(osng.ExportToWkt())
      
    # Perform the projection/resampling
    gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(),gdal.GRA_Bilinear)						

    return dest, ulx, lry, lrx, uly, epsg_to
#------------------------------------------------------------------------------
def reproject_dataset_example(dataset, dataset_example, method = 1):
   
    # open example dataset 
    g_ex = gdal.Open(dataset_example)
    try:
        proj = g_ex.GetProjection()
        Proj=proj.split('EPSG","')
        epsg_to=int((str(Proj[-1]).split(']')[0])[0:-1])		
    except:
        epsg_to = int(4326)       
      
    Y_raster_size = g_ex.RasterYSize				
    X_raster_size = g_ex.RasterXSize
				
    Geo = g_ex.GetGeoTransform()	
    ulx = Geo[0]
    uly = Geo[3]
    lrx = ulx + X_raster_size * Geo[1]				
    lry = uly + Y_raster_size * Geo[5]	
 
    # open dataset that must be transformed    
    g_in = gdal.Open(dataset)
    try:
        proj = g_in.GetProjection()
        Proj=proj.split('EPSG","')
        epsg_from=int((str(Proj[-1]).split(']')[0])[0:-1])		   
    except:
        epsg_from = int(4326)

    # Set the EPSG codes
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    # Create new raster			
    mem_drv = gdal.GetDriverByName('MEM')
    dest1 = mem_drv.Create('', X_raster_size, Y_raster_size, 1, gdal.GDT_Float32)
    dest1.SetGeoTransform(Geo)
    dest1.SetProjection(osng.ExportToWkt())
    
    # Perform the projection/resampling
    if method == 1:
        gdal.ReprojectImage(g_in, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_NearestNeighbour)
    if method == 2:
        gdal.ReprojectImage(g_in, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average)

    return(dest1, ulx, lry, lrx, uly, epsg_to)			

#------------------------------------------------------------------------------
def AngleSlope(a,b,c,w):
    '''
    Based on Richard G. Allen 2006
    Calculate the cos zenith angle by using the hour angle and constants
    '''
    angle = -a + b*np.cos(w) + c*np.sin(w)
    
    return(angle)    

#------------------------------------------------------------------------------
def Calc_Gradient(dataset,pixel_spacing):
    """
    This function calculates the slope and aspect of a DEM map.
    """
    # constants
    deg2rad = np.pi / 180.0  # Factor to transform from degree to rad
    rad2deg = 180.0 / np.pi  # Factor to transform from rad to degree
    
    # Calculate slope		
    x, y = np.gradient(dataset)
    slope = np.arctan(np.sqrt(np.square(x/pixel_spacing) + np.square(y/pixel_spacing))) * rad2deg
    
    # calculate aspect                  
    aspect = np.arctan2(y/pixel_spacing, -x/pixel_spacing) * rad2deg
    aspect = 180 + aspect

    return(deg2rad,rad2deg,slope,aspect)

#------------------------------------------------------------------------------

def Reshape_Reproject_Input_data(input_File_Name, output_File_Name, Example_extend_fileName):

   # Reproject the dataset based on the example       
   data_rep, ulx_dem, lry_dem, lrx_dem, uly_dem, epsg_to = reproject_dataset_example(
       input_File_Name, Example_extend_fileName)
   
   # Get the array information from the new created map
   band_data = data_rep.GetRasterBand(1) # Get the reprojected dem band
   ncol_data = data_rep.RasterXSize
   nrow_data = data_rep.RasterYSize
   shape_data=[ncol_data, nrow_data]
 
   # Save new dataset 
   #stats = band.GetStatistics(0, 1)
   data = band_data.ReadAsArray(0, 0, ncol_data, nrow_data)
   save_GeoTiff_proy(data_rep, data, output_File_Name, shape_data, nband=1)
   
   return(data)

#------------------------------------------------------------------------------

def save_GeoTiff_proy(src_dataset, dst_dataset_array, dst_fileName, shape_lsc, nband):
    """
    This function saves an array dataset in GeoTiff, using the parameters
    from the source dataset, in projected coordinates

    """
    dst_dataset_array	= np.float_(dst_dataset_array)		
    dst_dataset_array[dst_dataset_array<-9999] = np.nan					
    geotransform = src_dataset.GetGeoTransform()
    spatialreference = src_dataset.GetProjection()
    
    # create dataset for output
    fmt = 'GTiff'
    driver = gdal.GetDriverByName(fmt)
    dir_name = os.path.dirname(dst_fileName)
    
    # If the directory does not exist, make it.
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    dst_dataset = driver.Create(dst_fileName, shape_lsc[0], shape_lsc[1], nband,gdal.GDT_Float32)
    dst_dataset.SetGeoTransform(geotransform)
    dst_dataset.SetProjection(spatialreference)
    dst_dataset.GetRasterBand(1).SetNoDataValue(-9999)				
    dst_dataset.GetRasterBand(1).WriteArray(dst_dataset_array)
    dst_dataset = None

#------------------------------------------------------------------------------   
def Calc_Meteo(Rs_24,eact_24,Temp_24,Surf_albedo,cos_zn,dr,tir_emis,Surface_temp,water_mask,NDVI,Transm_24,SB_const,lw_in_inst,Rs_in_inst):
    """       
    Calculates the instantaneous Ground heat flux and solar radiation.
    """ 
    
    # Net shortwave radiation (W/m2):
    Rns_24 = Rs_24 * (1 - Surf_albedo)


    # Net outgoing longwave radiation (W/m2):
    Rnl_24_FAO = (SB_const * np.power(Temp_24 + 273.15, 4) * (0.34-0.14 *
                  np.power(eact_24, 0.5)) * (1.35 * Transm_24 / 0.8 - 0.35))
                  
    Rnl_24_Slob = 110 * Transm_24            
    print 'Mean Daily Net Radiation (Slob) = %0.3f (W/m2)' % np.nanmean(Rnl_24_Slob)    
				
    # Net 24 hrs radiation (W/m2):
    Rn_24_FAO = Rns_24 - Rnl_24_FAO          # FAO equation
    Rn_24_Slob = Rns_24 - Rnl_24_Slob       # Slob equation
    Rn_24 = (Rn_24_FAO + Rn_24_Slob) / 2  # Average
   

    # Instantaneous outgoing longwave radiation:
    lw_out_inst = tir_emis * SB_const * np.power(Surface_temp, 4)
    
    # Instantaneous net radiation
    rn_inst = (Rs_in_inst * (1 - Surf_albedo) + lw_in_inst - lw_out_inst -
               (1 - tir_emis) * lw_in_inst)
    # Instantaneous Soil heat flux
    g_inst = np.where(water_mask != 0.0, 0.4 * rn_inst,
                      ((Surface_temp - 273.15) * (0.0038 + 0.0074 * Surf_albedo) *
                       (1 - 0.978 * np.power(NDVI, 4))) * rn_inst)
    return(Rn_24,rn_inst,g_inst,Rnl_24_FAO)



#------------------------------------------------------------------------------    
def Calc_Rn_Ref(shape_lsc,water_mask,Rn_24,Ra_mountain_24,Transm_24,Rnl_24_FAO,Wind_24):
    """
    Function to calculate the net solar radiation
    """  
    # Aerodynamic resistance (s/m) for grass surface:
    rah_grass = 208.0 / Wind_24
    print  'rah_grass=', '%0.3f (s/m)' % np.nanmean(rah_grass)
    # Net radiation for grass Rn_ref, eq 40, FAO56:
    Rn_ref = Ra_mountain_24 * Transm_24 * (1 - 0.23) - Rnl_24_FAO  # Rnl avg(fao-slob)?
    return(Rn_ref, Refl_rad_water,rah_grass)

#------------------------------------------------------------------------------
def Calc_Ref_Pot_ET(sl_es_24,Rn_ref,air_dens,esat_24,eact_24,rah_grass,Psychro_c):
    """
    Function to calculate the reference potential evapotransporation and potential evaporation
    """ 
    Lhv = 2.45 * 1E6

    # Reference evapotranspiration- grass
    # Penman-Monteith of the combination equation (eq 3 FAO 56) (J/s/m2)
    LET_ref_24 = ((sl_es_24 * Rn_ref + air_dens * 1004 * (esat_24 - eact_24) /
                  rah_grass) / (sl_es_24 + Psychro_c * (1 + 70.0/rah_grass)))
    # Reference evaportranspiration (mm/d):
    ETref_24 = LET_ref_24 / (Lhv * 1000) * 86400000
    return(ETref_24)

#------------------------------------------------------------------------------  

def Run_command_window(argument):
    """
    This function runs the argument in the command window without showing cmd window

    Keyword Arguments:
    argument -- string, name of the adf file
    """  
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW		
    
    process = subprocess.Popen(argument, startupinfo=startupinfo, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    process.wait()  
    
    return()
if __name__ == "__main__":
    main()