"This workflow takes the 3d data and uses it as a mask"
import PIL
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

def workflow_3D():
    "First we draw the picture from the 3D data"
    ########################################################################################################################################################################
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
        draw.rectangle([point_x, point_y, point_x + 1, point_y + 1], fill = "black")
        #rectange takes input [x0, y0, x1, y1]
        i += 1
    image_top.save("output//" + args.filename + "top_3D.png")
    
    image_side = Image.new("RGB", (width, height), color = 'white')
    draw = ImageDraw.Draw(image_side)
    i = 0
    for point_y in y:
        point_z = z[i]
        draw.rectangle([point_z, point_y, point_z + 1, point_y + 1], fill = "black")
        #rectange takes input [x0, y0, x1, y1]
        i += 1
    image_side = image_side.rotate(90)
    image_side.save("output//" + args.filename + "side_3D.png")
    ########################################################################################################################################################################
    
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
    
    #We now have the morphology, next step is to use the 3D model as a mask on the RGB image to get colors
    ##########################################################################################################################################
    #mask = Image.open("output//" + args.filename + "top_mask.png")
    #mask = mask.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    #mask = mask.transform(size = (1280,960), method = PIL.Image.AFFINE) # An affine transformation to larger mask
    #mask = mask.resize(size = (1280, 960))
    #mask.save("output//" + args.filename + "top_final_mask.png")

    
    
    
    
    
    # Now for the side
    ##########################################################################################################################################

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

    #We now have the morphology, next step is to use the 3D model as a mask on the RGB image to get colors
    ##########################################################################################################################################
    
   
    
    
    
    

  
    
do_all = True
if do_all == True:      
    wd = os.getcwd()
    args.debug = "plot"
    files = []          # absolute paths uses for processing
    files_names = []    # The names used for storing 
    temp = glob.glob("input//*3D.csv")
    for item in temp:
        files_names.append(os.path.basename(item))
        files.append(os.path.join(wd, item))
    top_files = []          # absolute paths uses for processing
    top_files_names = []    # The names used for storing 
    temp = glob.glob("input//*cam9.png")
    for item in temp:
        top_files_names.append(os.path.basename(item))
        top_files.append(os.path.join(wd, item))

        
    file_counter = 0
    for item in files[0:1]:
        args.image = item
        args.outdir = "/output/"
        args.result = "output//" + files_names[file_counter][0:-4] + "_top_results.txt"
        args.result_side = "output//" + files_names[file_counter][0:-4] + "_side_results.txt"
        args.filename = files_names[file_counter][0:-4]
        workflow_3D()
        
        
        
        file_counter += 1
        print("handled dataset %i of %i" %(file_counter, len(files)))
