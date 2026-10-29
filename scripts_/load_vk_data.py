import io
import struct
import zipfile


from scripts_.preprocess_vk_data import extract_color_data
from scripts_.preprocess_vk_data import extract_img_data
from scripts_.preprocess_vk_data import extract_measurement_conditions
from scripts_.preprocess_vk_data import extract_offsets



def parse_vk6_file(filename):
    '''
    function to parse a VK6 file and return the data in a dictionary
        this function is converted from the Gwyddion software c source code
        for details, check out the Gwyddion official website: https://gwyddion.net/

    Parameters:
    filename: str, the path to the VK6 file

    Returns:
    result: dict, a dictionary containing:
            a Vk4 file object
            a Vk4 measurement condition object
            a VK6 measurement condition object
            a Vk6 image data object
    '''
    
    MAGIC6 = b'VK6'
    MAGICBMP = b'BM'
    KEYENCE6_HEADER_SIZE = 7
    BMP_HEADER_SIZE = 14 + 40  # NT/3.1 BMP header size

    with open(filename, 'rb') as f:
        buffer = f.read()
    # Check if the file starts with the VK6 magic number
    if not buffer.startswith(MAGIC6):
        raise ValueError("Not a valid VK6 file")

    # Check if the BMP header is present
    bmp_header_offset = KEYENCE6_HEADER_SIZE
    if not buffer[bmp_header_offset:bmp_header_offset + len(MAGICBMP)] == MAGICBMP:
        raise ValueError("BMP header not found in VK6 file")

    # Extract the BMP size from the VK6 miniheader
    vk6_skip = struct.unpack('<I', buffer[len(MAGIC6):len(MAGIC6) + 4])[0]

    # Extract the BMP size from the BMP header
    bmp_size = struct.unpack('<I', buffer[bmp_header_offset + 2:bmp_header_offset + 6])[0]
    # print(f"BMP image file size: {bmp_size}")

    # Verify that the VK6 miniheader agrees with the BMP header
    if vk6_skip != bmp_size:
        raise ValueError("VK6 miniheader and BMP header size mismatch")

    # The remaining data after the BMP should be a ZIP archive
    zip_data_offset = KEYENCE6_HEADER_SIZE + bmp_size
    zip_data = buffer[zip_data_offset:]

    # Open the ZIP archive
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
        # there should be four files in the ZIP archive
        # print(zip_file.namelist())
        Vk4File = zip_file.open('Vk4File')
        Vk4MeasureCondition = zip_file.open('Vk4MeasureCondition')
        VK6MeasureCondition = zip_file.open('VK6MeasureCondition')
        Vk6ImageData = zip_file.open('Vk6ImageData')
    
    result = {'Vk4File': Vk4File, 
              'Vk4MeasureCondition': Vk4MeasureCondition, 
              'VK6MeasureCondition': VK6MeasureCondition, 
              'Vk6ImageData': Vk6ImageData}

    return result




def parse_vk4_file(Vk4File):
    '''
    a wrapper function for parsing a VK4 file and returning the data in a dictionary
        a specific step in this function is to calibrate the units of the x, y, and z axes
        the calibration is done by multiplying the pixel values by the x_length_per_pixel, y_length_per_pixel, and z_length_per_digit values
        which are recorded in the metadata of the VK4 file

    Parameters:
    Vk4File: file object, the VK4 file object

    Returns:
    result: dict, a dictionary containing:
            a dictionary of measurement conditions
            a dictionary of color peak data
            a dictionary of color light data
            a dictionary of height image data
            a dictionary of light image data    
    '''

    offset_dict = extract_offsets(Vk4File)

    color_peak_data = extract_color_data(offset_dict, 'peak', Vk4File)
    color_light_data = extract_color_data(offset_dict, 'light', Vk4File)
    img_height_data = extract_img_data(offset_dict, 'height', Vk4File)
    img_light_data = extract_img_data(offset_dict, 'light', Vk4File)
    measurement_conditions = extract_measurement_conditions(offset_dict, Vk4File)

    # append true width and height in µm to dictionary
    measurement_conditions['true_width'] = img_height_data['width']/1e6*measurement_conditions['x_length_per_pixel']
    measurement_conditions['true_height'] = img_height_data['height']/1e6*measurement_conditions['y_length_per_pixel']
    # convert height data to be in µm
    img_height_data['data'] = img_height_data['data']/1e6*measurement_conditions['z_length_per_digit']

    result = {'measurement_conditions': measurement_conditions,
              'color_peak_data': color_peak_data,
              'color_light_data': color_light_data,
              'img_height_data': img_height_data,
              'img_light_data': img_light_data}

    return result



def parse_vk4_file_stitched_tile(Vk4File):
    '''
    a wrapper function for parsing a VK4 file of a tile from a stitched image and returning the data in a dictionary
        a specific step in this function is to calibrate the units of the x, y, and z axes
        the calibration is done by multiplying the pixel values by the x_length_per_pixel, y_length_per_pixel, and z_length_per_digit values
        which are recorded in the metadata of the VK4 file

    Parameters:
    Vk4File: file object, the VK4 file object

    Returns:
    result: dict, a dictionary containing:
            a dictionary of measurement conditions
            a dictionary of color peak data
            a dictionary of color light data
            a dictionary of height image data
            a dictionary of light image data    
    '''
    
    offset_dict = extract_offsets(Vk4File)

    color_peak_data = extract_color_data(offset_dict, 'peak', Vk4File)
    #color_light_data = extract_color_data(offset_dict, 'light', Vk4File)
    img_height_data = extract_img_data(offset_dict, 'height', Vk4File)
    #img_light_data = extract_img_data(offset_dict, 'light', Vk4File)
    measurement_conditions = extract_measurement_conditions(offset_dict, Vk4File)

    # append true width and height in µm to dictionary
    measurement_conditions['true_width'] = img_height_data['width']/1e6*measurement_conditions['x_length_per_pixel']
    measurement_conditions['true_height'] = img_height_data['height']/1e6*measurement_conditions['y_length_per_pixel']
    # convert height data to be in µm
    img_height_data['data'] = img_height_data['data']/1e6*measurement_conditions['z_length_per_digit']

    result = {'measurement_conditions': measurement_conditions,
              'color_peak_data': color_peak_data,
              #'color_light_data': color_light_data,
              'img_height_data': img_height_data,}
              #'img_light_data': img_light_data}

    return result