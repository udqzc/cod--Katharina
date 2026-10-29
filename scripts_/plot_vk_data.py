import numpy as np
import matplotlib.pyplot as plt




def plot_reflected_light(img_array, img_width, img_height, calibration, colormap='gray', scale='absolute'): #271217
    '''
    function for plotting the reflected light image of a VK4 file
    the function uses the plot_reflected_light function to plot the image

    Parameters:
    img_array: np.array, the image data
    img_width: int, the width of the image
    img_height: int, the height of the image
    calibration: int, the calibration value of the image, can be found in the metadata of the VK4 file
    colormap: str, the colormap to use for the plot
    scale: str, the scale of the plot, must be 'absolute' or 'pixels'

    Returns:
    ax: matplotlib axis object, the axis object of the plot
    '''
    assert scale in ['absolute', 'pixels'], 'scale must be either "absolute" or "pixels"'
    fig, ax = plt.subplots(figsize=(8, 8))

    if scale == 'absolute':
        ax.imshow(
            img_array, 
            cmap=colormap, 
            extent=[0, img_width*calibration/1e6, 
                    0, img_height*calibration/1e6]
        )
        #ax.set_xticks(np.linspace(0, img_width-1, 5))
        #ax.set_yticks(np.linspace(0, img_height-1, 5))
        #ax.set_xticklabels(np.round(np.linspace(0, (img_width-1)*calibration/1e6, 5), 2))
        #ax.set_yticklabels(np.round(np.linspace(0, (img_height-1)*calibration/1e6, 5), 2))
        ax.tick_params(axis='both', labelsize=18)
        ax.set_xlabel('X (µm)', fontsize=20)
        ax.set_ylabel('Y (µm)', fontsize=20)

    else:
        ax.imshow(img_array, cmap=colormap)
        ax.tick_params(axis='both', labelsize=18)
        ax.set_xlabel('X (pixels)', fontsize=20)
        ax.set_ylabel('Y (pixels)', fontsize=20)
    #ax.set_title('Reflected Light Image')

    return ax




def plot_vk4_reflected_light(Vk4File, colormap = 'gray', scale='absolute'):
    '''
    function for plotting the reflected light image of a VK4 file
    the function uses the plot_reflected_light function to plot the image

    Parameters:
    Vk4File: dict, a dictionary containing the data of a VK4 file
    colormap: str, the colormap to use for the plot
    scale: str, the scale of the plot, must be 'absolute' or 'pixels'

    Returns:
    ax: matplotlib axis object, the axis object of the plot
    '''

    img_data = Vk4File['img_light_data']
    img_width = img_data['width']
    img_height = img_data['height']
    img_array = img_data['data']

    calibration = Vk4File['measurement_conditions']['x_length_per_pixel']
    img_array = img_array.reshape(img_height, img_width)

    return plot_reflected_light(img_array, img_width, img_height, calibration, colormap, scale)




def plot_height_data(img_array, img_width, img_height, calibration, colormap='viridis', scale='absolute'):
    '''
    function for plotting the height image of a VK4 file

    Parameters:
    img_array: np.array, the image data
    img_width: int, the width of the image
    img_height: int, the height of the image
    calibration: int, the calibration value of the image, can be found in the metadata of the VK4 file
    colormap: str, the colormap to use for the plot
    scale: str, the scale of the plot, must be 'absolute' or 'pixels'

    Returns:
    ax: matplotlib axis object, the axis object of the plot
    '''
    assert scale in ['absolute', 'pixels'], 'scale must be either "absolute" or "pixels"'

    fig, ax = plt.subplots(figsize=(10, 10))


    # set colorbar scale
    if np.max(np.abs(img_array)) <= 0.5:
        img_array = img_array*1e3
        cbar_label = 'Height (nm)'
    else:
        cbar_label = 'Height (µm)'    


    if scale == 'absolute':
        im = ax.imshow(
            img_array,
            cmap=colormap,
            extent=[0, img_width*calibration/1e6,
                    0, img_height*calibration/1e6]
        )
        ax.tick_params(axis='both', labelsize=18)
        ax.set_xlabel('X (µm)', fontsize=20)
        ax.set_ylabel('Y (µm)', fontsize=20)

        #ax.set_xticks(np.linspace(0, img_width-1, 10))
        #ax.set_yticks(np.linspace(0, img_height-1, 10))
        #ax.set_xticklabels(np.round(np.linspace(0, (img_width-1)*calibration/1e6, 10), 3))
        #ax.set_yticklabels(np.round(np.linspace(0, (img_height-1)*calibration/1e6, 10), 3))
        
    else:
        im = ax.imshow(img_array, cmap=colormap)
        ax.ticks_params(labelsize=18)
        ax.set_xlabel('X (pixels)', fontsize=20)
        ax.set_ylabel('Y (pixels)', fontsize=20)
        

    cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.5)
    
    #vmin = np.nanmin(img_array)
    #vmax = np.nanmax(img_array)

    vmin, vmax = im.get_clim()
    
    positions = np.linspace(vmin, vmax, 7)  # min + 5 interior + max

    ticks = [vmin]
    ticks += [int(round(x)) for x in positions[1:-1]]
    ticks += [vmax]

    # remove duplicates if a limit is already an integer
    ticks = np.unique(ticks)

    cbar.set_ticks(ticks)
    cbar.ax.tick_params(labelsize=18)
    cbar.set_label(cbar_label, fontsize=20)

    #cbar.set_ticks(np.arange(int(np.floor(vmin)), int(np.ceil(vmax))+1, 1))
    #cbar.set_ticks(np.arange(int(np.floor(img_array.min()))+2, int(np.ceil(img_array.max())), 5))
    #ax.set_title('Height Image', fontsize=18)
    
    return ax




def plot_vk4_height(Vk4File, data_type='original', colormap = 'viridis', scale='absolute'):
    '''
    function for plotting the height image of a VK4 file
    the function uses the plot_height_data function to plot the image

    Parameters:
    Vk4File: dict, a dictionary containing the data of a VK4 file
    data_type: str, the type of height data to plot, must be 'original', 'baseplane', 'baseplane_fit', or 'baseplane_subtracted'
    colormap: str, the colormap to use for the plot
    scale: str, the scale of the plot, must be 'absolute' or 'pixels'

    Returns:
    ax: matplotlib axis object, the axis object of the plot
    '''
    if data_type == 'original':
        img_array = Vk4File['img_height_data']['data']
    elif data_type == 'baseplane':
        img_array = Vk4File['baseplane']
    elif data_type == 'baseplane_fit':
        img_array = Vk4File['baseplane_fit']
    elif data_type == 'baseplane_subtracted':
        img_array = Vk4File['baseplane_subtracted']
    elif data_type == 'feature_enhanced':
        img_array = Vk4File['feature_enhanced']
    else:
        raise ValueError('data_type must be either "original", "baseplane", "baseplane_fit", "baseplane_subtracted" or "feature_enhanced"')
    
    img_width = Vk4File['img_height_data']['width']
    img_height = Vk4File['img_height_data']['height']

    calibration = Vk4File['measurement_conditions']['x_length_per_pixel']
    img_array = img_array.reshape(img_height, img_width)

    return plot_height_data(img_array, img_width, img_height, calibration, colormap, scale)
