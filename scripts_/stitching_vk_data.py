import glob
import numpy as np
import re

from pathlib import Path

from scripts_.load_vk_data import parse_vk6_file
from scripts_.load_vk_data import parse_vk4_file_stitched_tile
from scripts_.plot_vk_data import plot_height_data, plot_reflected_light
from scripts_.tilt_correction import baseplane_filter
from scripts_.tilt_correction import fit_least_squares_plane
from scripts_.feature_enhancement import feature_enhancement_proceedings




def plot_stitched_height_image_from_vk(file_name, mode, overlap_x_um, overlap_y_um):
    '''
    function for plotting the stitched image consisting of VK4 or VK6 file tiles
    
    Parameters:
    file_name: str, the path to the VK4/VK6 files, file names must correspond to default name by Keyence: 
               'YearMonthDayHourMinuteSecond_Y*_X*.vk4' or 'YearMonthDayHourMinuteSecond_Y*_X*.vk6'
    mode: str, tiles include either original or tilt corrected data, must be either 'orig' or 'tilt_corr'
    overlap_x_um: float, overlap between tiles in x direction in µm
    overlap_y_um: float, overlap between tiles in y direction in µm
    
    Returns:
    ax: matplotlib axis object, the axis object of the plot
    
    '''
    
    assert mode in ['orig', 'tilt_corr', 'feat_enhanced'], 'mode must be either "orig", "tilt_corr" or "feat_enhanced"'
    
    files = glob.glob(str(file_name))
    files = [Path(f) for f in files]
    
    tiles = {}

    for f in files:

        m = re.search(r"_Y(\d+)_X(\d+)", f.name)
        
        if m:
            
            y, x = int(m.group(1)), int(m.group(2))

            if f.suffix.lower() == '.vk6':
                data_vk6 = parse_vk6_file(f)
                data_vk4 = parse_vk4_file_stitched_tile(data_vk6['Vk4File'])

            elif f.suffix.lower() == '.vk4':
                with open(f, 'rb') as vk4_file:
                    data_vk4 = parse_vk4_file_stitched_tile(vk4_file)

            else:
                raise ValueError('File must be .vk4 or .vk6')
            
            calibration = data_vk4['measurement_conditions']['x_length_per_pixel']
            overlap_x_px = int(round(overlap_x_um / (calibration/1e6)))
            overlap_y_px = int(round(overlap_y_um / (calibration/1e6)))

            #Abschnitt 4
            if mode == 'orig':
                img = data_vk4['img_height_data']
                h = img['height']
                w = img['width']
                data = img['data']

                tile = data.reshape(h,w)
                tile = tile[:h-overlap_y_px, :w-overlap_x_px]
                tiles[(y, x)] = tile
                
            elif mode == 'tilt_corr':
                data_vk4_tilt_corr = baseplane_filter(data_vk4, 20)
                img = data_vk4_tilt_corr['img_height_data']
                h = img['height']
                w = img['width']
                data = img['data']

                tile = data_vk4_tilt_corr['baseplane_subtracted'].reshape(h, w)
                tile = tile[:h-overlap_y_px, :w-overlap_x_px]
                tiles[(y, x)] = tile
            
            else:
                data_vk4_tilt_corr = baseplane_filter(data_vk4, 20)
                #data_vk4_feat_enhanced = feature_enhancement(data_vk4_tilt_corr)
                data_vk4_feat_enhanced = feature_enhancement_proceedings(data_vk4_tilt_corr)
                img = data_vk4_feat_enhanced['img_height_data']
                h = img['height']
                w = img['width']
                data = img['data']

                tile = data_vk4_feat_enhanced['feature_enhanced'].reshape(h, w)
                tile = tile[:h-overlap_y_px, :w-overlap_x_px]
                tiles[(y, x)] = tile
            #Ende Abschnitt 4



    if not tiles:
        raise ValueError(f"No tiles found. Files processed: {[str(f) for f in files]}")
    
    # grid size
    #max_y = max(y for y, _ in tiles)
    #max_x = max(x for _, x in tiles)

    ys = [y for y, _ in tiles]
    xs = [x for _, x in tiles]

    min_y, max_y = min(ys), max(ys)
    min_x, max_x = min(xs), max(xs)
    
    # big image
    #tile_h, tile_w = next(iter(tiles.values())).shape
    #big = np.zeros((max_y * tile_h, max_x * tile_w))

    tile_h, tile_w = next(iter(tiles.values())).shape

    big_h = (max_y - min_y + 1) * tile_h
    big_w = (max_x - min_x + 1) * tile_w

    big = np.full((big_h, big_w), np.nan)
    
    # stitch
    for (y, x), tile in tiles.items():
        #y0 = (y - 1) * tile_h
        #x0 = (x - 1) * tile_w
        y0 = (y - min_y) * tile_h
        x0 = (x - min_x) * tile_w
        big[y0:y0 + tile_h, x0:x0 + tile_w] = tile
    
    # plot    
    height_px, width_px = big.shape
    #print(big.shape)
    
    ax = plot_height_data(
        big,
        width_px,
        height_px,
        calibration=calibration,
        colormap='viridis',
        scale='absolute'
    )
    #plt.savefig('Stitched image')

    return ax




def plot_stitched_height_image_from_vk_2(file_name, mode, overlap_x_um, overlap_y_um):
    '''
    function for plotting the stitched image consisting of VK4 or VK6 file tiles

    Parameters:
    file_name: str, the path to the VK4/VK6 files, file names must correspond to default name by Keyence: 
               'YearMonthDayHourMinuteSecond_Y*_X*.vk4' or 'YearMonthDayHourMinuteSecond_Y*_X*.vk6'
    mode: str, tiles include either original or tilt corrected data, must be either 'orig' or 'tilt_corr'
    overlap_x_um: float, overlap between tiles in x direction in µm
    overlap_y_um: float, overlap between tiles in y direction in µm
    
    Returns:
    ax: matplotlib axis object, the axis object of the plot

    '''
    
    assert mode in ['orig', 'tilt_corr'], 'mode must be either "orig" or "tilt_corr"'

    files = glob.glob(str(file_name))
    files = [Path(f) for f in files]

    tiles = {}

    for f in files:

        m = re.search(r"_Y(\d+)_X(\d+)", f.name)
        
        if m:
            
            y, x = int(m.group(1)), int(m.group(2))

            if f.suffix.lower() == '.vk6':
                data_vk6 = parse_vk6_file(f)
                data_vk4 = parse_vk4_file_stitched_tile(data_vk6['Vk4File'])

            elif f.suffix.lower() == '.vk4':
                with open(f, 'rb') as vk4_file:
                    data_vk4 = parse_vk4_file_stitched_tile(vk4_file)

            else:
                raise ValueError('File must be .vk4 or .vk6')
            
            calibration = data_vk4['measurement_conditions']['x_length_per_pixel']
            overlap_x_px = int(round(overlap_x_um / (calibration/1e6)))
            overlap_y_px = int(round(overlap_y_um / (calibration/1e6)))
            
            
            img = data_vk4['img_height_data']
            h = img['height']
            w = img['width']
            data = img['data']

            tile = data.reshape(h,w)
            tile = tile[:h-overlap_y_px, :w-overlap_x_px]
            tiles[(y, x)] = tile


    if not tiles:
        raise ValueError(f"No tiles found. Files processed: {[str(f) for f in files]}")


    ys = [y for y, _ in tiles]
    xs = [x for _, x in tiles]

    min_y, max_y = min(ys), max(ys)
    min_x, max_x = min(xs), max(xs)
    

    tile_h, tile_w = next(iter(tiles.values())).shape

    big_h = (max_y - min_y + 1) * tile_h
    big_w = (max_x - min_x + 1) * tile_w

    big = np.full((big_h, big_w), np.nan)
    
    # stitch
    for (y, x), tile in tiles.items():
        #y0 = (y - 1) * tile_h
        #x0 = (x - 1) * tile_w
        y0 = (y - min_y) * tile_h
        x0 = (x - min_x) * tile_w
        big[y0:y0 + tile_h, x0:x0 + tile_w] = tile

    
    # tilt correction
    if mode == "tilt_corr":
        baseplane = np.where(big < np.nanpercentile(big, 20), np.nan, big)

        baseplane_fit = fit_least_squares_plane(baseplane)

        big = big - baseplane_fit

    
    # plot    
    height_px, width_px = big.shape
    #print(big.shape)
    
    ax = plot_height_data(
        big,
        width_px,
        height_px,
        calibration=calibration,
        colormap='viridis',
        scale='absolute'
    )
    #plt.savefig('Stitched image')

    return ax
