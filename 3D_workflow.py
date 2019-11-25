"This workflow takes the 3d data and uses it as a mask"
from PIL import Image, ImageDraw
from plantcv import plantcv as pcv

height = 500    # The boundary a plant should always fit in
width = 500     # The boundary a plant should always fit in

x = []
y = []
z = []
image_top = Image.new("RGB", (width, height), color = 'white')
draw = ImageDraw.Draw(image_top)
data_3d = open("C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_perspective\\0224_2018-03-07 08.55 - 26_0_3D.csv", "r")

for line in data_3d:
    line = line.split(",")
    x.append(int(line[0]))
    y.append(int(line[1]))
    z.append(int(line[2]))
    
i = 0
for point_x in x:
    point_y = y[i]
    draw.rectangle([point_x, point_y, point_x + 1, point_y + 1], fill = "black")
    #rectange takes input [x0, y0, x1, y1]
    i += 1
image_top.save("top_test.png")

image_side = Image.new("RGB", (1280, 960), color = 'white')
draw = ImageDraw.Draw(image_side)
i = 0
for point_y in y:
    point_z = z[i]
    draw.rectangle([point_z, point_y, point_z + 1, point_y + 1], fill = "black")
    #rectange takes input [x0, y0, x1, y1]
    i += 1
image_side.save("side_test.png")

def silhouette_top():
    
    class args:
            image = image = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project\\top_test.png"
            outdir = "C:\\Users\\RensD\\OneDrive\\studie\\Master\\The_big_project"
            debug = "plot"
            result = "results.txt"
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

    # Find shape properties, output shape image (optional)
    shape_img = pcv.analyze_object(img=img, obj=obj, mask=mask)
        
    # Write shape and color data to results file
    pcv.print_results(filename=args.result)
        
        
silhouette_top()
