import numpy as np

from pathlib import Path

from scripts_.load_vk_data import parse_vk6_file
from scripts_.load_vk_data import parse_vk4_file_stitched_tile
from scripts_.tilt_correction import baseplane_filter
#from scripts_.feature_enhancement import feature_enhancement
from scripts_.feature_enhancement import feature_enhancement_single_gaussian_clip




def vk_height_to_csv(file_name, data_type='original', output_dir=None):
    '''
    Convert the height data in a single VK4/VK6 file to CSV.

    Parameters:
    file_name : str or path, input VK4 or VK6 file
    data_type: str, the type of height data to convert to CSV, must be 'original', 'baseplane_subtracted' or 'feature_enhanced'
    output_dir : str or path or None, folder to save CSV; if None, same folder as input file
    
    '''

    file_name = Path(file_name)
    suffix = file_name.suffix.lower()

    if suffix not in [".vk4", ".vk6"]:
        raise ValueError("Only .vk4 or .vk6 files are supported")


    if suffix == ".vk6":
        data_vk6 = parse_vk6_file(str(file_name))
        data_vk4 = parse_vk4_file_stitched_tile(data_vk6["Vk4File"])
    else:
        with open(file_name, "rb") as f:
            data_vk4 = parse_vk4_file_stitched_tile(f)


    if data_type == 'original':
        img_data = data_vk4['img_height_data']['data']
    elif data_type == 'baseplane_subtracted':
        img_data = baseplane_filter(data_vk4, 60)['baseplane_subtracted']
        
    #elif data_type == 'feature_enhanced':
    #    img_data = feature_enhancement(data_vk4)['feature_enhanced']
    elif data_type == 'feature_enhanced':
        data_vk4 = baseplane_filter(data_vk4, 60)
        data_vk4 = feature_enhancement_single_gaussian_clip(data_vk4)
        img_data = data_vk4['feature_enhanced']

    else:
        raise ValueError('data_type must be either "original", "baseplane_subtracted" or "feature_enhanced"')


    width = data_vk4["img_height_data"]["width"]
    height = data_vk4["img_height_data"]["height"]


    if img_data.ndim == 1:
        img_data = img_data.reshape((height, width), order="C")

    calib_xy = data_vk4["measurement_conditions"]["x_length_per_pixel"]
    calib_z = data_vk4["measurement_conditions"]["z_length_per_digit"]


    if output_dir is None:
        name = file_name.parent.name
        output_dir = Path("../processed_data_csv") / name
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)


    if data_type == 'original':
        output_file = output_dir / f"{file_name.stem}_csv.csv"
    elif data_type == 'baseplane_subtracted':
        output_file = output_dir / f"{file_name.stem}_tiltcorr_csv.csv"
    elif data_type == 'feature_enhanced':
        output_file = output_dir / f"{file_name.stem}_enhanced_csv.csv"


    with open(output_file, "w") as f:
        f.write("Height Data Export\n")
        f.write(f"File: {file_name.name}\n")
        f.write(f"Image width: {width}\n")
        f.write(f"Image height: {height}\n")
        f.write(f"XY calibration (nm/pixel): {calib_xy}\n")
        f.write(f"Z calibration (nm/digit): {calib_z}\n\n")

        np.savetxt(f, img_data, delimiter=";")

    return output_file



#def convert_vk_folder_to_csv(input_folder, output_folder=None):
def convert_vk_folder_to_csv(input_folder, output_folder=None, data_type="original"):
    '''
    Convert the height data of all VK4/VK6 files in a folder to CSV.

    Parameters:
    input_folder: str, path to folder with VK4/VK6 files
    output_folder: str, output folder; if None, folder 'csv_output' inside original folder is created
    
    '''

    input_folder = Path(input_folder)

    if output_folder is None:
        name = input_folder.name
        output_folder = Path("../processed_data_csv") / name
    else:
        output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    vk_files = sorted(list(input_folder.glob("*.vk4")) +
                      list(input_folder.glob("*.vk6")))

    if not vk_files:
        raise ValueError("No VK4/VK6 files found in folder")

    for file in vk_files:
        #out = vk_height_to_csv(file, output_folder)
        out = vk_height_to_csv(file, data_type=data_type, output_dir=output_folder)
        print(f"Saved: {out}")