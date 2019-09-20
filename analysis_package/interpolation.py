def interpolate_c_to_v(data_array,grid):
    # need to interpolate between c values and corresponding values shifted downwards one cell unit
    # in the v direction
    print("checkpoint 1")
    interpolated_v_data = data_array.copy(deep=True)
    j_distance_between_c_points = data_array.copy(deep=True)
    
    print("checkpoint 2")
    interpolated_v_data.loc[{"tile":0}] = data_array.isel(tile=0) - np.concatenate((data_array.isel(tile=0,j=slice(89,90)).values*0,data_array.isel(tile=0,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":1}] = data_array.isel(tile=1) - np.concatenate((data_array.isel(tile=0,j=slice(89,90)).values,data_array.isel(tile=1,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":2}] = data_array.isel(tile=2) - np.concatenate((data_array.isel(tile=1,j=slice(89,90)).values,data_array.isel(tile=2,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":3}] = data_array.isel(tile=3) - np.concatenate((data_array.isel(tile=3,j=slice(89,90)).values*0,data_array.isel(tile=3,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":4}] = data_array.isel(tile=4) - np.concatenate((data_array.isel(tile=3,j=slice(89,90)).values,data_array.isel(tile=4,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":5}] = data_array.isel(tile=5) - np.concatenate((data_array.isel(tile=4,j=slice(89,90)).values,data_array.isel(tile=5,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":6}] = data_array.isel(tile=6) - np.concatenate((data_array.isel(tile=5,j=slice(89,90)).values,data_array.isel(tile=6,j=slice(0,89)).values),axis=2) 
    interpolated_v_data.loc[{"tile":7}] = data_array.isel(tile=7) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=5,i=slice(89,90)).values,axis=2),axes=[0,1,3,2]),data_array.isel(tile=7,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":8}] = data_array.isel(tile=8) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=4,i=slice(89,90)).values,axis=2),axes=[0,1,3,2]),data_array.isel(tile=8,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":9}] = data_array.isel(tile=9) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=3,i=slice(89,90)).values,axis=2),axes=[0,1,3,2]),data_array.isel(tile=9,j=slice(0,89)).values),axis=2)            
    interpolated_v_data.loc[{"tile":10}] = data_array.isel(tile=10) - np.concatenate((data_array.isel(tile=7,j=slice(89,90)).values,data_array.isel(tile=10,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":11}] = data_array.isel(tile=11) - np.concatenate((data_array.isel(tile=8,j=slice(89,90)).values,data_array.isel(tile=11,j=slice(0,89)).values),axis=2)    
    interpolated_v_data.loc[{"tile":12}] = data_array.isel(tile=12) - np.concatenate((data_array.isel(tile=9,j=slice(89,90)).values,data_array.isel(tile=12,j=slice(0,89)).values),axis=2)    
    
    print("checkpoint 3")
    j_distance_between_c_points.loc[{"tile":0}] = (grid.dyG.isel(tile=0) + np.concatenate((grid.dyG.isel(tile=0,j=slice(89,90)).values*0,grid.dyG.isel(tile=0,j=slice(0,89)).values),axis=0))/2.  
    j_distance_between_c_points.loc[{"tile":1}] = (grid.dyG.isel(tile=1) + np.concatenate((grid.dyG.isel(tile=0,j=slice(89,90)).values,grid.dyG.isel(tile=1,j=slice(0,89)).values),axis=0))/2.    
    j_distance_between_c_points.loc[{"tile":2}] = (grid.dyG.isel(tile=2) + np.concatenate((grid.dyG.isel(tile=1,j=slice(89,90)).values,grid.dyG.isel(tile=2,j=slice(0,89)).values),axis=0))/2.        
    j_distance_between_c_points.loc[{"tile":3}] = (grid.dyG.isel(tile=3) + np.concatenate((grid.dyG.isel(tile=3,j=slice(89,90)).values*0,grid.dyG.isel(tile=3,j=slice(0,89)).values),axis=0))/2.    
    j_distance_between_c_points.loc[{"tile":4}] = (grid.dyG.isel(tile=4) + np.concatenate((grid.dyG.isel(tile=3,j=slice(89,90)).values,grid.dyG.isel(tile=4,j=slice(0,89)).values),axis=0))/2.    
    j_distance_between_c_points.loc[{"tile":5}] = (grid.dyG.isel(tile=5) + np.concatenate((grid.dyG.isel(tile=4,j=slice(89,90)).values,grid.dyG.isel(tile=5,j=slice(0,89)).values),axis=0))/2.    
    j_distance_between_c_points.loc[{"tile":6}] = (grid.dyG.isel(tile=6) + np.concatenate((grid.dyG.isel(tile=5,j=slice(89,90)).values,grid.dyG.isel(tile=6,j=slice(0,89)).values),axis=0))/2.   
    j_distance_between_c_points.loc[{"tile":7}] = (grid.dyG.isel(tile=7) + np.concatenate((np.transpose(np.flip(grid.dyG.isel(tile=5,i_g=slice(89,90)).values,axis=0),axes=[1,0]),grid.dyG.isel(tile=7,j=slice(0,89)).values),axis=0))/2.    
    j_distance_between_c_points.loc[{"tile":8}] = (grid.dyG.isel(tile=8) + np.concatenate((np.transpose(np.flip(grid.dyG.isel(tile=4,i_g=slice(89,90)).values,axis=0),axes=[1,0]),grid.dyG.isel(tile=8,j=slice(0,89)).values),axis=0))/2.    
    j_distance_between_c_points.loc[{"tile":9}] = (grid.dyG.isel(tile=9) + np.concatenate((np.transpose(np.flip(grid.dyG.isel(tile=3,i_g=slice(89,90)).values,axis=0),axes=[1,0]),grid.dyG.isel(tile=9,j=slice(0,89)).values),axis=0))/2.        
    j_distance_between_c_points.loc[{"tile":10}] = (grid.dyG.isel(tile=10) + np.concatenate((grid.dyG.isel(tile=7,j=slice(89,90)).values,grid.dyG.isel(tile=10,j=slice(0,89)).values),axis=0))/2.   
    j_distance_between_c_points.loc[{"tile":11}] = (grid.dyG.isel(tile=11) + np.concatenate((grid.dyG.isel(tile=8,j=slice(89,90)).values,grid.dyG.isel(tile=11,j=slice(0,89)).values),axis=0))/2.   
    j_distance_between_c_points.loc[{"tile":12}] = (grid.dyG.isel(tile=12) + np.concatenate((grid.dyG.isel(tile=9,j=slice(89,90)).values,grid.dyG.isel(tile=12,j=slice(0,89)).values),axis=0))/2.    
    
    print("checkpoint 4")
    data_slope_between_c_points = interpolated_v_data.rename({"j":"j_g"})/j_distance_between_c_points.rename({"j":"j_g"})
    print("checkpoint 5")
    data_at_v_points = data_slope_between_c_points*grid.dyG.rename({"j":"j_g","i_g":"i"})/2 + data_array.rename({"j":"j_g"})
    
    return data_at_v_points, data_slope_between_c_points, j_distance_between_c_points



def interpolate_c_to_u(data_array,grid):
    # need to interpolate between c values and corresponding values shifted downwards one cell unit
    # in the v direction
    print("checkpoint 1")
    interpolated_u_data = data_array.copy(deep=True)
    i_distance_between_c_points = data_array.copy(deep=True)*0
    
    print("checkpoint 2")
    interpolated_u_data.loc[{"tile":0}] = data_array.isel(tile=0) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=12,j=slice(89,90)).values,axis=3),axes=[0,1,3,2]),data_array.isel(tile=0,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":1}] = data_array.isel(tile=1) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=11,j=slice(89,90)).values,axis=3),axes=[0,1,3,2]),data_array.isel(tile=1,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":2}] = data_array.isel(tile=2) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=10,j=slice(89,90)).values,axis=3),axes=[0,1,3,2]),data_array.isel(tile=2,i=slice(0,89)).values),axis=3) 
    interpolated_u_data.loc[{"tile":3}] = data_array.isel(tile=3) - np.concatenate((data_array.isel(tile=0,i=slice(89,90)).values,data_array.isel(tile=3,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":4}] = data_array.isel(tile=4) - np.concatenate((data_array.isel(tile=1,i=slice(89,90)).values,data_array.isel(tile=4,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":5}] = data_array.isel(tile=5) - np.concatenate((data_array.isel(tile=2,i=slice(89,90)).values,data_array.isel(tile=5,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":6}] = data_array.isel(tile=6) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=2,j=slice(89,90)).values,axis=3),axes=[0,1,3,2]),data_array.isel(tile=6,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":7}] = data_array.isel(tile=7) - np.concatenate((data_array.isel(tile=6,i=slice(89,90)).values,data_array.isel(tile=7,i=slice(0,89)).values),axis=3)     
    interpolated_u_data.loc[{"tile":8}] = data_array.isel(tile=8) - np.concatenate((data_array.isel(tile=7,i=slice(89,90)).values,data_array.isel(tile=8,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":9}] = data_array.isel(tile=9) - np.concatenate((data_array.isel(tile=8,i=slice(89,90)).values,data_array.isel(tile=9,i=slice(0,89)).values),axis=3)
    interpolated_u_data.loc[{"tile":10}] = data_array.isel(tile=10) - np.concatenate((np.transpose(np.flip(data_array.isel(tile=6,j=slice(89,90)).values,axis=3),axes=[0,1,3,2]),data_array.isel(tile=10,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":11}] = data_array.isel(tile=11) - np.concatenate((data_array.isel(tile=10,i=slice(89,90)).values,data_array.isel(tile=11,i=slice(0,89)).values),axis=3)    
    interpolated_u_data.loc[{"tile":12}] = data_array.isel(tile=12) - np.concatenate((data_array.isel(tile=11,i=slice(89,90)).values,data_array.isel(tile=12,i=slice(0,89)).values),axis=3)    
    
    print("checkpoint 3")
    i_distance_between_c_points.loc[{"tile":0}] = (grid.dxG.isel(tile=0) + np.concatenate((np.transpose(np.flip(grid.dxG.isel(tile=12,j_g=slice(89,90)).values,axis=1),axes=[1,0]),grid.dxG.isel(tile=0,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":1}] = (grid.dxG.isel(tile=1) + np.concatenate((np.transpose(np.flip(grid.dxG.isel(tile=11,j_g=slice(89,90)).values,axis=1),axes=[1,0]),grid.dxG.isel(tile=1,i=slice(0,89)).values),axis=1))/2.   
    i_distance_between_c_points.loc[{"tile":2}] = (grid.dxG.isel(tile=2) + np.concatenate((np.transpose(np.flip(grid.dxG.isel(tile=10,j_g=slice(89,90)).values,axis=1),axes=[1,0]),grid.dxG.isel(tile=2,i=slice(0,89)).values),axis=1))/2. 
    i_distance_between_c_points.loc[{"tile":3}] = (grid.dxG.isel(tile=3) + np.concatenate((grid.dxG.isel(tile=0,i=slice(89,90)).values,grid.dxG.isel(tile=3,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":4}] = (grid.dxG.isel(tile=4) + np.concatenate((grid.dxG.isel(tile=1,i=slice(89,90)).values,grid.dxG.isel(tile=4,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":5}] = (grid.dxG.isel(tile=5) + np.concatenate((grid.dxG.isel(tile=2,i=slice(89,90)).values,grid.dxG.isel(tile=5,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":6}] = (grid.dxG.isel(tile=6) + np.concatenate((np.transpose(np.flip(grid.dxG.isel(tile=2,j_g=slice(89,90)).values,axis=1),axes=[1,0]),grid.dxG.isel(tile=6,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":7}] = (grid.dxG.isel(tile=7) + np.concatenate((grid.dxG.isel(tile=6,i=slice(89,90)).values,grid.dxG.isel(tile=7,i=slice(0,89)).values),axis=1))/2.     
    i_distance_between_c_points.loc[{"tile":8}] = (grid.dxG.isel(tile=8) + np.concatenate((grid.dxG.isel(tile=7,i=slice(89,90)).values,grid.dxG.isel(tile=8,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":9}] = (grid.dxG.isel(tile=9) + np.concatenate((grid.dxG.isel(tile=8,i=slice(89,90)).values,grid.dxG.isel(tile=9,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":10}] = (grid.dxG.isel(tile=10) + np.concatenate((np.transpose(np.flip(grid.dxG.isel(tile=6,j_g=slice(89,90)).values,axis=1),axes=[1,0]),grid.dxG.isel(tile=10,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":11}] = (grid.dxG.isel(tile=11) + np.concatenate((grid.dxG.isel(tile=10,i=slice(89,90)).values,grid.dxG.isel(tile=11,i=slice(0,89)).values),axis=1))/2.    
    i_distance_between_c_points.loc[{"tile":12}] = (grid.dxG.isel(tile=12) + np.concatenate((grid.dxG.isel(tile=11,i=slice(89,90)).values,grid.dxG.isel(tile=12,i=slice(0,89)).values),axis=1))/2.       

    print("checkpoint 4")
    data_slope_between_c_points = interpolated_u_data.rename({"i":"i_g"})/i_distance_between_c_points.rename({"i":"i_g"})
    print("checkpoint 5")
    data_at_u_points = data_slope_between_c_points*grid.dxG.rename({"j_g":"j","i":"i_g"})/2. + data_array.rename({"i":"i_g"})
    
    
    return data_at_u_points, data_slope_between_c_points, i_distance_between_c_points