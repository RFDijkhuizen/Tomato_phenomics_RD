from plantcv import plantcv as pcv
import sys
import os
import glob
import numpy as np
from PIL import Image
import random
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


# Starting parameters Parameters
hue_lower_tresh = 24                #24
hue_higher_tresh = 50               #50
saturation_lower_tresh = 140        #140
saturation_higher_tresh = 230       #230
value_lower_tresh = 125             #125
value_higher_tresh = 255            #255
green_lower_tresh = 110             #110
green_higher_tresh = 255            #255
red_lower_tresh = 24                #24
red_higher_thresh = 98              #98
blue_lower_tresh = 85               #85
blue_higher_tresh = 255             #255

blur_k = 3
fill_k = 3
debug_setting = "None"
loops = 1 # Amount of loops you try to find better parameters
pixel_match_reward = 1     # The similarity score for when the True positive and test agree on whether a pixel is plant
pixel_mismatch_penalty = -1 # The similiarity score for when the True positve and test disagree
# Starting parameters in array
starting_parameters = [hue_lower_tresh, hue_higher_tresh, saturation_lower_tresh, saturation_higher_tresh, value_lower_tresh, value_higher_tresh, green_lower_tresh,
              green_higher_tresh, red_lower_tresh, red_higher_thresh, blue_lower_tresh, blue_higher_tresh, blur_k, fill_k]
use_mask = True # dependent on this parameter test() will return a mask or masked image.
roi_type = "largest" # Should be largest but turn to partial to ignore warnings.
mu, sigma = 0, 5                   # Normal distribution of steps taken to permute parameters




class HiddenPrints:                                # To surpress unnecessary warning messages
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

### test workflow
def test(true_positive_file, test_parameters):
    hue_lower_tresh = test_parameters[0]
    hue_higher_tresh = test_parameters[1]
    saturation_lower_tresh = test_parameters[2]
    saturation_higher_tresh = test_parameters[3]
    value_lower_tresh = test_parameters[4]
    value_higher_tresh = test_parameters[5]
    green_lower_tresh = test_parameters[6]
    green_higher_tresh = test_parameters[7]
    red_lower_tresh = test_parameters[8]
    red_higher_thresh = test_parameters[9]
    blue_lower_tresh = test_parameters[10]
    blue_higher_tresh = test_parameters[11]
    blur_k = test_parameters[12]
    fill_k = test_parameters[13]
    
    class args:
            #image = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\0214_2018-03-07 08.55 - 26_cam9.png"
            image = true_positive_file
            outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\output"
            debug = debug_setting
            result = "results.txt"
    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    # Read image (readimage mode defaults to native but if image is RGBA then specify mode='rgb')
    # Inputs:
    #   filename - Image file to be read in 
    #   mode - Return mode of image; either 'native' (default), 'rgb', 'gray', or 'csv'
    img, path, filename = pcv.readimage(filename=args.image, mode='rgb')
    
    s = pcv.rgb2gray_hsv(rgb_img=img, channel='h')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[hue_lower_tresh], upper_thresh=[hue_higher_tresh], channel='gray')
    masked = pcv.apply_mask(rgb_img=img, mask = mask, mask_color = 'white')
    #print("filtered on hue")
    s = pcv.rgb2gray_hsv(rgb_img=masked, channel='s')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[saturation_lower_tresh], upper_thresh=[saturation_higher_tresh], channel='gray')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    #print("filtered on saturation")
    s = pcv.rgb2gray_hsv(rgb_img=masked, channel='v')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[value_lower_tresh], upper_thresh=[value_higher_tresh], channel='gray')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    #print("filtered on value")
    mask, masked = pcv.threshold.custom_range(rgb_img=masked, lower_thresh=[0,green_lower_tresh,0], upper_thresh=[255,green_higher_tresh,255], channel='RGB')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    #print("filtered on green")
    mask, masked = pcv.threshold.custom_range(rgb_img=masked, lower_thresh=[red_lower_tresh,0,0], upper_thresh=[red_higher_thresh,255,255], channel='RGB')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    #print("filtered on red")
    mask_old, masked_old = pcv.threshold.custom_range(rgb_img=masked, lower_thresh=[0,0,blue_lower_tresh], upper_thresh=[255,255,blue_higher_tresh], channel='RGB')
    masked = pcv.apply_mask(rgb_img=masked_old, mask = mask_old, mask_color = 'white')
    #print("filtered on blue")
    ###____________________________________ Blur to minimize 
    try:
        s_mblur = pcv.median_blur(gray_img = masked_old, ksize = blur_k)
        s = pcv.rgb2gray_hsv(rgb_img=s_mblur, channel='v')
        mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[0], upper_thresh=[254], channel='gray')
    except:
        print("failed blur step")
    try:
        mask = pcv.fill(mask, fill_k)
    except:
        pass
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')


    ###_____________________________________ Now to identify objects
    masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
    masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')
    
     # Threshold the green-magenta and blue images
    maskeda_thresh = pcv.threshold.binary(gray_img=masked_a, threshold=115, 
                                      max_value=255, object_type='dark')
    maskeda_thresh1 = pcv.threshold.binary(gray_img=masked_a, threshold=135, 
                                           max_value=255, object_type='light')
    maskedb_thresh = pcv.threshold.binary(gray_img=masked_b, threshold=128, 
                                          max_value=255, object_type='light')
    
    ab1 = pcv.logical_or(bin_img1=maskeda_thresh, bin_img2=maskedb_thresh)
    ab = pcv.logical_or(bin_img1=maskeda_thresh1, bin_img2=ab1)
    
    # Fill small objects
    # Inputs: 
    #   bin_img - Binary image data 
    #   size - Minimum object area size in pixels (must be an integer), and smaller objects will be filled
    ab_fill = pcv.fill(bin_img=ab, size=200)
    #print("filled")
    # Apply mask (for VIS images, mask_color=white)
    masked2 = pcv.apply_mask(rgb_img=masked, mask=ab_fill, mask_color='white')
    
    id_objects, obj_hierarchy = pcv.find_objects(masked, ab_fill)
    # Let's just take the largest
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked, x=0, y=0, h=960, w=1280)  # Currently hardcoded
    with HiddenPrints():
        roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                                       roi_hierarchy=roi_hierarchy, 
                                                                       object_contour=id_objects, 
                                                                       obj_hierarchy=obj_hierarchy,
                                                                       roi_type=roi_type)
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)
    
    if use_mask == True:
        return(mask)
    else:
        masked2 = pcv.apply_mask(rgb_img=masked, mask=mask, mask_color='white')
        return(masked2)

def read_true_positive(true_positive_file):
    class args:
        #image = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\0214_2018-03-07 08.55 - 26_true_positive.png"
        image = true_positive_file
        outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\output"
        debug = "None"
        result = "results.txt"
        
    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory
    
    # Read image (readimage mode defaults to native but if image is RGBA then specify mode='rgb')
    # Inputs:
    #   filename - Image file to be read in 
    #   mode - Return mode of image; either 'native' (default), 'rgb', 'gray', or 'csv'
    img, path, filename = pcv.readimage(filename=args.image, mode='rgb')
    
    s = pcv.rgb2gray_hsv(rgb_img=img, channel='s')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[10], upper_thresh=[255], channel='gray')
    masked = pcv.apply_mask(rgb_img=img, mask = mask, mask_color = 'white')
    #new_im = Image.fromarray(mask)
    #name = "positive_test.png"
    #Recognizing objects
    id_objects, obj_hierarchy = pcv.find_objects(masked, mask)
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked, x=0, y=0, h=960, w=1280)  # Currently hardcoded
    with HiddenPrints():
        roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                                       roi_hierarchy=roi_hierarchy, 
                                                                       object_contour=id_objects, 
                                                                       obj_hierarchy=obj_hierarchy,
                                                                   roi_type=roi_type)
    
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)
    #new_im.save(name)
    return(mask)
    
def compare(true_result, test_file, parameters):
    # Run the test with the parameters
    comp_result = test(test_file, parameters)

    # Check similarity
    similarity = 0
    pixel_y_counter = 0 
    pixel_x_counter = 0      
    for pixel_y in comp_result:
        pixel_x_counter = 0
        for pixel_x in pixel_y:
            if np.array_equal(comp_result[pixel_y_counter][pixel_x_counter], true_result[pixel_y_counter][pixel_x_counter]):
                similarity += 1
            else:
                similarity += -1
            pixel_x_counter += 1
        pixel_y_counter += 1
    return (similarity / (pixel_y_counter * pixel_x_counter))
    

def permute_parameters(input_parameters):
    i = 0
    new_values = [0,0,0,0,0,0,0,0,0,0,0,0,0,00]
    for item in input_parameters:
        new_values[i] = item
        i += 1
    random_para_nummer = random.randint(0,13)
    step = (np.random.normal(mu, sigma, 1))
    if random_para_nummer <= 11:
        new_random_value = round(new_values[random_para_nummer] + (step), 2)
        if new_random_value <= 0:
            new_random_value = 0
        elif new_random_value >= 255:
            new_random_value = 255
    else:                                   # Blur fill en k have alternative restraints because of computational reasons.
        new_random_value = round(new_values[random_para_nummer] + (step), 0)
        if new_random_value <= 2:
            new_random_value = 2
        elif new_random_value >= 10:
            new_random_value = 10
            
    new_values[random_para_nummer] = new_random_value
    return(new_values)
    
def main(true_positive_file, test_file, starting_values, rounds):
    values = starting_values
    true_result = read_true_positive(true_positive_file)
    old_similarity = compare(true_result, test_file, starting_values)
    print("The starting similiary is")
    print(old_similarity)
    for n in range(rounds):
        #### Here we permute the parameters
        new_values = permute_parameters(values)
        similarity = compare(true_result, test_file, new_values)
        if similarity > old_similarity:
            old_similarity = similarity
            values = new_values
            print("better parameters found")
            print(similarity)
        else:
            print("nothing better found")
        print("current loop is %d"% (n))
    return(values)
 
    
### The magic is here
counter_hue_lower_tresh = 0
counter_hue_higher_tresh = 0
counter_saturation_lower_tresh = 0
counter_saturation_higher_tresh = 0
counter_value_lower_tresh = 0
counter_value_higher_tresh = 0
counter_green_lower_tresh = 0
counter_green_higher_tresh = 0
counter_red_lower_tresh = 0
counter_red_higher_thresh = 0
counter_blue_lower_tresh = 0
counter_blue_higher_tresh = 0
counter_blur_k = 0
counter_fill_k = 0
counter_sets = 0
true_positives = glob.glob('*positive.png')
true_positive_files = []
all_learned_parameters = []
for item in true_positives:
    item = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\" + item
    true_positive_files.append(item)
test_files = []
for item in true_positive_files:
    item = item[0:-17] + "cam9.png"
    test_files.append(item)
print(test_files)
i = 0
for item in true_positive_files:
    true_file = item
    test_file = test_files[i]
    print("current file is %d" %(i))
    use_mask = True
    learned_parameters = main(true_file, test_file, starting_parameters, loops)
    all_learned_parameters.append(learned_parameters)
    print (learned_parameters)
    debug_setting = "None"
    use_mask = False
    final_result = test(test_file, learned_parameters)
    new_im = Image.fromarray(final_result)
    result_filename = "learned_result" + true_positives[i][0:-18] + ".png"
    i += 1
    new_im.save(result_filename)
#Now to calculate the final average values
for item in all_learned_parameters:
    counter_hue_lower_tresh += item[0]
    counter_hue_higher_tresh += item[1]
    counter_saturation_lower_tresh += item[2]
    counter_saturation_higher_tresh += item[3]
    counter_value_lower_tresh += item[4]
    counter_value_higher_tresh += item[5]
    counter_green_lower_tresh += item[6]
    counter_green_higher_tresh += item[7]
    counter_red_lower_tresh += item[8]
    counter_red_higher_thresh += item[9]
    counter_blue_lower_tresh += item[10]
    counter_blue_higher_tresh += item[11]
    counter_blur_k += item[12]
    counter_fill_k += item[13]
    counter_sets += 1
final_parameters = [counter_hue_lower_tresh / counter_sets, counter_hue_higher_tresh / counter_sets,
                    counter_saturation_lower_tresh / counter_sets,counter_saturation_higher_tresh / counter_sets,
                    counter_value_lower_tresh / counter_sets, counter_value_higher_tresh / counter_sets,
                    counter_green_lower_tresh / counter_sets, counter_green_higher_tresh / counter_sets,
                    counter_red_lower_tresh / counter_sets, counter_red_higher_thresh / counter_sets,
                    counter_blue_lower_tresh / counter_sets, counter_blue_higher_tresh / counter_sets,
                    counter_blur_k / counter_sets, counter_fill_k / counter_sets]
print(final_parameters)
x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14] * counter_sets
x = ["hue_l", "hue_h", "sat_l", "sat_h", "val_l", "val_h", "green_l", "green_h", "red_l", "red_h", "blue_l", "blue_h", "blur_k", "fill_k"] * counter_sets
y = []
for item in all_learned_parameters:
    for subitem in item:
        y.append(subitem)


plt.scatter(x, y, s=10)
plt.rcParams["figure.figsize"] = (10,5)
plt.xlabel("all parameters")
plt.ylabel("value")
plt.savefig("learned_para.png")
plt.show()

# Write all found parameters out in a file.
output = open("found_parameters.txt", "w")
output.write("hue_low, hue_high, sat_low, sat_high, val_low, val_high, green_low, green_high, red_low, red_high, blue_low, blue_high, blur_k, fill_k \n")
for item in all_learned_parameters:
    line = ""
    for subitem in item:
        line = line + str(subitem) + ", "
    line = line + "\n"
    output.write(line)
output.close()