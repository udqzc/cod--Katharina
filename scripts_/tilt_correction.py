import numpy as np

from scripts_.plot_vk_data import plot_height_data




def fit_least_squares_plane(z):
    '''
    function for fitting a plane to the height data of a VK4 file using the least squares method
    
    Parameters:
    z: np.array, the height data of the VK4 file, must be a 2D array

    Returns:
    z_plane: np.array, the plane fit to the height data
    '''
    z_flat = z.flatten()
    x = np.arange(z.shape[1])
    y = np.arange(z.shape[0])
    x, y = np.meshgrid(x, y)
    x = x.flatten()
    y = y.flatten()
    # Create a mask to ignore NaN values in z
    mask = ~np.isnan(z_flat)
    # Apply the mask to filter out NaN values
    x_filtered = x[mask]
    y_filtered = y[mask]
    z_filtered = z_flat[mask]
                        
    X = np.vstack([x_filtered, y_filtered, np.ones_like(x_filtered)]).T
    coefficients, _, _, _ = np.linalg.lstsq(X, z_filtered, rcond=None)
    a, b, c = coefficients
    z_plane = a * x + b * y + c
    return z_plane.reshape(z.shape)



def baseplane_filter(Vk4File, percentage):
    height_data = Vk4File['img_height_data']['data']
    baseplane = np.where(height_data < np.nanpercentile(height_data, percentage), np.nan, height_data)
    baseplane = baseplane.reshape(Vk4File['img_height_data']['height'], Vk4File['img_height_data']['width'])
    baseplane_fit = fit_least_squares_plane(baseplane)
    Vk4File['baseplane'] = baseplane
    Vk4File['baseplane_fit'] = baseplane_fit
    Vk4File['baseplane_subtracted'] = (height_data - baseplane_fit.flatten()).reshape(Vk4File['img_height_data']['height'], Vk4File['img_height_data']['width'])
    return Vk4File



def plot_baseplane(Vk4File):
    ax = plot_height_data(Vk4File['baseplane'], Vk4File['img_height_data']['width'], Vk4File['img_height_data']['height'])
    return ax



def plot_baseplane_fit(Vk4File):
    ax = plot_height_data(Vk4File['baseplane_fit'], Vk4File['img_height_data']['width'], Vk4File['img_height_data']['height'])
    return ax