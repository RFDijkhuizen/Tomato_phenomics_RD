"This workflow takes the 3d data and uses it as a mask"
from PIL import Image, ImageDraw


x = []
y = []
z = []
image_top = Image.new("RGB", (1280, 960), color = 'white')
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
