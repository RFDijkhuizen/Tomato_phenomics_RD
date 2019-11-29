"This workflow takes the 3d data and uses it as a mask"
from PIL import Image, ImageDraw
from plantcv import plantcv as pcv
import glob
import os
import re

# Parameters
height = 200    # The boundary a plant should always fit in
width = 200     # The boundary a plant should always fit in
pattern = ".*- (\d+)_\d_3D.csv"     # Pattern to get your genotype from filename
replacement = "\g<1>"               # Replacement regex to get your genotype

class args:
    image = ""
    outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\output"
    debug = "None"
    result = ""
    filename = ""

def silhouette_top():
    "First we draw the picture from the 3D data"
    ########################################################################################################################################################################
    x = []
    y = []
    z = []
    image_top = Image.new("RGB", (width, height), color = 'white')
    draw = ImageDraw.Draw(image_top)
    data_3d = open(args.image, "r")
    orignal_file = args.image
    for line in data_3d:
        line = line.split(",")
        y.append(int(line[0]))
        x.append(int(line[1]))
        z.append(int(line[2]))
        
    i = 0
    for point_x in x:
        point_y = y[i]
        draw.rectangle([point_x, point_y, point_x + 1, point_y + 1], fill = "black")
        #rectange takes input [x0, y0, x1, y1]
        i += 1
    image_top.save("top_temp.png")
    
    image_side = Image.new("RGB", (1280, 960), color = 'white')
    draw = ImageDraw.Draw(image_side)
    i = 0
    for point_y in y:
        point_z = z[i]
        draw.rectangle([point_z, point_y, point_z + 1, point_y + 1], fill = "black")
        #rectange takes input [x0, y0, x1, y1]
        i += 1
    image_side.save("side_temp.png")
    ########################################################################################################################################################################
    
    args.image = "top_temp.png"
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
        
    # Shape properties relative to user boundary line (optional)
    boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)
    new_im = Image.fromarray(boundary_img1)
    new_im.save("output//" + args.filename + "_top_boundary.png")

    # Find shape properties, output shape image (optional)
    shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
    new_im = Image.fromarray(shape_img)
    new_im.save("output//" + args.filename + "_top_shape.png")
    
    new_im.save("output//" + args.filename + "shape_img.png")
    GT = re.sub(pattern, replacement, files_names[file_counter])
    pcv.outputs.add_observation(variable = "genotype", trait = "genotype",
                                method = "Regexed from the filename", scale = None,
                                datatype = str, value = int(GT), label = "GT")
    
    # Write shape and color data to results file
    pcv.print_results(filename=args.result)
    ##########################################################################################################################################

    args.image = "side_temp.png"
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
        
    # Shape properties relative to user boundary line (optional)
    boundary_img1 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, line_position=1680)
    new_im = Image.fromarray(boundary_img1)
    new_im.save("output//" + args.filename + "_side_boundary.png")

    # Find shape properties, output shape image (optional)
    shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
    new_im = Image.fromarray(shape_img)
    new_im.save("output//" + args.filename + "_side_shape.png")
    
    GT = re.sub(pattern, replacement, files_names[file_counter])
    pcv.outputs.add_observation(variable = "genotype", trait = "genotype",
                                method = "Regexed from the filename", scale = None,
                                datatype = str, value = int(GT), label = "GT")
    
    # Write shape and color data to results file
    pcv.print_results(filename=args.result_side)

       
do_subset = False
if do_subset == True:
    wd = os.getcwd()
    top_files = []          # absolute paths uses for processing
    top_files_names = []    # The names used for storing 
    temp = glob.glob("subset//*3D.csv")
    for item in temp:
        print(item)
        top_files_names.append(os.path.basename(item))
        top_files.append(os.path.join(wd, item))
 
    file_counter = 0
    for item in top_files:
        args.image = item
        args.debug = "plot"
        args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\subset\\"
        args.result = "subset//" + top_files_names[file_counter][0:-4] + "silhouette_results.txt"
        args.filename = top_files_names[file_counter][0:-4]
        silhouette_top()
        file_counter += 1
        print("handled top picture %i of %i" %(file_counter, len(top_files)))
  
    
do_all = True
if do_all == True:      
    wd = os.getcwd()
    args.debug = "None"
    files = []          # absolute paths uses for processing
    files_names = []    # The names used for storing 
    temp = glob.glob("top_input//*3D.csv")
    for item in temp:
        files_names.append(os.path.basename(item))
        files.append(os.path.join(wd, item))

        
    file_counter = 0
    for item in files:
        args.image = item
        args.outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\output\\"
        args.result = "output//" + files_names[file_counter][0:-4] + "_top_results.txt"
        args.result_side = "output//" + files_names[file_counter][0:-4] + "_side_results.txt"
        args.filename = files_names[file_counter][0:-4]
        silhouette_top()
        file_counter += 1
        print("handled dataset %i of %i" %(file_counter, len(files)))
