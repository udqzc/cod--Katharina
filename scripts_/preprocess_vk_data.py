import copy
import numpy as np
import struct



def extract_color_data(offset_dict, color_type, in_file):
    '''
    function to extract the offsets for the data sections of a VK4 file
        this code is from Github repo of torkian
        for details, check out the Github website https://github.com/torkian/vk4-python-driver
    
    Parameters:
    offset_dict: dict, a dictionary containing the offsets for the data sections of the VK4 file
    color_type: str, the type of color data, must be 'peak' or 'light'
    in_file: file object, the VK4 file object

    Returns:
    rgb_color_data: dict, a dictionary containing the color data of the VK4 file
    '''

    rgb_types = {'peak': 'color_peak', 'light': 'color_light'}
    rgb_color_data = dict()
    rgb_color_data['name'] = 'RGB ' + color_type
    in_file.seek(offset_dict[rgb_types[color_type]])

    rgb_color_data['width'] = struct.unpack('<I', in_file.read(4))[0]
    rgb_color_data['height'] = struct.unpack('<I', in_file.read(4))[0]
    rgb_color_data['bit_depth'] = struct.unpack('<I', in_file.read(4))[0]
    rgb_color_data['compression'] = struct.unpack('<I', in_file.read(4))[0]
    rgb_color_data['data_byte_size'] = struct.unpack('<I', in_file.read(4))[0]

    rgb_color_arr = np.zeros(((rgb_color_data['width'] * rgb_color_data['height']),
                              (rgb_color_data['bit_depth'] // 8)), dtype=np.uint8)

    i = 0
    for val in range(rgb_color_data['width'] * rgb_color_data['height']):
        rgb = []
        for channel in range(3):
            rgb.append(ord(in_file.read(1)))
        rgb_color_arr[i] = rgb
        i = i + 1

    rgb_color_data['data'] = rgb_color_arr

    return rgb_color_data




def extract_img_data(offset_dict, d_type, in_file):
    '''
    function to extract the offsets for the data sections of a VK4 file
        this code is from Github repo of torkian
        for details, check out the Github website https://github.com/torkian/vk4-python-driver
    
    Parameters:
    offset_dict: dict, a dictionary containing the offsets for the data sections of the VK4 file
    d_type: str, the type of image data, must be 'height' or 'light'
    in_file: file object, the VK4 file object

    Returns:
    data: dict, a dictionary containing the image data of the VK4 file
    '''

    data_types = {'height': ('height', np.uint32, '<I', 4),
                  'light': ('light', np.uint16, '<H', 2)}
    data = dict()
    data['name'] = d_type.capitalize()
    in_file.seek(offset_dict[data_types[d_type][0]])
    data['width'] = struct.unpack('<I', in_file.read(4))[0]
    data['height'] = struct.unpack('<I', in_file.read(4))[0]
    data['bit_depth'] = struct.unpack('<I', in_file.read(4))[0]
    data['compression'] = struct.unpack('<I', in_file.read(4))[0]
    data['data_byte_size'] = struct.unpack('<I', in_file.read(4))[0]
    data['palette_range_min'] = struct.unpack('<I', in_file.read(4))[0]
    data['palette_range_max'] = struct.unpack('<I', in_file.read(4))[0]
    # The palette section of the hexdump is 768 bytes long has 256 3-byte
    # repeats, for now I will store them as a 1d array of uint8 values
    palette = np.zeros(768, dtype=np.uint8)

    i = 0
    for val in range(768):
        palette[i] = ord(in_file.read(1))
        i = i+1
    data['palette'] = palette

    array = np.zeros((data['width']*data['height']), dtype=data_types[d_type][1])
    int_type = data_types[d_type][2]
    bytesize = data_types[d_type][3]
    i = 0
    for val in range(data['width']*data['height']):
        # array[i] = data_types[d_type][2](in_file)
        array[i] = struct.unpack(int_type, in_file.read(bytesize))[0]
        i = i + 1
    data['data'] = array

    return data




def extract_measurement_conditions(offset_dict, in_file):
    '''
    function to extract the offsets for the data sections of a VK4 file
        this code is from Github repo of torkian
        for details, check out the Github website https://github.com/torkian/vk4-python-driver

    Parameters:
    offset_dict: dict, a dictionary containing the offsets for the data sections of the VK4 file
    in_file: file object, the VK4 file object

    Returns:
    measurement_conditions: dict, a dictionary containing the measurement conditions of the VK4 file
    '''

    measurement_conditions = dict()
    measurement_conditions['name'] = 'measurement_conditions'
    in_file.seek(offset_dict['meas_conds'])
    measurement_conditions['size'] = struct.unpack('<I', in_file.read(4))[0]
    # file date
    measurement_conditions['year'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['month'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['day'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['hour'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['minute'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['second'] = struct.unpack('<I', in_file.read(4))[0]

    measurement_conditions['diff_from_UTC'] = struct.unpack('<i', in_file.read(4))[0]
    measurement_conditions['img_attributes'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['user_interface_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['color_composite_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['img_layer_number'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['run_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['peak_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['sharpening_level'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['speed'] = struct.unpack('<I', in_file.read(4))[0]
    # distance and pitch are considered in nanometers
    measurement_conditions['distance'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['pitch'] = struct.unpack('<I', in_file.read(4))[0]
    # optical zoom interpreted as float => optical_zoom/10.0
    measurement_conditions['optical_zoom'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['number_of_lines'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['line0_position'] = struct.unpack('<I', in_file.read(4))[0]
    # next 12 bytes 'reserved'
    measurement_conditions['reserved_1'] = []
    for x in range(3):
        measurement_conditions['reserved_1'].append(struct.unpack('<I', in_file.read(4))[0])

    measurement_conditions['lens_magnification'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['PMT_gain_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['PMT_gain'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['PMT_offset'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['ND_filter'] = struct.unpack('<I', in_file.read(4))[0]
    # next 4 bytes 'reserved'
    measurement_conditions['reserved_2'] = struct.unpack('<I', in_file.read(4))[0]
    # image average frequency
    measurement_conditions['persist_count'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['shutter_speed_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['shutter_speed'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['white_balance_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['white_balance_red'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['white_balance_blue'] = struct.unpack('<I', in_file.read(4))[0]
    # multiply camera_gain by 6 to get camera gain in dB
    measurement_conditions['camera_gain'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['plane_compensation'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['xy_length_unit'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['z_length_unit'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['xy_decimal_place'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['z_decimal_place'] = struct.unpack('<I', in_file.read(4))[0]
    # the following three values are considered in picometers
    measurement_conditions['x_length_per_pixel'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['y_length_per_pixel'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['z_length_per_digit'] = struct.unpack('<I', in_file.read(4))[0]
    # next 20 bytes reserved
    measurement_conditions['reserved_3'] = []
    for x in range(5):
        measurement_conditions['reserved_3'].append(struct.unpack('<I', in_file.read(4))[0])

    measurement_conditions['light_filter_type'] = struct.unpack('<I', in_file.read(4))[0]
    # next 4 bytes reserved
    measurement_conditions['reserved_4'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['gamma_reverse'] = struct.unpack('<I', in_file.read(4))[0]
    # gamma interpreted as float => gamma/100.0
    measurement_conditions['gamma'] = struct.unpack('<I', in_file.read(4))[0]
    # gamma offset interpreted as float => gamma_correction_offset/65536.0
    measurement_conditions['gamma_correction_offset'] = struct.unpack('<I', in_file.read(4))[0]
    # CCD BW offset interpreted as float => CCD_BW_offset/100.0
    measurement_conditions['CCD_BW_offset'] = struct.unpack('<I', in_file.read(4))[0]
    # numerical aperture interpreted as float => num_aperture/1000.0
    measurement_conditions['num_aperture'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['head_type'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['PMT_gain_2'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['omit_color_img'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['lens_ID'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_mode'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_in0'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_out0'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_in1'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_out1'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_in2'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_out2'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_in3'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_out3'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_in4'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_lut_out4'] = struct.unpack('<I', in_file.read(4))[0]
    # upper and lower position considered in nanometers
    measurement_conditions['upper_position'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['lower_position'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['light_effective_bit_depth'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['height_effective_bit_depth'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['x position'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['y position'] = struct.unpack('<I', in_file.read(4))[0]
    measurement_conditions['stage type'] = struct.unpack('<I', in_file.read(4))[0]

    return measurement_conditions




def extract_offsets(in_file):
    '''
    function to extract the offsets for the data sections of a VK4 file
        this code is from Github repo of torkian
        for details, check out the Github website https://github.com/torkian/vk4-python-driver

    Parameters:
    in_file: file object, the VK4 file object

    Returns:
    offsets: dict, a dictionary containing the offsets for the data sections of the VK4 file
    '''

    offsets = dict()
    in_file.seek(12)
    offsets['meas_conds'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['color_peak'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['color_light'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['light'] = struct.unpack('<I', in_file.read(4))[0]
    in_file.seek(8, 1)
    offsets['height'] = struct.unpack('<I', in_file.read(4))[0]
    in_file.seek(8, 1)
    offsets['clr_peak_thumb'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['clr_thumb'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['light_thumb'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['height_thumb'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['assembly_info'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['line_measure'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['line_thickness'] = struct.unpack('<I', in_file.read(4))[0]
    offsets['string_data'] = struct.unpack('<I', in_file.read(4))[0]
    # not sure if reserved is necessary
    offsets['reserved'] = struct.unpack('<I', in_file.read(4))[0]

    return offsets



def crop_map(data, x0, x1, y0, y1):
    '''
    function for cropping a 2D map

    Parameters:
    data: np.array, the 2D map to crop
    x0: int, the starting x coordinate of the crop
    x1: int, the ending x coordinate of the crop 
    y0: int, the starting y coordinate of the crop
    y1: int, the ending y coordinate of the crop

    Returns:
    data[y0:y1, x0:x1]: np.array, the cropped 2D map
    '''
    return data[y0:y1, x0:x1]




def crop_Vk4File_map(Vk4File, x0=None, x1=None, y0=None, y1=None):
    '''
    function for cropping a VK4 file
        this includes cropping all maps in the VK4 file and updating the width and height of the data
        currently, they are height data, light image data, base plane, base plane fit, base plane subtracted and feature enhanced data
    
    Parameters:
    Vk4File: dict, a dictionary containing the data of a VK4 file
    x0: int, the starting x coordinate of the crop in um
    x1: int, the ending x coordinate of the crop in um
    y0: int, the starting y coordinate of the crop in um
    y1: int, the ending y coordinate of the crop in um

    Returns:
    Vk4File_copy: dict, a dictionary containing the cropped data of the VK4 file
    '''
    if x0 is None:
        x0 = 0
    if x1 is None:
        x1 = Vk4File['img_height_data']['width']
    if y0 is None:
        y0 = 0
    if y1 is None:
        y1 = Vk4File['img_height_data']['height']

    Vk4File_copy = copy.deepcopy(Vk4File)
    # crop both the height and light data so they stay aligned
    Vk4File_copy['img_height_data']['data'] = crop_map(Vk4File_copy['img_height_data']['data'].reshape(Vk4File_copy['img_height_data']['height'], Vk4File_copy['img_height_data']['width']), x0, x1, y0, y1).flatten()
    Vk4File_copy['img_light_data']['data'] = crop_map(Vk4File_copy['img_light_data']['data'].reshape(Vk4File_copy['img_light_data']['height'], Vk4File_copy['img_light_data']['width']), x0, x1, y0, y1).flatten()
    # crop the base plane, base plane fit, and base plane subtracted data if they exist
    if 'baseplane' in Vk4File_copy:
        Vk4File_copy['baseplane'] = crop_map(Vk4File_copy['baseplane'], x0, x1, y0, y1)
    if 'baseplane_fit' in Vk4File_copy:
        Vk4File_copy['baseplane_fit'] = crop_map(Vk4File_copy['baseplane_fit'], x0, x1, y0, y1)
    if 'baseplane_subtracted' in Vk4File_copy:
        Vk4File_copy['baseplane_subtracted'] = crop_map(Vk4File_copy['baseplane_subtracted'], x0, x1, y0, y1)
    if 'feature_enhanced' in Vk4File_copy:
        Vk4File_copy['feature_enhanced'] = crop_map(Vk4File_copy['feature_enhanced'], x0, x1, y0, y1)
    # update the width and height of the data
    Vk4File_copy['img_height_data']['width'] = x1 - x0
    Vk4File_copy['img_height_data']['height'] = y1 - y0
    Vk4File_copy['img_light_data']['width'] = x1 - x0
    Vk4File_copy['img_light_data']['height'] = y1 - y0
    return Vk4File_copy