import glob
import numpy as np
import re

from pathlib import Path

from scripts_.plot_vk_data import plot_height_data



def plot_stitched_height_image_from_csv(file_name, mode, overlap_x_um, overlap_y_um):
    '''
    function for plotting the stitched image consisting of CSV file tiles

    Parameters:
    file_name: str, glob pattern for CSV files
               file names must have ending: '_Y*_X*.csv'

    mode: str, tiles include either original or tilt corrected data,
          must be either 'orig' or 'tilt_corr'

    overlap_x_um: float, overlap between tiles in x direction in µm

    overlap_y_um: float, overlap between tiles in y direction in µm

    Returns:
    ax: matplotlib axis object
    
    '''

    assert mode in ['orig', 'tilt_corr'], 'mode must be either "orig" or "tilt_corr"'

    files = glob.glob(str(file_name))
    files = [Path(f) for f in files]

    tiles = {}

    # calibration assumed identical for all files
    with open(files[0], 'r') as file:
        lines = file.readlines()
    #calibration = float(lines[4].split(',')[1])
    calibration = float(lines[4].split(':')[1])

    for f in files:

        m = re.search(r"_Y(\d+)_X(\d+)", f.name)

        if m: 
            y, x = int(m.group(1)), int(m.group(2))

            with open(f, 'r') as file:
                lines = file.readlines()

            overlap_x_px = int(round(overlap_x_um / (calibration/1e6)))
            overlap_y_px = int(round(overlap_y_um / (calibration/1e6)))

            data = np.loadtxt(f, delimiter=';', skiprows=6)

            h, w = data.shape
            tile = data[:h - overlap_y_px, :w - overlap_x_px]

            if mode == 'orig':
                pass

            else:
                pass

            tiles[(y, x)] = tile

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

    ax = plot_height_data(
        big,
        width_px,
        height_px,
        calibration=calibration,
        colormap='viridis',
        scale='absolute'
    )

    return ax