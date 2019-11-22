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


## Parameters
"HSV color space"
saturation_lower_tresh = 120        #
saturation_higher_tresh = 255       # 
hue_lower_tresh = 18                #
hue_higher_tresh = 55               #
value_lower_tresh = 70              #
value_higher_tresh = 255            #
HSV_blur_k = 3
"CIELAB color space"
l_lower_thresh = 130                # Lower light thresh to be considered plant # original 125
l_higher_thresh = 255               # Higher thresh to be considered plant.
a_lower_thresh_1 = 118              # Lower thresh to be considered plant
a_lower_thresh_2 = 138              # Lower thresh to be considered too magenta to be plant
b_lower_thresh_1 = 165              # Threshold to filter background away
b_higher_thresh_1 = 255             # Threshold to filter background away
b_fill_k = 1000                     # Fill to make sure we do not lose anything
b_lower_thresh_2 = 120              # Threshold to capture plant
b_higher_thresh_2 = 255             # Threshold to capture plant
LAB_fill_k = 1500                   # Fill kernel for the LAB filtered image
LAB_blur_k = 10                     # Final Blur


debug_setting = "None"
loops = 1 # Amount of loops you try to find better parameters
pixel_match_reward = 1     # The similarity score for when the True positive and test agree on whether a pixel is plant
pixel_mismatch_penalty = -1 # The similiarity score for when the True positve and test disagree
# Starting parameters in array
starting_parameters = [saturation_lower_tresh, saturation_higher_tresh, hue_lower_tresh, hue_higher_tresh, value_lower_tresh, value_higher_tresh, l_lower_thresh,
                       a_lower_thresh_1, a_lower_thresh_2, b_lower_thresh_1, b_higher_thresh_1, b_lower_thresh_2, b_higher_thresh_2, HSV_blur_k , LAB_blur_k, b_fill_k, 
                       LAB_fill_k]
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
    saturation_lower_tresh = test_parameters[0]
    saturation_higher_tresh = test_parameters[1]
    hue_lower_tresh = test_parameters[2]
    hue_higher_tresh = test_parameters[3]
    value_lower_tresh = test_parameters[4]
    value_higher_tresh = test_parameters[5]
    l_lower_thresh = test_parameters[6]
    a_lower_thresh_1 = test_parameters[7]
    a_lower_thresh_2 = test_parameters[8]
    b_lower_thresh_1 = test_parameters[9]
    b_higher_thresh_1 = test_parameters[10]
    b_lower_thresh_2 = test_parameters[11]
    b_higher_thresh_2 = test_parameters[12]
    HSV_blur_k = test_parameters[13]
    LAB_blur_k = test_parameters[14]
    b_fill_k = test_parameters[15]
    LAB_fill_k = test_parameters[16]
    
    

    
    class args:
            #image = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\0214_2018-03-07 08.55 - 26_cam9.png"
            image = true_positive_file
            outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\output"
            debug = debug_setting
            result = "results.txt"
    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    pcv.params.debug = args.debug  # set debug mode
    pcv.params.debug_outdir = args.outdir  # set output directory

    # Read image
    img, path, filename = pcv.readimage(filename=args.image)

    #______________________________________________________________#### BEGIN HSV COLORSPACE WORKFLOW ###
    # Convert RGB to HSV and extract the saturation channel
    # Threshold the saturation
    

    s = pcv.rgb2gray_hsv(rgb_img=img, channel='s')
    s_thresh, maskeds_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[saturation_lower_tresh], upper_thresh=[saturation_higher_tresh], channel='gray')
    # Threshold the hue
    h = pcv.rgb2gray_hsv(rgb_img=img, channel='h')
    h_thresh, maskedh_image = pcv.threshold.custom_range(rgb_img=h, lower_thresh=[hue_lower_tresh], upper_thresh=[hue_higher_tresh], channel='gray')
    v = pcv.rgb2gray_hsv(rgb_img=img, channel='v')
    v_thresh, maskedv_image = pcv.threshold.custom_range(rgb_img=v, lower_thresh=[value_lower_tresh], upper_thresh=[value_higher_tresh], channel='gray')
    # Join saturation, Hue and Value
    sh = pcv.logical_and(bin_img1 = s_thresh, bin_img2 = h_thresh)
    hsv = pcv.logical_and(bin_img1 = sh, bin_img2=v_thresh)
    # Median Blur
    s_mblur = pcv.median_blur(gray_img=hsv, ksize= HSV_blur_k)
    #s_cnt = pcv.median_blur(gray_img=s_thresh, ksize=5)
    #______________________________________________________________#### END HSV COLORSPACE WORKFLOW ###
    
    #______________________________________________________________#### BEGIN CIELAB COLORSPACE WORKFLOW ###
    # Convert RGB to LAB and extract the Blue channel
    b = pcv.rgb2gray_lab(rgb_img=img, channel='b')

    # Threshold the blue image
    b_thresh = pcv.threshold.binary(gray_img=b, threshold=b_lower_thresh_1, max_value=b_higher_thresh_1, object_type='light')
    b_cnt = pcv.threshold.binary(gray_img=b, threshold=b_lower_thresh_1, max_value=b_higher_thresh_1, object_type='light')
    # Fill small objects
    b_cnt = pcv.fill(b_thresh, b_fill_k)        # If the fill step fails because of small objects try a smaller fill, else abort.

    # Join the thresholded saturation and blue-yellow images
    bs = pcv.logical_and(bin_img1=s_mblur, bin_img2=b_cnt)             # CHANGER OR TO AND

    # Apply Mask (for VIS images, mask_color=white)
    masked = pcv.apply_mask(rgb_img=img, mask=bs, mask_color='white')
    #Now the background is filtered away. Next step is to capture the plant.
    
    # Convert RGB to LAB and extract the Green-Magenta and Blue-Yellow channels
    masked_l = pcv.rgb2gray_lab(rgb_img=masked, channel='l')
    masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
    masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')
    # Threshold the green-magenta and blue images
    maskedl_thresh, maskedl_image = pcv.threshold.custom_range(rgb_img=masked_l, lower_thresh=[120], upper_thresh=[247], channel='gray')
    maskeda_thresh, maskeda_image = pcv.threshold.custom_range(rgb_img=masked_a, lower_thresh=[0], upper_thresh=[114], channel='gray')
    maskedb_thresh, maskedb_image = pcv.threshold.custom_range(rgb_img=masked_b, lower_thresh=[130], upper_thresh=[240], channel='gray')


    # Join the thresholded saturation and blue-yellow images (OR)
    ab1 = pcv.logical_and(bin_img1=maskeda_thresh, bin_img2=maskedb_thresh)
    ab = pcv.logical_and(bin_img1=maskedl_thresh, bin_img2=ab1)

    # Fill small objects
    ab_fill = pcv.median_blur(gray_img=ab, ksize= LAB_blur_k)
    ab_fill = pcv.fill(bin_img=ab_fill, size=LAB_fill_k)
    # Apply mask (for VIS images, mask_color=white)
    masked2 = pcv.apply_mask(rgb_img=masked, mask=ab_fill, mask_color='white')
    
    # Identify objects
    id_objects, obj_hierarchy = pcv.find_objects(img=masked2, mask=ab_fill)
    
    # Define ROI
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=0, y=0, h=960, w=1280)
    
    # Decide which objects to keep
    roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                                   roi_hierarchy=roi_hierarchy, 
                                                                   object_contour=id_objects, 
                                                                   obj_hierarchy=obj_hierarchy,
                                                                   roi_type='partial')
    
        # Object combine kept objects
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
    new_values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for item in input_parameters:
        new_values[i] = item
        i += 1
    random_para_nummer = random.randint(0,16)
    if random_para_nummer <= 12:
        step = np.round((np.random.normal(0, 5, 1)), 2)
        new_random_value = new_values[random_para_nummer] + (step)
        if new_random_value <= 0:
            new_random_value = 0
        elif new_random_value >= 255:
            new_random_value = 255
    
    elif random_para_nummer <= 14:                                   # Blur fill en k have alternative restraints because of computational reasons.
        step = int(np.random.normal(0, 3, 1))
        new_random_value = np.round(new_values[random_para_nummer] + (step), 0)
        if new_random_value <= 2:
            new_random_value = 2
        elif new_random_value >= 30:
            new_random_value = 30
            
    elif random_para_nummer <= 16:
        step = int(np.random.normal(0, 200, 1))
        new_random_value = np.round(new_values[random_para_nummer] + (step), 0)
        if new_random_value <= 1:
            new_random_value = 1
        elif new_random_value >= 5000:
            new_random_value = 5000
            
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
        try:
            similarity = compare(true_result, test_file, new_values)
        except:
            similarity = 0 # If the new parameters are extreme enough to let it crash it will assume similarity = 0
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
    
    counter_saturation_lower_tresh = item[0]
    counter_saturation_higher_tresh = item[1]
    counter_hue_lower_tresh = item[2]
    counter_hue_higher_tresh = item[3]
    counter_value_lower_tresh = item[4]
    counter_value_higher_tresh = item[5]
    counter_l_lower_thresh = item[6]
    counter_a_lower_thresh_1 = item[7]
    counter_a_lower_thresh_2 = item[8]
    counter_b_lower_thresh_1 = item[9]
    counter_b_higher_thresh_1 = item[10]
    counter_b_lower_thresh_2 = item[11]
    counter_b_higher_thresh_2 = item[12]
    counter_HSV_blur_k = item[13]
    counter_LAB_blur_k = item[14]
    counter_b_fill_k = item[15]
    counter_LAB_fill_k = item[16]
    counter_sets += 1
    

final_parameters = [counter_saturation_lower_tresh / counter_sets,  counter_saturation_higher_tresh / counter_sets,
                    counter_hue_lower_tresh / counter_sets,counter_hue_higher_tresh / counter_sets,
                    counter_value_lower_tresh / counter_sets, counter_value_higher_tresh / counter_sets,
                    counter_l_lower_thresh / counter_sets, counter_a_lower_thresh_1 / counter_sets,
                    counter_a_lower_thresh_2 / counter_sets, counter_b_lower_thresh_1 / counter_sets,
                    counter_b_higher_thresh_1 / counter_sets, counter_b_lower_thresh_2 / counter_sets,
                    counter_b_higher_thresh_2 / counter_sets, counter_HSV_blur_k / counter_sets,
                    counter_LAB_blur_k / counter_sets, counter_b_fill_k / counter_sets,
                   counter_LAB_fill_k / counter_sets]
print(final_parameters)
x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17] * counter_sets
x = ["sat_low", "sat_high", "hue_low", "hue_high", "val_low", "val_high", "l_low", "a_low1", "a_low2", "b_low1", "b_high1", "b_low2", "b_high2",
     "HSV_blur", "LAB_blur", "b_fill", "LAB_fill"] * counter_sets
y = []
for item in all_learned_parameters:
    for subitem in item:
        y.append(subitem)


plt.scatter(x, y, s=10)
plt.rcParams["figure.figsize"] = (20,10)
plt.xlabel("all parameters")
plt.ylabel("value")
plt.savefig("learned_para.png")
plt.show()

# Write all found parameters out in a file.
output = open("found_parameters.txt", "w")
output.write("sat_low, sat_high, hue_low, hue_high, val_low, val_high, l_low, a_low1, a_low2, b_low1, b_high1, b_low2, b_high2, HSV_blur, LAB_blur, b_fill, LAB_fill \n")
for item in all_learned_parameters:
    line = ""
    for subitem in item:
        line = line + str(subitem) + ", "
    line = line + "\n"
    output.write(line)
output.close()
