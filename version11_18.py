import numpy as np
from plantcv import plantcv as pcv
from PIL import Image
import cv2
import os
import glob
import sys

class args:
    image = ""
    outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\output"
    debug = "None"
    result = ""
    filename = ""
    
class HiddenPrints:                                # To surpress unnecessary warning messages
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

### Set working directory
################################################___________________________________________ TOP DOWN PERSPECTIVE

### Main workflow
def main():

    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    # Read image (readimage mode defaults to native but if image is RGBA then specify mode='rgb')
    # Inputs:
    #   filename - Image file to be read in 
    #   mode - Return mode of image; either 'native' (default), 'rgb', 'gray', or 'csv'
    img, path, filename = pcv.readimage(filename=args.image, mode='rgb')
    
    ### SELECTING THE PLANT



    ### Attempt 5 combineren
    # Parameters
    hue_lower_tresh = 22                # 24
    hue_higher_tresh = 50               # 50
    saturation_lower_tresh = 138        # 140
    saturation_higher_tresh = 230       # 230
    value_lower_tresh = 125             # 125
    value_higher_tresh = 255            # 255
    green_lower_tresh = 105             # 110
    green_higher_tresh = 255            # 255
    red_lower_tresh = 24                # 24
    red_higher_thresh = 98             # 98
    blue_lower_tresh = 85               # 85
    blue_higher_tresh = 253             # 255
    
    
    #print("Select on green")
    s = pcv.rgb2gray_hsv(rgb_img=img, channel='h')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[hue_lower_tresh], upper_thresh=[hue_higher_tresh], channel='gray')
    masked = pcv.apply_mask(rgb_img=img, mask = mask, mask_color = 'white')
    print("filtered on hue")
    s = pcv.rgb2gray_hsv(rgb_img=masked, channel='s')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[saturation_lower_tresh], upper_thresh=[saturation_higher_tresh], channel='gray')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    print("filtered on saturation")
    s = pcv.rgb2gray_hsv(rgb_img=masked, channel='v')
    mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[value_lower_tresh], upper_thresh=[value_higher_tresh], channel='gray')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    print("filtered on value")
    mask, masked = pcv.threshold.custom_range(rgb_img=masked, lower_thresh=[0,green_lower_tresh,0], upper_thresh=[255,green_higher_tresh,255], channel='RGB')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    print("filtered on green")
    mask, masked = pcv.threshold.custom_range(rgb_img=masked, lower_thresh=[red_lower_tresh,0,0], upper_thresh=[red_higher_thresh,255,255], channel='RGB')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    print("filtered on red")
    mask_old, masked_old = pcv.threshold.custom_range(rgb_img=masked, lower_thresh=[0,0,blue_lower_tresh], upper_thresh=[255,255,blue_higher_tresh], channel='RGB')
    masked = pcv.apply_mask(rgb_img=masked_old, mask = mask_old, mask_color = 'white')
    print("filtered on blue")
    ###____________________________________ Blur to minimize 
    try:
        s_mblur = pcv.median_blur(gray_img = masked_old, ksize = 3)
        s = pcv.rgb2gray_hsv(rgb_img=s_mblur, channel='v')
        mask, masked_image = pcv.threshold.custom_range(rgb_img=s, lower_thresh=[0], upper_thresh=[254], channel='gray')
    except:
        print("failed blur step")
    try:
        mask = pcv.fill(masked, 3)
    except:
        masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
        print("failed fill step")


    ###_____________________________________ Now to identify objects
    masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
    masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')
    
     # Threshold the green-magenta and blue images
    maskeda_thresh = pcv.threshold.binary(gray_img=masked_a, threshold=125, # original 115
                                      max_value=255, object_type='dark')
    maskeda_thresh1 = pcv.threshold.binary(gray_img=masked_a, threshold=140, # original 135
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
    print("filled")
    # Apply mask (for VIS images, mask_color=white)
    masked2 = pcv.apply_mask(rgb_img=masked, mask=ab_fill, mask_color='white')
    # ID the objects
    id_objects, obj_hierarchy = pcv.find_objects(masked2, ab_fill)
    # Let's just take the largest
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=0, y=0, h=960, w=1280)  # Currently hardcoded
    
    # Decide which objects to keep
    # Inputs:
    #    img            = img to display kept objects
    #    roi_contour    = contour of roi, output from any ROI function
    #    roi_hierarchy  = contour of roi, output from any ROI function
    #    object_contour = contours of objects, output from pcv.find_objects function
    #    obj_hierarchy  = hierarchy of objects, output from pcv.find_objects function
    #    roi_type       = 'partial' (default, for partially inside), 'cutto', or 
    #    'largest' (keep only largest contour)
    with HiddenPrints():
        roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                                       roi_hierarchy=roi_hierarchy, 
                                                                       object_contour=id_objects, 
                                                                       obj_hierarchy=obj_hierarchy,
                                                                       roi_type='largest')
     # Object combine kept objects
    # Inputs:
    #   img - RGB or grayscale image data for plotting 
    #   contours - Contour list 
    #   hierarchy - Contour hierarchy array 
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)
    print("final plant")
    new_im = Image.fromarray(masked2)
    new_im.save("output//" + args.filename + "last_masked.png")

    ##################_________________ Analysis

    outfile=args.outdir+"/"+filename
    # Here come all the analyse functions.
    # pcv.acute_vertex(img, obj, 30, 15, 100)
    
    color_img = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type = None)
    #new_im = Image.fromarray(color_img)
    #new_im.save(args.filename + "color_img.png")
    
    # Find shape properties, output shape image (optional)

    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj- Single or grouped contour object
    #   mask - Binary image mask to use as mask for moments analysis     
    shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
    new_im = Image.fromarray(shape_img)
    new_im.save("output//" + args.filename + "shape_img.png")
    # Shape properties relative to user boundary line (optional)

    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj - Single or grouped contour object 
    #   mask - Binary mask of selected contours 
    #   line_position - Position of boundary line (a value of 0 would draw a line 
    #                   through the bottom of the image) 
    boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, 
                                                   line_position=1680)
    new_im = Image.fromarray(boundary_img1)
    new_im.save("output//" + args.filename + "boundary_img.png")
    # Determine color properties: Histograms, Color Slices, output color analyzed histogram (optional)

    # Inputs:
    #   rgb_img - RGB image data
    #   mask - Binary mask of selected contours 
    #   hist_plot_type - None (default), 'all', 'rgb', 'lab', or 'hsv'
    #                    This is the data to be printed to the SVG histogram file  
    color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')
    #new_im = Image.fromarray(color_histogram)
    #new_im.save(args.filename + "color_histogram_img.png")

    # Pseudocolor the grayscale image

    # Inputs:
    #     gray_img - Grayscale image data
    #     obj - Single or grouped contour object (optional), if provided the pseudocolored image gets 
    #           cropped down to the region of interest.
    #     mask - Binary mask (optional) 
    #     background - Background color/type. Options are "image" (gray_img, default), "white", or "black". A mask 
    #                  must be supplied.
    #     cmap - Colormap
    #     min_value - Minimum value for range of interest
    #     max_value - Maximum value for range of interest
    #     dpi - Dots per inch for image if printed out (optional, if dpi=None then the default is set to 100 dpi).
    #     axes - If False then the title, x-axis, and y-axis won't be displayed (default axes=True).
    #     colorbar - If False then the colorbar won't be displayed (default colorbar=True)
    pseudocolored_img = pcv.visualize.pseudocolor(gray_img=s, mask=kept_mask, cmap='jet')
    #new_im = Image.fromarray(pseudocolored_img)
    #new_im.save(args.filename + "pseudocolored.png")

    # Write shape and color data to results file
    pcv.print_results(filename=args.result)

    ##########################################################___________________________________________ SIDE PERSPECTIVE

### Main workflow
def main_side():
    # Setting "args"
    
    # Get options
    pcv.params.debug=args.debug #set debug mode
    pcv.params.debug_outdir=args.outdir #set output directory

    # Read image (readimage mode defaults to native but if image is RGBA then specify mode='rgb')
    # Inputs:
    #   filename - Image file to be read in 
    #   mode - Return mode of image; either 'native' (default), 'rgb', 'gray', or 'csv'
    filename = args.image
    img = cv2.imread(args.image, flags=0)
    #img = pcv.invert(img)
    path, img_name = os.path.split(args.image)
    img_bkgrd = cv2.imread("background.png", flags=0)
    #print(img)
    #print(img_bkgrd)
    bkg_sub_img = pcv.image_subtract(img_bkgrd, img)
    bkg_sub_thres_img, masked_img = pcv.threshold.custom_range(rgb_img=bkg_sub_img, lower_thresh=[50], 
                                                               upper_thresh=[255], channel='gray')
    # Laplace filtering (identify edges based on 2nd derivative)

    # Inputs:
    #   gray_img - Grayscale image data 
    #   ksize - Aperture size used to calculate the second derivative filter, 
    #           specifies the size of the kernel (must be an odd integer)
    #   scale - Scaling factor applied (multiplied) to computed Laplacian values 
    #           (scale = 1 is unscaled) 
    lp_img = pcv.laplace_filter(gray_img=img, ksize=1, scale=1)
    
    # Plot histogram of grayscale values 
    pcv.visualize.histogram(gray_img=lp_img)

    # Lapacian image sharpening, this step will enhance the darkness of the edges detected
    lp_shrp_img = pcv.image_subtract(gray_img1=img, gray_img2=lp_img)

    # Plot histogram of grayscale values, this helps to determine thresholding value 
    pcv.visualize.histogram(gray_img=lp_shrp_img)
    # Sobel filtering
    # 1st derivative sobel filtering along horizontal axis, kernel = 1)

    # Inputs: 
    #   gray_img - Grayscale image data 
    #   dx - Derivative of x to analyze 
    #   dy - Derivative of y to analyze 
    #   ksize - Aperture size used to calculate 2nd derivative, specifies the size of the kernel and must be an odd integer
    # NOTE: Aperture size must be greater than the largest derivative (ksize > dx & ksize > dy) 
    sbx_img = pcv.sobel_filter(gray_img=img, dx=1, dy=0, ksize=1)

    # 1st derivative sobel filtering along vertical axis, kernel = 1)
    sby_img = pcv.sobel_filter(gray_img=img, dx=0, dy=1, ksize=1)

    # Combine the effects of both x and y filters through matrix addition
    # This will capture edges identified within each plane and emphasize edges found in both images

    # Inputs:
    #   gray_img1 - Grayscale image data to be added to gray_img2
    #   gray_img2 - Grayscale image data to be added to gray_img1
    sb_img = pcv.image_add(gray_img1=sbx_img, gray_img2=sby_img)
    
    # Use a lowpass (blurring) filter to smooth sobel image

    # Inputs:
    #   gray_img - Grayscale image data 
    #   ksize - Kernel size (integer or tuple), (ksize, ksize) box if integer input,
    #           (n, m) box if tuple input 
    mblur_img = pcv.median_blur(gray_img=sb_img, ksize=1)

    # Inputs:
    #   gray_img - Grayscale image data 
    mblur_invert_img = pcv.invert(gray_img=mblur_img)

    # combine the smoothed sobel image with the laplacian sharpened image
    # combines the best features of both methods as described in "Digital Image Processing" by Gonzalez and Woods pg. 169
    edge_shrp_img = pcv.image_add(gray_img1=mblur_invert_img, gray_img2=lp_shrp_img)

    # Perform thresholding to generate a binary image
    tr_es_img = pcv.threshold.binary(gray_img=edge_shrp_img, threshold=145, 
                                     max_value=255, object_type='dark')

    # Do erosion with a 3x3 kernel (ksize=3)

    # Inputs:
    #   gray_img - Grayscale (usually binary) image data 
    #   ksize - The size used to build a ksize x ksize 
    #            matrix using np.ones. Must be greater than 1 to have an effect 
    #   i - An integer for the number of iterations 
    e1_img = pcv.erode(gray_img=tr_es_img, ksize=3, i=1)
    # Bring the two object identification approaches together.
    # Using a logical OR combine object identified by background subtraction and the object identified by derivative filter.

    # Inputs: 
    #   bin_img1 - Binary image data to be compared in bin_img2
    #   bin_img2 - Binary image data to be compared in bin_img1
    comb_img = pcv.logical_or(bin_img1=e1_img, bin_img2=bkg_sub_thres_img)

    # Get masked image, Essentially identify pixels corresponding to plant and keep those.

    # Inputs: 
    #   rgb_img - RGB image data 
    #   mask - Binary mask image data 
    #   mask_color - 'black' or 'white'
    masked_erd = pcv.apply_mask(rgb_img=img, mask=comb_img, mask_color='black')
    
    # Need to remove the edges of the image, we did that by generating a set of rectangles to mask the edges
    # img is (1280 X 960)
    # mask for the bottom of the image

    # Inputs:
    #   img - RGB or grayscale image data 
    #   p1 - Point at the top left corner of the rectangle (tuple)
    #   p2 - Point at the bottom right corner of the rectangle (tuple) 
    #   color 'black' (default), 'gray', or 'white'
    #
    masked1, box1_img, rect_contour1, hierarchy1 = pcv.rectangle_mask(img=img, p1=(500,875), 
                                                                      p2=(720,960))
    # mask the edges
    masked2, box2_img, rect_contour2, hierarchy2 = pcv.rectangle_mask(img=img, p1=(1,1), 
                                                                      p2=(1279,959))
    bx12_img = pcv.logical_or(bin_img1=box1_img, bin_img2=box2_img)
    inv_bx1234_img = bx12_img # we dont invert
    inv_bx1234_img = bx12_img
    #inv_bx1234_img = pcv.invert(gray_img=bx12_img)

    edge_masked_img = pcv.apply_mask(rgb_img=masked_erd, mask=inv_bx1234_img, 
                                     mask_color='black')
    print("here we create a mask")
    mask, masked = pcv.threshold.custom_range(rgb_img=edge_masked_img, lower_thresh=[25], upper_thresh=[175], channel='gray')
    masked = pcv.apply_mask(rgb_img=masked, mask = mask, mask_color = 'white')
    print("end")
    # Identify objects

    # Inputs:
    #   img - RGB or grayscale image data for plotting
    #   mask - Binary mask used for detecting contours
    id_objects,obj_hierarchy = pcv.find_objects(img=edge_masked_img, mask=mask)

    # Define ROI

    # Inputs: 
    #   img - RGB or grayscale image to plot the ROI on 
    #   x - The x-coordinate of the upper left corner of the rectangle 
    #   y - The y-coordinate of the upper left corner of the rectangle 
    #   h - The height of the rectangle 
    #   w - The width of the rectangle 
    roi1, roi_hierarchy= pcv.roi.rectangle(img=edge_masked_img, x=100, y=100, h=800, w=1000)

    # Decide which objects to keep

    # Inputs:
    #    img            = img to display kept objects
    #    roi_contour    = contour of roi, output from any ROI function
    #    roi_hierarchy  = contour of roi, output from any ROI function
    #    object_contour = contours of objects, output from pcv.find_objects function
    #    obj_hierarchy  = hierarchy of objects, output from pcv.find_objects function
    #    roi_type       = 'partial' (default, for partially inside), 'cutto', or 
    #    'largest' (keep only largest contour)
    with HiddenPrints():
        roi_objects, hierarchy5, kept_mask, obj_area = pcv.roi_objects(img=edge_masked_img, 
                                                                       roi_contour=roi1, 
                                                                       roi_hierarchy=roi_hierarchy, 
                                                                       object_contour=id_objects, 
                                                                       obj_hierarchy=obj_hierarchy, 
                                                                       roi_type='largest')
    
    rgb_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # Inputs:
    #   img - RGB or grayscale image data for plotting 
    #   contours - Contour list 
    #   hierarchy - Contour hierarchy array 
    o, m = pcv.object_composition(img=rgb_img, contours=roi_objects, hierarchy=hierarchy5)
    
### Analysis ###

    outfile=False
    if args.writeimg==True:
        outfile=args.outdir+"/"+filename

    # Perform signal analysis
    
    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj- Single or grouped contour object
    #   mask - Binary image mask to use as mask for moments analysis     
    shape_img = pcv.analyze_object(img=img, obj=o, mask=mask)
    new_im = Image.fromarray(shape_img)
    new_im.save("output//" + args.filename + "shape_img_side.png")

    
    # Inputs: 
    #   gray_img - 8 or 16-bit grayscale image data 
    #   mask - Binary mask made from selected contours 
    #   bins - Number of classes to divide the spectrum into 
    #   histplot - If True, plots the histogram of intensity values 
    nir_hist = pcv.analyze_nir_intensity(gray_img=img, mask=kept_mask, 
                                         bins=256, histplot=True)

    # Pseudocolor the grayscale image to a colormap

    # Inputs:
    #     gray_img - Grayscale image data
    #     obj - Single or grouped contour object (optional), if provided the pseudocolored image gets cropped down to the region of interest.
    #     mask - Binary mask (optional) 
    #     background - Background color/type. Options are "image" (gray_img), "white", or "black". A mask must be supplied.
    #     cmap - Colormap
    #     min_value - Minimum value for range of interest
    #     max_value - Maximum value for range of interest
    #     dpi - Dots per inch for image if printed out (optional, if dpi=None then the default is set to 100 dpi).
    #     axes - If False then the title, x-axis, and y-axis won't be displayed (default axes=True).
    #     colorbar - If False then the colorbar won't be displayed (default colorbar=True)
    pseudocolored_img = pcv.visualize.pseudocolor(gray_img=img, mask=kept_mask, cmap='viridis')

    # Perform shape analysis

    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj- Single or grouped contour object
    #   mask - Binary image mask to use as mask for moments analysis 
    shape_imgs = pcv.analyze_object(img=rgb_img, obj=o, mask=m)

    # Write shape and nir data to results file
    pcv.print_results(filename=args.result)

#______________________________________________________________________________________________________________________________#


# Calling functions
wd = os.getcwd()
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
    #main()
    print(file_counter)
    file_counter += 1
    
file_counter = 0
for item in side_files:
    args.image = item
    background = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\side_perspective\\background.png"
    args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\output\\"
    args.writeimg = True
    args.result = "output//" + side_files_names[file_counter][0:-4] + "side_results.txt"
    args.filename = side_files_names[file_counter][0:-4]
    main_side()
    print(file_counter)
    file_counter += 1



