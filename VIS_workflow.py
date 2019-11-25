"This workflow uses CieLABcolors rather than RGB"
import sys, traceback
import cv2
import numpy as np
import argparse
import string
from plantcv import plantcv as pcv
import os
import glob
from PIL import Image
import re

class args:
    image = ""
    outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\output"
    debug = "None"
    result = ""
    filename = ""


## Parameters
"HSV color space"
saturation_lower_tresh = 120        # 130
saturation_higher_tresh = 240       # 240
hue_lower_tresh = 18                # 18
hue_higher_tresh = 55               # 55
value_lower_tresh = 70              # 70
value_higher_tresh = 255            # 250
HSV_blur_k = 3                      # 3
"CIELAB color space"
l_lower_thresh = 130                # 130 Lower light thresh to be considered plant # original 125
l_higher_thresh = 255               # 255 Higher thresh to be considered plant.
a_lower_thresh_1 = 118              # 118 Lower thresh to be considered plant
a_lower_thresh_2 = 138              # 138 Lower thresh to be considered too magenta to be plant
b_lower_thresh_1 = 165              # 165 Threshold to filter background away
b_higher_thresh_1 = 245             # 245 Threshold to filter background away
b_lower_thresh_2 = 120              # 120 Threshold to capture plant
b_higher_thresh_2 = 255             # 255 Threshold to capture plant
b_fill_k = 1000                     # 1000 Fill to make sure we do not lose anything
LAB_fill_k = 1500                   # 1500 Fill kernel for the LAB filtered image
LAB_blur_k = 10                     # 10 Final Blur
pattern = ".*- (\d+)\w+\d+.png"     # Pattern to get your genotype from filename
replacement = "\g<1>"               # Replacement regex to get your genotype
### Main workflow
def main():
    pcv.params.debug = args.debug  # set debug mode
    pcv.params.debug_outdir = args.outdir  # set output directory

    # Read image
    img, path, filename = pcv.readimage(filename=args.image)

    #______________________________________________________________#### BEGIN HSV COLORSPACE WORKFLOW ###
    # Convert RGB to HSV and extract the saturation channel
    # Threshold the saturation
    

    print("Starting HSV workflow")
    s = pcv.rgb2gray_hsv(rgb_img=img, channel='s')
    s_thresh, maskeds_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[saturation_lower_tresh], upper_thresh=[saturation_higher_tresh], channel='gray')
    print("thresholded on saturation")
    # Threshold the hue
    h = pcv.rgb2gray_hsv(rgb_img=img, channel='h')
    h_thresh, maskedh_image = pcv.threshold.custom_range(rgb_img=h, lower_thresh=[hue_lower_tresh], upper_thresh=[hue_higher_tresh], channel='gray')
    print("thresholded on hue")
    v = pcv.rgb2gray_hsv(rgb_img=img, channel='v')
    v_thresh, maskedv_image = pcv.threshold.custom_range(rgb_img=v, lower_thresh=[value_lower_tresh], upper_thresh=[value_higher_tresh], channel='gray')
    print("thresholded on value")
    # Join saturation, Hue and Value
    sh = pcv.logical_and(bin_img1 = s_thresh, bin_img2 = h_thresh)
    hsv = pcv.logical_and(bin_img1 = sh, bin_img2=v_thresh)
    # Median Blur
    s_mblur = pcv.median_blur(gray_img=hsv, ksize= HSV_blur_k)
    #s_cnt = pcv.median_blur(gray_img=s_thresh, ksize=5)
    print("Blur on HSV")
    #______________________________________________________________#### END HSV COLORSPACE WORKFLOW ###
    
    #______________________________________________________________#### BEGIN CIELAB COLORSPACE WORKFLOW ###
    # Convert RGB to LAB and extract the Blue channel
    b = pcv.rgb2gray_lab(rgb_img=img, channel='b')

    # Threshold the blue image
    b_thresh = pcv.threshold.binary(gray_img=b, threshold=b_lower_thresh_1, max_value=b_higher_thresh_1, object_type='light')
    b_cnt = pcv.threshold.binary(gray_img=b, threshold=b_lower_thresh_1, max_value=b_higher_thresh_1, object_type='light')
    print("thresholded on blue yellow channel")
    # Fill small objects
    b_cnt = pcv.fill(b_thresh, b_fill_k)        # If the fill step fails because of small objects try a smaller fill, else abort.
    print("Filled blue channel mask")

    # Join the thresholded saturation and blue-yellow images
    bs = pcv.logical_and(bin_img1=s_mblur, bin_img2=b_cnt)             # CHANGER OR TO AND

    # Apply Mask (for VIS images, mask_color=white)
    masked = pcv.apply_mask(rgb_img=img, mask=bs, mask_color='white')
    print("Masked image")
    #Now the background is filtered away. Next step is to capture the plant.
    
    # Convert RGB to LAB and extract the Green-Magenta and Blue-Yellow channels
    print("LAB color space")
    masked_l = pcv.rgb2gray_lab(rgb_img=masked, channel='l')
    masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
    masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')
    # Threshold the green-magenta and blue images
    print("LAB threshholds")
    maskedl_thresh, maskedl_image = pcv.threshold.custom_range(rgb_img=masked_l, lower_thresh=[120], upper_thresh=[247], channel='gray')
    maskeda_thresh, maskeda_image = pcv.threshold.custom_range(rgb_img=masked_a, lower_thresh=[0], upper_thresh=[114], channel='gray')
    maskedb_thresh, maskedb_image = pcv.threshold.custom_range(rgb_img=masked_b, lower_thresh=[130], upper_thresh=[240], channel='gray')


    # Join the thresholded saturation and blue-yellow images (OR)
    print("Join the thresholds")
    ab1 = pcv.logical_and(bin_img1=maskeda_thresh, bin_img2=maskedb_thresh)
    ab = pcv.logical_and(bin_img1=maskedl_thresh, bin_img2=ab1)

    try:
        # Fill small objects
        ab_fill = pcv.median_blur(gray_img=ab, ksize= LAB_blur_k)
        ab_fill = pcv.fill(bin_img=ab_fill, size=LAB_fill_k)
        print("final fill and blur")
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
            ############### Analysis ################
        
        outfile=args.outdir+"/"+filename
            # Pseudocolor the grayscale image
        pseudocolored_img = pcv.visualize.pseudocolor(gray_img=s, mask=kept_mask, cmap='jet')
        
        # Shape properties relative to user boundary line (optional)
        boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)
        new_im = Image.fromarray(boundary_img1)
        new_im.save("output//" + args.filename + "boundary_img.png")
        
        # Determine color properties: Histograms, Color Slices, output color analyzed histogram (optional)
        color_img = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type = None)
        #new_im = Image.fromarray(color_img)
        #new_im.save(args.filename + "color_img.png")
        
        color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')
        
        # Find shape properties, output shape image (optional)

        shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
        new_im = Image.fromarray(shape_img)
        new_im.save("output//" + args.filename + "shape_img.png")
        GT = re.sub(pattern, replacement, filename)
        pcv.outputs.add_observation(variable = "genotype", trait = "The genotype",
                                    method = "Regexed from the filename", scale = None,
                                    datatype = str, value = int(GT), label = "GT")
        
        # Write shape and color data to results file
        pcv.print_results(filename=args.result)

    except:
        print("not enough plant material found")

# Calling functions # subset
    
do_subset = False
if do_subset == True:
    wd = os.getcwd()
    top_files = []          # absolute paths uses for processing
    top_files_names = []    # The names used for storing 
    temp = glob.glob("subset//*cam9.png")
    for item in temp:
        top_files_names.append(os.path.basename(item))
        top_files.append(os.path.join(wd, item))
    side_files = []          # absolute paths uses for processing
    side_files_names = []    # The names used for storing 
    temp = glob.glob("subset//*cam0.png")
    for item in temp:
        side_files_names.append(os.path.basename(item))
        side_files.append(os.path.join(wd, item))
        
    file_counter = 0
    for item in top_files[0:1]:
        args.image = item
        args.debug = "plot"
        args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\subset\\"
        args.result = "subset//" + top_files_names[file_counter][0:-4] + "top_results.txt"
        args.filename = top_files_names[file_counter][0:-4]
        main()
        file_counter += 1
        print("handled top picture %i of %i" %(file_counter, len(top_files)))
  
    
do_all = True
if do_all == True:      
    wd = os.getcwd()
    args.debug = "None"
    top_files = []          # absolute paths uses for processing
    top_files_names = []    # The names used for storing 
    temp = glob.glob("top_input//*cam9.png")
    for item in temp:
        top_files_names.append(os.path.basename(item))
        top_files.append(os.path.join(wd, item))
    side_files = []          # absolute paths uses for processing
    side_files_names = []    # The names used for storing 
    temp = glob.glob("side_input//*cam0.png")
    for item in temp:
        side_files_names.append(os.path.basename(item))
        side_files.append(os.path.join(wd, item))
        
    file_counter = 0
    for item in top_files:
        args.image = item
        args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\output\\"
        args.result = "output//" + top_files_names[file_counter][0:-4] + "top_results.txt"
        args.filename = top_files_names[file_counter][0:-4]
        main()
        file_counter += 1
        print("handled top picture %i of %i" %(file_counter, len(top_files)))
        
            
