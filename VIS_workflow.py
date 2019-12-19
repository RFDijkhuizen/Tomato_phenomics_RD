"This workflow uses CieLABcolors rather than RGB"
import sys, traceback
import cv2
import numpy as np
import argparse
import string
from plantcv import plantcv as pcv
import plantcv.utils
import os
import glob
from PIL import Image, ImageDraw

import re

class args:
    image = ""
    outdir = "/output/"
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
pattern = ".*- (\d+.)\w+\d+.*"     # Pattern to get your genotype from filename
replacement = "\g<1>"               # Replacement regex to get your genotype
height = 200    # The boundary a plant should always fit in
width = 200     # The boundary a plant should always fit in
pattern_3d_file = ".*- (\d+.)_\d_3D.csv"

class HiddenPrints:                                # To surpress unnecessary warning messages
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

### Main workflow##############################################################################################################
"Main() is the workflow for the colored top pictures"     
###############################################################################################################################
def main():
    pcv.params.debug = args.debug  # set debug mode
    pcv.params.debug_outdir = args.outdir  # set output directory

    # Read image
    img, path, filename = pcv.readimage(filename=args.image)

    #______________________________________________________________#### BEGIN HSV COLORSPACE WORKFLOW ###
    # Convert RGB to HSV and extract the saturation channel
    # Threshold the saturation
    

    #print("Starting HSV workflow")
    s = pcv.rgb2gray_hsv(rgb_img=img, channel='s')
    s_thresh, maskeds_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[saturation_lower_tresh], upper_thresh=[saturation_higher_tresh], channel='gray')
    #print("thresholded on saturation")
    # Threshold the hue
    h = pcv.rgb2gray_hsv(rgb_img=img, channel='h')
    h_thresh, maskedh_image = pcv.threshold.custom_range(rgb_img=h, lower_thresh=[hue_lower_tresh], upper_thresh=[hue_higher_tresh], channel='gray')
    #print("thresholded on hue")
    v = pcv.rgb2gray_hsv(rgb_img=img, channel='v')
    v_thresh, maskedv_image = pcv.threshold.custom_range(rgb_img=v, lower_thresh=[value_lower_tresh], upper_thresh=[value_higher_tresh], channel='gray')
    #print("thresholded on value")
    # Join saturation, Hue and Value
    sh = pcv.logical_and(bin_img1 = s_thresh, bin_img2 = h_thresh)
    hsv = pcv.logical_and(bin_img1 = sh, bin_img2=v_thresh)
    # Median Blur
    s_mblur = pcv.median_blur(gray_img=hsv, ksize= HSV_blur_k)
    #s_cnt = pcv.median_blur(gray_img=s_thresh, ksize=5)
    #print("Blur on HSV")
    #______________________________________________________________#### END HSV COLORSPACE WORKFLOW ###
    
    #______________________________________________________________#### BEGIN CIELAB COLORSPACE WORKFLOW ###
    # Convert RGB to LAB and extract the Blue channel
    b = pcv.rgb2gray_lab(rgb_img=img, channel='b')

    # Threshold the blue image
    b_thresh = pcv.threshold.binary(gray_img=b, threshold=b_lower_thresh_1, max_value=b_higher_thresh_1, object_type='light')
    b_cnt = pcv.threshold.binary(gray_img=b, threshold=b_lower_thresh_1, max_value=b_higher_thresh_1, object_type='light')
    #print("thresholded on blue yellow channel")
    # Fill small objects
    b_cnt = pcv.fill(b_thresh, b_fill_k)        # If the fill step fails because of small objects try a smaller fill, else abort.
    #print("Filled blue channel mask")

    # Join the thresholded saturation and blue-yellow images
    bs = pcv.logical_and(bin_img1=s_mblur, bin_img2=b_cnt)             # CHANGER OR TO AND

    # Apply Mask (for VIS images, mask_color=white)
    masked = pcv.apply_mask(rgb_img=img, mask=bs, mask_color='white')
    #print("Masked image")
    #Now the background is filtered away. Next step is to capture the plant.
    
    # Convert RGB to LAB and extract the Green-Magenta and Blue-Yellow channels
    #print("LAB color space")
    masked_l = pcv.rgb2gray_lab(rgb_img=masked, channel='l')
    masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
    masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')
    # Threshold the green-magenta and blue images
    #print("LAB threshholds")
    maskedl_thresh, maskedl_image = pcv.threshold.custom_range(rgb_img=masked_l, lower_thresh=[120], upper_thresh=[247], channel='gray')
    maskeda_thresh, maskeda_image = pcv.threshold.custom_range(rgb_img=masked_a, lower_thresh=[0], upper_thresh=[114], channel='gray')
    maskedb_thresh, maskedb_image = pcv.threshold.custom_range(rgb_img=masked_b, lower_thresh=[130], upper_thresh=[240], channel='gray')


    # Join the thresholded saturation and blue-yellow images (OR)
    #print("Join the thresholds")
    ab1 = pcv.logical_and(bin_img1=maskeda_thresh, bin_img2=maskedb_thresh)
    ab = pcv.logical_and(bin_img1=maskedl_thresh, bin_img2=ab1)

    try:
        # Fill small objects
        ab_fill = pcv.median_blur(gray_img=ab, ksize= LAB_blur_k)
        ab_fill = pcv.fill(bin_img=ab_fill, size=LAB_fill_k)
        #print("final fill and blur")
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
        # Turn pseudocolored img off to prevent unnecessary output
        #pseudocolored_img = pcv.visualize.pseudocolor(gray_img=s, mask=kept_mask, cmap='jet')
        
        # Shape properties relative to user boundary line (optional)
        boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)
        new_im = Image.fromarray(boundary_img1)
        new_im.save("output//" + args.filename + "boundary_img.png")
        
        # Determine color properties: Histograms, Color Slices, output color analyzed histogram (optional)
        #color_img = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type = None)
        #new_im = Image.fromarray(color_img)
        #new_im.save(args.filename + "color_img.png")
        
        color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')
        
        # Find shape properties, output shape image (optional)
        shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
        
        # Find and annotate genotype
        new_im = Image.fromarray(shape_img)
        new_im.save("output//" + args.filename + "shape_img.png")
        GT = re.sub(pattern, replacement, filename)
        pcv.outputs.add_observation(variable = "genotype", trait = "genotype",
                                    method = "Regexed from the filename", scale = None,
                                    datatype = str, value = GT, label = "GT")
        
        # Write shape and color data to results file
        pcv.print_results(filename=args.result)

    except:
        print("not enough plant material found")

### Side workflow###################################################################################################################
"MainSide() is the workflow for the grayscale sidepictures"     
####################################################################################################################################

def main_side():
    # Setting "args"
    fill_k_side = 1000
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    # Read image (readimage mode defaults to native but if image is RGBA then specify mode='rgb')
    filename = args.image
    img = cv2.imread(args.image, flags=0)
    path, img_name = os.path.split(args.image)
    img_bkgrd = cv2.imread("background.png", flags=0)
    # Substract the background

    bkg_sub_img = pcv.image_subtract(img_bkgrd, img)
    bkg_sub_thres_img, masked_img = pcv.threshold.custom_range(rgb_img=bkg_sub_img, lower_thresh=[50], 
                                                               upper_thresh=[255], channel='gray')
    # Laplace filtering (identify edges based on 2nd derivative)
    lp_img = pcv.laplace_filter(gray_img=img, ksize=1, scale=1)
    
    # Plot histogram of grayscale values 
    # Turn this off to ease graphical output
    #pcv.visualize.histogram(gray_img=lp_img)

    # Lapacian image sharpening, this step will enhance the darkness of the edges detected
    lp_shrp_img = pcv.image_subtract(gray_img1=img, gray_img2=lp_img)

    # Plot histogram of grayscale values, this helps to determine thresholding value 
    pcv.visualize.histogram(gray_img=lp_shrp_img)
    # Sobel filtering
    # 1st derivative sobel filtering along horizontal axis, kernel = 1)
    # NOTE: Aperture size must be greater than the largest derivative (ksize > dx & ksize > dy) 
    sbx_img = pcv.sobel_filter(gray_img=img, dx=1, dy=0, ksize=1)

    # 1st derivative sobel filtering along vertical axis, kernel = 1)
    sby_img = pcv.sobel_filter(gray_img=img, dx=0, dy=1, ksize=1)

    # Combine the effects of both x and y filters through matrix addition
    sb_img = pcv.image_add(gray_img1=sbx_img, gray_img2=sby_img)
    
    # Use a lowpass (blurring) filter to smooth sobel image
    mblur_img = pcv.median_blur(gray_img=sb_img, ksize=3)
    mblur_invert_img = pcv.invert(gray_img=mblur_img)

    # combine the smoothed sobel image with the laplacian sharpened image
    # combines the best features of both methods as described in "Digital Image Processing" by Gonzalez and Woods pg. 169
    edge_shrp_img = pcv.image_add(gray_img1=mblur_invert_img, gray_img2=lp_shrp_img)

    # Perform thresholding to generate a binary image
    tr_es_img = pcv.threshold.binary(gray_img=edge_shrp_img, threshold=145, 
                                     max_value=255, object_type='dark')

    # Do erosion with a 3x3 kernel (ksize=3)
    e1_img = pcv.erode(gray_img=tr_es_img, ksize=3, i=1)
    # Bring the two object identification approaches together.
    # Using a logical OR combine object identified by background subtraction and the object identified by derivative filter.
    comb_img = pcv.logical_or(bin_img1=e1_img, bin_img2=bkg_sub_thres_img)

    # Get masked image, Essentially identify pixels corresponding to plant and keep those.
    masked_erd = pcv.apply_mask(rgb_img=img, mask=comb_img, mask_color='black')
    
    # Need to remove the edges of the image, we did that by generating a set of rectangles to mask the edges

    masked1, box1_img, rect_contour1, hierarchy1 = pcv.rectangle_mask(img=img, p1=(500,875), 
                                                                      p2=(720,960))
    # mask the edges
    masked2, box2_img, rect_contour2, hierarchy2 = pcv.rectangle_mask(img=img, p1=(1,1), 
                                                                      p2=(1279,959))
    bx12_img = pcv.logical_or(bin_img1=box1_img, bin_img2=box2_img)
    inv_bx1234_img = bx12_img # we dont invert
    inv_bx1234_img = pcv.fill(bin_img=inv_bx1234_img, size = fill_k_side)


    edge_masked_img = pcv.apply_mask(rgb_img=masked_erd, mask=inv_bx1234_img, 
                                     mask_color='black')
            #print("here we create a mask")
    mask, masked = pcv.threshold.custom_range(rgb_img=edge_masked_img, lower_thresh=[25], upper_thresh=[175], channel='gray')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
            #print("end")
    # Identify objects
    id_objects,obj_hierarchy = pcv.find_objects(img=edge_masked_img, mask=mask)

    # Define ROI
    roi1, roi_hierarchy= pcv.roi.rectangle(img=edge_masked_img, x=100, y=100, h=800, w=1000)

    # Decide which objects to keep

    with HiddenPrints():
        roi_objects, hierarchy5, kept_mask, obj_area = pcv.roi_objects(img=edge_masked_img, 
                                                                       roi_contour=roi1, 
                                                                       roi_hierarchy=roi_hierarchy, 
                                                                       object_contour=id_objects, 
                                                                       obj_hierarchy=obj_hierarchy, 
                                                                       roi_type='largest')
    
    rgb_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    o, m = pcv.object_composition(img=rgb_img, contours=roi_objects, hierarchy=hierarchy5)
    
### Analysis ###

    outfile=False
    if args.writeimg==True:
        outfile=args.outdir+"/"+filename

    # Perform signal analysis   
    shape_img = pcv.analyze_object(img=img, obj=o, mask=m)
    new_im = Image.fromarray(shape_img)
    new_im.save("output//" + args.filename + "shape_img_side.png")
    nir_hist = pcv.analyze_nir_intensity(gray_img=img, mask=kept_mask, 
                                         bins=256, histplot=True)

    top, bottom, center_v = pcv.x_axis_pseudolandmarks(img, o, mask)
    left, right, center_h  = pcv.y_axis_pseudolandmarks(img, o, mask)  # This makes everything crash and explode

    # Pseudocolor the grayscale image to a colormap
    # Turn pseudocolored img off to prevent unnecessary output
    #pseudocolored_img = pcv.visualize.pseudocolor(gray_img=img, mask=kept_mask, cmap='viridis')


    GT = re.sub(pattern, replacement, filename)
    pcv.outputs.add_observation(variable = "genotype", trait = "genotype",
                                method = "Regexed from the filename", scale = None,
                                datatype = str, value = GT, label = "GT")

    # Write shape and nir data to results file
    pcv.print_results(filename=args.result)


### 3D workflow###################################################################################################################
"Silhouette_top() is the workflow for the 3d DATA"     
##################################################################################################################################
def workflow_3d():
    "First we draw the picture from the 3D data"
    x = []
    y = []
    z = []
    image_top = Image.new("RGB", (width, height), color = 'white')
    draw = ImageDraw.Draw(image_top)
    data_3d = open(args.image, "r")
    for line in data_3d:
        line = line.split(",")
        y.append(int(line[0]))
        x.append(int(line[1]))
        z.append(int(line[2]))
        
    i = 0
    for point_x in x:
        point_y = y[i]
        draw.rectangle([point_x, point_y, point_x, point_y], fill = "black")
        #rectange takes input [x0, y0, x1, y1]
        i += 1
    image_top.save("output//" + args.filename + "top_3D.png")
    
    image_side = Image.new("RGB", (width, height), color = 'white')
    draw = ImageDraw.Draw(image_side)
    i = 0
    for point_y in y:
        point_z = z[i]
        draw.rectangle([point_z, point_y, point_z, point_y], fill = "black")
        #rectange takes input [x0, y0, x1, y1]
        i += 1
    image_side = image_side.rotate(90)
    image_side.save("output//" + args.filename + "side_3D.png")
    
                                                # We have now drawn the images, time to move on to analysis
    
    args.image = "output//" + args.filename + "top_3D.png"
    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    pcv.params.debug = args.debug  # set debug mode
    pcv.params.debug_outdir = args.outdir  # set output directory

    # Read image
    img, path, filename = pcv.readimage(filename=args.image)
    
    v = pcv.rgb2gray_hsv(rgb_img=img, channel='v')
    v_thresh, maskedv_image = pcv.threshold.custom_range(rgb_img=v, lower_thresh=[0], upper_thresh=[200], channel='gray')
    
    id_objects, obj_hierarchy = pcv.find_objects(img=maskedv_image, mask=v_thresh)
    
    # Define ROI
    roi1, roi_hierarchy= pcv.roi.rectangle(img=maskedv_image, x=0, y=0, h=height, w=width)
    
    # Decide which objects to keep
    roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                               roi_hierarchy=roi_hierarchy, 
                                                               object_contour=id_objects, 
                                                               obj_hierarchy=obj_hierarchy,
                                                               roi_type='partial')
    
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)
    outfile=args.outdir+"/"+filename
        
    skeleton = pcv.morphology.skeletonize(mask)
    try:
        skeleton, segmented_img, segment_objects = pcv.morphology.prune(skel_img=skeleton, size=5) # Prune to remove barbs
    except: # passes plants too small to be pruned
        skeleton, segmented_img, segment_objects = pcv.morphology.prune(skel_img=skeleton, size=0) # Prune to remove barbs

    new_im = Image.fromarray(skeleton)
    new_im.save("output//" + args.filename + "_top_skeleton.png")
    
    pcv.params.line_thickness = 3 # just for debugging
    leaf_obj, other_obj = pcv.morphology.segment_sort(skel_img=skeleton, objects=segment_objects, mask=mask)
    
    segmented_img, segmented_obj = pcv.morphology.segment_skeleton(skel_img=skeleton)
    new_im = Image.fromarray(segmented_img)
    new_im.save("output//" + args.filename + "top_segmented_skeleton.png")
    
    cycle_img = pcv.morphology.check_cycles(skel_img=skeleton)
    new_im = Image.fromarray(cycle_img)
    new_im.save("output//" + args.filename + "top_cycle_skeleton.png")

    if leaf_obj:
        with HiddenPrints():
            pcv.morphology.segment_angle(segmented_img = segmented_img, objects = leaf_obj)
            leaf_angles_values = pcv.outputs.observations['segment_angle']['value']
            leaf_angles_labels = pcv.outputs.observations['segment_angle']['label']
    
            pcv.outputs.add_observation(variable = "top_leaf_angles", trait = "top_leaf_angles",
                                        method = "plantcv.morphology.segment_angle",
                                        scale = "degrees", datatype = float,
                                        value = leaf_angles_values, label = leaf_angles_labels)
    if other_obj:
        with HiddenPrints():
            pcv.morphology.segment_angle(segmented_img = segmented_img, objects = other_obj)
            stem_angles_values = pcv.outputs.observations['segment_angle']['value']
            stem_angles_labels = pcv.outputs.observations['segment_angle']['label']
        
            pcv.outputs.add_observation(variable = "top_stem_angles", trait = "top_stem_angles",
                                        method = "plantcv.morphology.segment_angle",
                                        scale = "degrees", datatype = float,
                                        value = stem_angles_values, label = stem_angles_labels)
    if segmented_obj:
        with HiddenPrints():
            pcv.morphology.segment_angle(segmented_img, segmented_obj)
            #new_im = Image.fromarray(seg_angle_img)
            #new_im.save("output//" + args.filename + "top_seg_angle.png")

    path_length_img = pcv.morphology.segment_path_length(segmented_img, leaf_obj)
    leaf_length_values = pcv.outputs.observations['segment_path_length']['value']
    leaf_length_labels = pcv.outputs.observations['segment_path_length']['value']

    pcv.outputs.add_observation(variable = "top_leaf_length", trait = "top_leaf_lengths",
                                method = "plantcv.morphology.segment_angle",
                                scale = "pixels", datatype = float,
                                value = leaf_length_values, label = leaf_length_labels)

    path_length_img = pcv.morphology.segment_path_length(segmented_img, other_obj)
    stem_length_values = pcv.outputs.observations['segment_path_length']['value']
    stem_length_labels = pcv.outputs.observations['segment_path_length']['value']

    pcv.outputs.add_observation(variable = "top_stem_length", trait = "top_stem_lengths",
                                method = "plantcv.morphology.segment_angle",
                                scale = "pixels", datatype = float,
                                value = stem_length_values, label = stem_length_labels)

    path_length_img = pcv.morphology.segment_path_length(segmented_img, segmented_obj)
    new_im = Image.fromarray(path_length_img)
    new_im.save("output//" + args.filename + "top_seg_length.png")
    
    # Shape properties relative to user boundary line (optional)
    boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)
    new_im = Image.fromarray(boundary_img1)
    new_im.save("output//" + args.filename + "_top_boundary.png")

    # Find shape properties, output shape image (optional)
    shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
    try:
        new_im = Image.fromarray(shape_img)
        new_im.save("output//" + args.filename + "_top_shape.png")
    except:
        print("non fatal shape analyze error. Shape analysis could not be drawn") # weird error that happens 1 in ~1000 pictures.
    
    # Find all leaf tips
    try:
        list_of_acute_points, point_img = pcv.acute_vertex(img, obj, 10, 80, 20)
        new_im = Image.fromarray(point_img)
        new_im.save("output//" + args.filename + "_top_point_img.png")
    except:
        print("no acute points found")
    
    # Watershed image to find all leafs
    analysis_image = pcv.watershed_segmentation(img, mask, 8)
    new_im = Image.fromarray(analysis_image)
    new_im.save("output//" + args.filename + "_leaves.png")
        
    GT = re.sub(pattern_3d_file, replacement, files_names[file_counter])
    pcv.outputs.add_observation(variable = "genotype", trait = "genotype",
                                method = "Regexed from the filename", scale = None,
                                datatype = str, value = GT, label = "GT")
    
    # Write shape and color data to results file
    pcv.print_results(filename=args.result)
    
    #   #   #   #   #   #   #   #   #   #    # Now do approximately the same for the side pic
    
    pcv.outputs.clear()
    args.image = ("output//" + args.filename + "side_3D.png")
    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    pcv.params.debug = args.debug  # set debug mode
    pcv.params.debug_outdir = args.outdir  # set output directory

    # Read image
    img, path, filename = pcv.readimage(filename=args.image)
    
    v = pcv.rgb2gray_hsv(rgb_img=img, channel='v')
    v_thresh, maskedv_image = pcv.threshold.custom_range(rgb_img=v, lower_thresh=[0], upper_thresh=[200], channel='gray')
    
    id_objects, obj_hierarchy = pcv.find_objects(img=maskedv_image, mask=v_thresh)
    
    # Define ROI
    roi1, roi_hierarchy= pcv.roi.rectangle(img=maskedv_image, x=0, y=0, h=height, w=width)
    
    # Decide which objects to keep
    roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                               roi_hierarchy=roi_hierarchy, 
                                                               object_contour=id_objects, 
                                                               obj_hierarchy=obj_hierarchy,
                                                               roi_type='partial')
    
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)
    outfile=args.outdir+"/"+filename
    
    skeleton = pcv.morphology.skeletonize(mask)
    try:
        skeleton, segmented_img, segment_objects = pcv.morphology.prune(skel_img=skeleton, size=5) # Prune to remove barbs
    except: # passes plants too small to be pruned
        skeleton, segmented_img, segment_objects = pcv.morphology.prune(skel_img=skeleton, size=0) # Prune to remove barbs
    new_im = Image.fromarray(skeleton)
    new_im.save("output//" + args.filename + "_side_skeleton.png")
    leaf_obj, other_obj = pcv.morphology.segment_sort(skel_img=skeleton, objects=segment_objects, mask=mask)

    segmented_img, segmented_obj = pcv.morphology.segment_skeleton(skel_img=skeleton)
    new_im = Image.fromarray(segmented_img)
    new_im.save("output//" + args.filename + "side_segmented_skeleton.png")
    
    cycle_img = pcv.morphology.check_cycles(skel_img=skeleton)
    new_im = Image.fromarray(cycle_img)
    new_im.save("output//" + args.filename + "side_cycle_skeleton.png")
    
    if leaf_obj:   # If object list is not empty
        with HiddenPrints():
            pcv.morphology.segment_angle(segmented_img = segmented_img, objects = leaf_obj)
            leaf_angles_values = pcv.outputs.observations['segment_angle']['value']
            leaf_angles_labels = pcv.outputs.observations['segment_angle']['label']
    
            pcv.outputs.add_observation(variable = "side_leaf_angles", trait = "side_leaf_angles",
                                        method = "plantcv.morphology.segment_angle",
                                        scale = "degrees", datatype = float,
                                        value = leaf_angles_values, label = leaf_angles_labels)

    if other_obj:   # If object list is not empty
        with HiddenPrints():
            pcv.morphology.segment_angle(segmented_img = segmented_img, objects = other_obj)

            stem_angles_values = pcv.outputs.observations['segment_angle']['value']
            stem_angles_labels = pcv.outputs.observations['segment_angle']['label']
    
            pcv.outputs.add_observation(variable = "side_stem_angles", trait = "side_stem_angles",
                                        method = "plantcv.morphology.segment_angle",
                                        scale = "degrees", datatype = float,
                                        value = stem_angles_values, label = stem_angles_labels)
    if segmented_obj:
        with HiddenPrints():
            pcv.morphology.segment_angle(segmented_img, segmented_obj)
            #new_im = Image.fromarray(seg_angle_img)
            #new_im.save("output//" + args.filename + "side_seg_angle.png")
    
    path_length_img = pcv.morphology.segment_path_length(segmented_img, segmented_obj)
    new_im = Image.fromarray(path_length_img)
    new_im.save("output//" + args.filename + "side_seg_length.png")
    


    
    # Shape properties relative to user boundary line (optional)
    boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)
    new_im = Image.fromarray(boundary_img1)
    new_im.save("output//" + args.filename + "_side_boundary.png")

    # Find shape properties, output shape image (optional)
    shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
    try:
        new_im = Image.fromarray(shape_img)
        new_im.save("output//" + args.filename + "_side_shape.png")
    except:
        print("non fatal shape analyze error. Shape analysis could not be drawn") # weird error that happens 1 in ~1000 pictures.
    
    # Find all leaf tips
    try:
        list_of_acute_points, point_img = pcv.acute_vertex(img, obj, 20, 80, 40)
        new_im = Image.fromarray(point_img)
        new_im.save("output//" + args.filename + "_side_point_img.png")
    except:
        print("no acute points found")


    
    GT = re.sub(pattern_3d_file, replacement, files_names[file_counter])
    pcv.outputs.add_observation(variable = "genotype", trait = "genotype",
                                method = "Regexed from the filename", scale = None,
                                datatype = str, value = GT, label = "GT")
    #Write shape and color data to results file
    pcv.print_results(filename=args.result_side)





### Test on subset ###############################################################################################################
"To test on a subset set do_subset to True, and do_all to False"  
##################################################################################################################################
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
    for item in top_files:
        args.image = item
        args.debug = "plot"
        #args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\subset\\"
        args.outdir = "/subset/"
        args.result = "subset/" + top_files_names[file_counter][0:-4] + "top_results.txt"
        args.filename = top_files_names[file_counter][0:-4]
        main()
        file_counter += 1
        print("handled top picture %i of %i" %(file_counter, len(top_files)))

    # Now the 3D workflow
    files = []          # absolute paths uses for processing
    files_names = []    # The names used for storing 
    temp = glob.glob("subset//*3D.csv")
    for item in temp:
        files_names.append(os.path.basename(item))
        files.append(os.path.join(wd, item))
 
    file_counter = 0
    for item in files:
        args.image = item
        args.debug = "None"
        #args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\subset\\"
        args.outdir = "/subset/"
        args.result = "subset//" + files_names[file_counter][0:-4] + "silhouette_results.txt"
        args.result_side = "output//" + files_names[file_counter][0:-4] + "_side_results.txt"
        args.filename = files_names[file_counter][0:-4]
        workflow_3d()
        file_counter += 1
        print("handled top picture %i of %i" %(file_counter, len(files)))
    
### Do on all data ###############################################################################################################
"To perform the script on all data set do_all to True and do_subset to False"  
##################################################################################################################################
    
do_all = True
if do_all == True:      
    wd = os.getcwd()
    args.debug = "None"
    top_files = []          # absolute paths uses for processing
    top_files_names = []    # The names used for storing 
    temp = glob.glob("input//*cam9.png")
    for item in temp:
        top_files_names.append(os.path.basename(item))
        top_files.append(os.path.join(wd, item))
    side_files = []          # absolute paths uses for processing
    side_files_names = []    # The names used for storing 
    temp = glob.glob("input//*cam0.png")
    for item in temp:
        side_files_names.append(os.path.basename(item))
        side_files.append(os.path.join(wd, item))

        
    file_counter = 0
    for item in top_files:
        pcv.outputs.clear() # To make sure you start clean
        args.image = item
        args.outdir = "/output/"
        args.result = "output//" + top_files_names[file_counter][0:-4] + "top_results.txt"
        args.filename = top_files_names[file_counter][0:-4]
        main()
        file_counter += 1
        print("handled top picture %i of %i" %(file_counter, len(top_files)))
        
    file_counter = 0
    for item in side_files:
        pcv.outputs.clear() # To make sure you start clean
        args.image = item
        #background = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\side_perspective\\background.png"
        background = "background.png"
        args.outdir = "/output/"
        args.writeimg = True
        args.result = "output//" + side_files_names[file_counter][0:-4] + "side_results.txt"
        args.filename = side_files_names[file_counter][0:-4]
        main_side()
        file_counter += 1
        print("handled side picture %i of %i" %(file_counter, len(side_files)))
        
        
    # Now the 3D workflow
    files = []          # absolute paths uses for processing
    files_names = []    # The names used for storing 
    temp = glob.glob("input//*3D.csv")
    for item in temp:
        files_names.append(os.path.basename(item))
        files.append(os.path.join(wd, item))

    file_counter = 0
    for item in files:
        pcv.outputs.clear() # To make sure you start clean
        args.image = item
        args.outdir = "/output/"
        args.result = "output//" + files_names[file_counter][0:-4] + "_top_results.txt"
        args.result_side = "output//" + files_names[file_counter][0:-4] + "_side_results.txt"
        args.filename = files_names[file_counter][0:-4]
        workflow_3d()
        file_counter += 1
        print("handled dataset %i of %i" %(file_counter, len(files)))
        
#json_files = glob.glob("*.JSON")
#wd = os.getcwd()
#for file in json_files:
#    json_name = file
#    print(json_name)
#    new_name = json_name[0:-4]
#    plantcv.utils.json2csv(json_file = json_name, csv_file = new_name)
