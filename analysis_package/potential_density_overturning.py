import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import xarray as xr


from xmitgcm import open_mdsdataset
import xmitgcm
import ecco_v4_py as ecco


from netCDF4 import Dataset

import seawater

from analysis_package import plotting_functions
from analysis_package import open_datasets

from analysis_package import derive_potential_density_values_TEST
from analysis_package import ecco_masks
#from analysis_scripts import integrate_on_density_surfaces.py

from importlib import reload

data_dir = "./nctiles_monthly/"

UVELMASS_var = "UVELMASS"
VVELMASS_var = "VVELMASS"
BOLUS_UVEL_var = "BOLUS_UVEL"
BOLUS_VVEL_var = "BOLUS_VVEL"

# RHOAnoma: insitu density anomaly
RHOAnoma_var_str = "RHOAnoma"
# PHIHYD: insitu pressure anomaly with respect to the depth integral of gravity and reference density (g*rho_reference)
PHIHYD_var_str = "PHIHYD"
# SALT: insitu salinity (psu)
SALT_var_str = "SALT"
# THETA: potential pressure (C)
THETA_var_str = "THETA"

grid_path = "./ecco_grid/ECCOv4r3_grid.nc"
grid = xr.open_dataset(grid_path)



def perform_potential_density_overturning_calculation(time_slice,PDENS_U_ds,PDENS_V_ds,UVELMASS_ds_raw,VVELMASS_ds_raw,
														GM_PSIX, GM_PSIY):
	""" 

	Parameters
	----------
	

	Returns
	_______
	
	"""

	maskW = xr.open_dataarray("generic_masks/maskW.nc").load()
	maskS = xr.open_dataarray("generic_masks/maskS.nc").load()
	maskC = xr.open_dataarray("generic_masks/maskC.nc").load()
	southern_ocean_mask_W, southern_ocean_mask_S, so_atl_basin_mask_W, so_atl_basin_mask_S, so_indpac_basin_mask_W, so_indpac_basin_mask_S = ecco_masks.get_basin_masks(maskW, maskS, maskC)
	print("loaded basin masks")



	cds = grid.coords.to_dataset()
	grid_xmitgcm = ecco.ecco_utils.get_llc_grid(cds)

	transport_x = (UVELMASS_ds_raw["UVELMASS"]*grid["drF"]*grid["dyG"] )
	transport_y = (VVELMASS_ds_raw["VVELMASS"]*grid["drF"]*grid["dxG"] )

	# create infrastructure for integrating in depth space

	lat_vals = np.arange(-88,88)

	# create an empty array with a stretched depth dimension
	# Set the coordinates of the stretched depth dimension to potential density values..
	# add padding to either end of the pot. density coordinates
	# just trying with slightly coarser resolution 
	#(what pot density resolution is valid in this case?)
	pot_dens_coord = np.arange(1028.0,1033.9,0.2)

	pot_dens_coord = np.concatenate((np.asarray([1000.]),pot_dens_coord, np.arange(1034.0,1036,0.1), np.arange(1036.0,1038,0.02)))

	# set dimensions based on input dataset with modified vertical level spacing..
	pot_dens_dims = (len(time_slice),
	                 len(pot_dens_coord),
	                 len(lat_vals))

	empty_pot_coords_data = np.zeros(pot_dens_dims)
	# trying to make this as general as possible, but need to keep an eye on this..
	new_coords = [time_slice, pot_dens_coord, lat_vals]
	new_dims = ["time", "pot_rho", "lat"]

	# the potential density values have been interpolated to the edges of the grid cells
	pot_dens_array_x = PDENS_U_ds.PDENS.copy(deep=True)#*basin_maskW
	pot_dens_array_y = PDENS_V_ds.PDENS.copy(deep=True)#*basin_maskS

	bolus_trsp_x = (GM_PSIX.fillna(0)*grid["drF"]*grid["hFacW"])#*basin_maskW
	bolus_trsp_y = (GM_PSIY.fillna(0)*grid["drF"]*grid["hFacS"])#*basin_maskS

	depth_integrated_pdens_transport = xr.DataArray(data=empty_pot_coords_data,coords=new_coords,dims=new_dims)
	depth_integrated_pdens_transport.load()

	# Create an array for storing depth-integrated transport in native grid coordinates
	native_pot_dens_dims = (13,
						    len(time_slice),
							90,
							90,
							len(pot_dens_coord),
							)
	new_native_pot_dens_dims_x = ["tile","time","j","i_g","pot_rho"]
	new_native_pot_dens_dims_y = ["tile","time","j_g","i","pot_rho"]
	empty_native_pot_dens_data = np.zeros(native_pot_dens_dims)
	new_native_pot_dens_coords = (np.arange(0,13),
								  time_slice,
								  np.arange(0,90),
				  				  np.arange(0,90),
				  				  pot_dens_coord
				  				  )
	depth_integrated_native_pdens_U_transport = xr.DataArray(data=empty_native_pot_dens_data, 
														      	coords=new_native_pot_dens_coords, 
														   		dims=new_native_pot_dens_dims_x)
	depth_integrated_native_pdens_U_transport.load()
	depth_integrated_native_pdens_V_transport = depth_integrated_native_pdens_U_transport.copy(deep=True).rename({"i_g":"i","j":"j_g"})
	depth_integrated_native_pdens_V_transport.load()

	bolus_depth_integrated_native_pdens_U_transport = depth_integrated_native_pdens_U_transport.copy(deep=True)
	bolus_depth_integrated_native_pdens_V_transport = depth_integrated_native_pdens_V_transport.copy(deep=True)
	euler_depth_integrated_native_pdens_U_transport = depth_integrated_native_pdens_U_transport.copy(deep=True)
	euler_depth_integrated_native_pdens_V_transport = depth_integrated_native_pdens_V_transport.copy(deep=True)

	for density in pot_dens_coord:
	    print("Started " + str(density) + " surface for time slice " + str(time_slice))
	    potdens_stencil_x_0 = pot_dens_array_x > density
	    potdens_stencil_y_0 = pot_dens_array_y > density
	    # this step is critical to remove low density anomalies in the deep ocean from stencil...
	    # not sure what to do about those, ignoring them for now
	    potdens_stencil_x = potdens_stencil_x_0.cumsum(dim="k") > 0
	    potdens_stencil_y = potdens_stencil_y_0.cumsum(dim="k") > 0
	    print("got to checkpoint 0")

	    ############################################################################################################
	    ###########################################     START INTERPOLATION    #####################################
	    ############################################################################################################
	    # set end-appended value equal to 1 for subtraction step..
	    potdens_stencil_x_shifted_up_one_cell = xr.concat((potdens_stencil_x.isel(k=slice(1,50)),
	                                                       potdens_stencil_x.isel(k=49)),
	                                                      dim="k").assign_coords(k=np.arange(0,50))
	    potdens_stencil_y_shifted_up_one_cell = xr.concat((potdens_stencil_y.isel(k=slice(1,50)),
	                                                       potdens_stencil_y.isel(k=49)),
	                                                      dim="k").assign_coords(k=np.arange(0,50))
	    potdens_stencil_x_shifted_down_one_cell = xr.concat((potdens_stencil_x.isel(k=0)*0,
	                                                         potdens_stencil_x.isel(k=slice(0,49))),
	                                                        dim="k").assign_coords(k=np.arange(0,50))
	    potdens_stencil_y_shifted_down_one_cell = xr.concat((potdens_stencil_y.isel(k=0)*0,
	                                                         potdens_stencil_y.isel(k=slice(0,49))),
	                                                        dim="k").assign_coords(k=np.arange(0,50))

	    potdens_stencil_x_one_above_top_level = potdens_stencil_x_shifted_up_one_cell*1 - potdens_stencil_x*1
	    potdens_stencil_y_one_above_top_level = potdens_stencil_y_shifted_up_one_cell*1 - potdens_stencil_y*1
	    # get rid of trailing negative values that occur at the ocean's bottom boundary..
	    potdens_stencil_x_one_above_top_level = potdens_stencil_x_one_above_top_level.where(potdens_stencil_x_one_above_top_level > 0,
	                                                                                        other=0)
	    potdens_stencil_y_one_above_top_level = potdens_stencil_y_one_above_top_level.where(potdens_stencil_y_one_above_top_level > 0,
	                                                                                        other=0)

	    potdens_stencil_x_top_level = potdens_stencil_x*1 - potdens_stencil_x_shifted_down_one_cell*1
	    potdens_stencil_y_top_level = potdens_stencil_y*1 - potdens_stencil_y_shifted_down_one_cell*1
	    # turn zeros into nans..
	    # NOTE SOMETIMES YOU GET PROTRUSIONS OF DENSITY ANOMALIES THAT SEEM TO CREATE TWO DENSITY SURFACES, LEADING TO A VALUE OF
	    # 2 IN THE STENCIL.. I eliminated this using "potdens_stencil_x = potdens_stencil_x_0.cumsum(dim="k") > 0" a couple lines above.
	    potdens_stencil_x_top_level = potdens_stencil_x_top_level.where(potdens_stencil_x_top_level > 0, other=np.nan)
	    potdens_stencil_y_top_level = potdens_stencil_y_top_level.where(potdens_stencil_y_top_level > 0, other=np.nan)
	    potdens_stencil_x_one_above_top_level = potdens_stencil_x_one_above_top_level.where(potdens_stencil_x_one_above_top_level > 0,
	                                                                                        other=np.nan)
	    potdens_stencil_y_one_above_top_level = potdens_stencil_y_one_above_top_level.where(potdens_stencil_y_one_above_top_level > 0,
	                                                                                        other=np.nan)
	    # multiply depth values by -1 to make them positive..
	    depth_above_x_top_level_raw = (-1*potdens_stencil_x_one_above_top_level.fillna(0)*transport_x.Z).sum(dim="k")
	    depth_x_top_level_raw = (-1*potdens_stencil_x_top_level.fillna(0)*transport_x.Z).sum(dim="k",skipna=True)
	    depth_above_y_top_level_raw = (-1*potdens_stencil_y_one_above_top_level.fillna(0)*transport_y.Z).sum(dim="k",skipna=True)
	    depth_y_top_level_raw = (-1*potdens_stencil_y_top_level.fillna(0)*transport_y.Z).sum(dim="k",skipna=True)
	    # turn zeros into nans..
	    depth_above_x_top_level = depth_above_x_top_level_raw.where(depth_above_x_top_level_raw > 0, other=np.nan)
	    depth_x_top_level = depth_x_top_level_raw.where(depth_x_top_level_raw > 0, other=np.nan)
	    depth_above_y_top_level = depth_above_y_top_level_raw.where(depth_above_y_top_level_raw > 0, other=np.nan)
	    depth_y_top_level = depth_y_top_level_raw.where(depth_y_top_level_raw > 0, other=np.nan)

	    thickness_above_x_top_level_raw = (potdens_stencil_x_one_above_top_level.fillna(0)*grid["drF"]).sum(dim="k")
	    thickness_x_top_level_raw = (potdens_stencil_x_top_level.fillna(0)*grid["drF"]).sum(dim="k")
	    thickness_above_y_top_level_raw = (potdens_stencil_y_one_above_top_level.fillna(0)*grid["drF"]).sum(dim="k")
	    thickness_y_top_level_raw = (potdens_stencil_y_top_level.fillna(0)*grid["drF"]).sum(dim="k")
	    # turn zeros into nans..
	    thickness_above_x_top_level = thickness_above_x_top_level_raw.where(thickness_above_x_top_level_raw > 0, other=np.nan)
	    thickness_x_top_level = thickness_x_top_level_raw.where(thickness_x_top_level_raw > 0, other=np.nan)
	    thickness_above_y_top_level = thickness_above_y_top_level_raw.where(thickness_above_y_top_level_raw > 0, other=np.nan)
	    thickness_y_top_level = thickness_y_top_level_raw.where(thickness_y_top_level_raw > 0, other=np.nan)    
	    
	    potdens_above_x_top_level = (potdens_stencil_x_one_above_top_level.fillna(0)*pot_dens_array_x.fillna(0)).sum(dim="k")
	    potdens_x_top_level = (potdens_stencil_x_top_level.fillna(0)*pot_dens_array_x.fillna(0)).sum(dim="k")
	    potdens_above_y_top_level = (potdens_stencil_y_one_above_top_level.fillna(0)*pot_dens_array_y.fillna(0)).sum(dim="k")
	    potdens_y_top_level = (potdens_stencil_y_top_level.fillna(0)*pot_dens_array_y.fillna(0)).sum(dim="k")
	    # turn zeros into nans..
	    potdens_above_x_top_level = potdens_above_x_top_level.where(potdens_above_x_top_level > 0, other=np.nan)
	    potdens_x_top_level = potdens_x_top_level.where(potdens_x_top_level > 0, other=np.nan)
	    potdens_above_y_top_level = potdens_above_y_top_level.where(potdens_above_y_top_level > 0, other=np.nan)
	    potdens_y_top_level = potdens_y_top_level.where(potdens_y_top_level > 0, other=np.nan)
	    
	    print("got to checkpoint 1")
	    # need to calculate transport per m so divide by cell thickness
	    transport_above_x_top_level = (potdens_stencil_x_one_above_top_level.fillna(0)*transport_x).sum(dim="k")
	    transport_x_top_level = (potdens_stencil_x_top_level.fillna(0)*transport_x).sum(dim="k")
	    transport_above_y_top_level = (potdens_stencil_y_one_above_top_level.fillna(0)*transport_y).sum(dim="k")
	    transport_y_top_level = (potdens_stencil_y_top_level.fillna(0)*transport_y).sum(dim="k")
	    
	    transport_above_x_top_level = transport_above_x_top_level.where(transport_above_x_top_level !=0, other=np.nan)    
	    transport_x_top_level = transport_x_top_level.where(transport_x_top_level != 0, other=np.nan)
	    transport_above_y_top_level = transport_above_y_top_level.where(transport_above_y_top_level !=0, other=np.nan)
	    transport_y_top_level = transport_y_top_level.where(transport_y_top_level !=0, other=np.nan)
	    
	    bolus_strfn_x_one_above_top_level = (potdens_stencil_x_one_above_top_level.fillna(0)*bolus_trsp_x["GM_PsiX"]).sum(dim="k")
	    bolus_strfn_x_top_level = (potdens_stencil_x_top_level.fillna(0)*bolus_trsp_x["GM_PsiX"].fillna(0)).sum(dim="k")
	    bolus_strfn_y_one_above_top_level = (potdens_stencil_y_one_above_top_level.fillna(0)*bolus_trsp_y["GM_PsiY"]).sum(dim="k")
	    bolus_strfn_y_top_level = (potdens_stencil_y_top_level.fillna(0)*bolus_trsp_y["GM_PsiY"].fillna(0)).sum(dim="k")

	    depth_above_x_top_level = depth_above_x_top_level.where(depth_above_x_top_level != 0, other = np.nan)
	    depth_x_top_level = depth_x_top_level.where(depth_x_top_level != 0, other=np.nan)
	    
	    depth_potdens_slope_x = (depth_above_x_top_level - depth_x_top_level)/(potdens_above_x_top_level - potdens_x_top_level)                                                
	    depth_potdens_slope_y = (depth_above_y_top_level - depth_y_top_level)/(potdens_above_y_top_level - potdens_y_top_level)
	    
	    bolus_depth_slope_x = (bolus_strfn_x_one_above_top_level - bolus_strfn_x_top_level)/(depth_above_x_top_level - depth_x_top_level)
	    bolus_depth_slope_y = (bolus_strfn_y_one_above_top_level - bolus_strfn_y_top_level)/(depth_above_y_top_level - depth_y_top_level)

	    # this is an issue... need to account for those low desnity protrusions..
	    h_array_x_0 = (density - potdens_x_top_level)*depth_potdens_slope_x
	    h_array_x = -1*h_array_x_0.where(h_array_x_0 < 0, other=0)
	    h_array_y_0 = (density - potdens_y_top_level)*depth_potdens_slope_y
	    h_array_y = -1*h_array_y_0.where(h_array_y_0 < 0, other=0)
	    
	    bolus_x_at_interp_lvl = -1*h_array_x*bolus_depth_slope_x  + bolus_strfn_x_top_level
	    bolus_y_at_interp_lvl = -1*h_array_y*bolus_depth_slope_y + bolus_strfn_y_top_level
	    
	    bolus_x_at_interp_lvl.load()
	    bolus_y_at_interp_lvl.load()

	    print("got to checkpoint 2")
	    half_thickness_x_top_level = (potdens_stencil_x_top_level.fillna(0)*grid.drF/2.).sum(dim="k")
	    half_thickness_y_top_level = (potdens_stencil_y_top_level.fillna(0)*grid.drF/2.).sum(dim="k")
	    half_thickness_x_one_above_top_level = (potdens_stencil_x_one_above_top_level.fillna(0)*grid.drF/2.).sum(dim="k")
	    half_thickness_y_one_above_top_level = (potdens_stencil_y_one_above_top_level.fillna(0)*grid.drF/2.).sum(dim="k")
	    
	    # "overshoot" is how high the density level protrudes into the cell above the top stencil cell, if it is higher
	    # "undershoot" is how low the density level is below the top of the top stencil cell, if it is lower
	    overshoot_x_0 = h_array_x - half_thickness_x_top_level
	    overshoot_x = overshoot_x_0.where(overshoot_x_0 > 0).fillna(0)
	    undershoot_x = overshoot_x_0.where(overshoot_x_0 <= 0).fillna(0)
	    overshoot_y_0 = h_array_y - half_thickness_y_top_level
	    overshoot_y = overshoot_y_0.where(overshoot_y_0 > 0).fillna(0)
	    undershoot_y = overshoot_y_0.where(overshoot_y_0 <= 0).fillna(0)
	    
	    # remember we are interpolating from the center of the top cell
	    percent_top_filled_x = (half_thickness_x_top_level + undershoot_x)/(half_thickness_x_top_level*2)
	    percent_top_filled_y = (half_thickness_y_top_level + undershoot_y)/(half_thickness_y_top_level*2)
	    
	    percent_one_above_top_filled_x = overshoot_x/(half_thickness_x_one_above_top_level*2)
	    percent_one_above_top_filled_y = overshoot_y/(half_thickness_y_one_above_top_level*2)  
	    
	    trsp_interpolated_x = (percent_top_filled_x*transport_x_top_level).fillna(0) + (percent_one_above_top_filled_x*transport_above_x_top_level).fillna(0)
	    trsp_interpolated_y = (percent_top_filled_y*transport_y_top_level).fillna(0) + (percent_one_above_top_filled_y*transport_above_y_top_level).fillna(0)
	    
	    # "transport_integral_x/y" is the vertical sum of the interpolated grid cell tranposrt
	    trsp_interpolated_x.load()
	    trsp_interpolated_y.load()
	    ############################################################################################################
	    ###########################################     END INTERPOLATION    #######################################
	    ############################################################################################################    
	    
	    # split the top cell in half since we are putting it into the interpolation,
	    # but only in cases where there actually is a cell above it.
	    depth_integrated_trsp_x_0 = transport_x*(potdens_stencil_x.where(potdens_stencil_x>0,other=np.nan)) - (transport_x*potdens_stencil_x_top_level.where(potdens_stencil_x_one_above_top_level>0,other=np.nan)/2.).fillna(0)
	    depth_integrated_trsp_x_0.load()
	    depth_integrated_trsp_x = depth_integrated_trsp_x_0.sum(dim='k') + trsp_interpolated_x.fillna(0) - bolus_x_at_interp_lvl.fillna(0)
	    depth_integrated_trsp_y_0 = transport_y*(potdens_stencil_y.where(potdens_stencil_y>0,other=np.nan)) - (transport_y*potdens_stencil_y_top_level.where(potdens_stencil_y_one_above_top_level>0,other=np.nan)/2.).fillna(0)
	    depth_integrated_trsp_y_0.load()
	    depth_integrated_trsp_y = depth_integrated_trsp_y_0.sum(dim='k') + trsp_interpolated_y.fillna(0) - bolus_y_at_interp_lvl.fillna(0)
	    
	    bolus_depth_integrated_native_pdens_U_transport.loc[{"pot_rho":density}] = -1*bolus_x_at_interp_lvl.fillna(0)
	    bolus_depth_integrated_native_pdens_V_transport.loc[{"pot_rho":density}] = -1*bolus_y_at_interp_lvl.fillna(0)
	    euler_depth_integrated_native_pdens_U_transport.loc[{"pot_rho":density}] = depth_integrated_trsp_x_0.sum(dim='k') + trsp_interpolated_x.fillna(0)
	    euler_depth_integrated_native_pdens_U_transport.loc[{"pot_rho":density}] = depth_integrated_trsp_y_0.sum(dim='k') + trsp_interpolated_y.fillna(0)

	    depth_integrated_native_pdens_V_transport.loc[{"pot_rho":density}] = depth_integrated_trsp_y.values
	    depth_integrated_native_pdens_U_transport.loc[{"pot_rho":density}] = depth_integrated_trsp_x.values

	depth_integrated_native_pdens_U_transport.load()
	depth_integrated_native_pdens_V_transport.load()
	
	return_tuple = (depth_integrated_native_pdens_U_transport,
					depth_integrated_native_pdens_V_transport,
					bolus_depth_integrated_native_pdens_U_transport,
					bolus_depth_integrated_native_pdens_V_transport,
					euler_depth_integrated_native_pdens_U_transport,
					euler_depth_integrated_native_pdens_V_transport)

	return return_tuple

	# depth_integrated_pdens.to_netcdf("./depth_integrated_pdens_TEST11.nc")






