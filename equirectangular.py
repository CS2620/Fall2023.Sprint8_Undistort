from PIL import Image
import os
import sys
import math


size = 200
image = Image.open("./panoramic.jpg")
newImage = Image.new("RGB", (size * 4, size * 3))

width = image.width
height = image.height

new_width = newImage.width
new_height = newImage.height


originalPixelBuffer = image.load()
newPixelBuffer = newImage.load()


# Take a percentage, turn it into a pixel value, and clip it to bounds of the image
def clip(x,y):
    maxed_x = max(0, min(width-1, x*width))
    maxed_y = max(0, min(height-1, y*height))
    return [maxed_x, maxed_y]

# Given a 3D vector for the top square, sample the original image
def sample(v):
    # Find the 'longitude' of the vector
    atan_result = math.atan2(v[1], v[0])
    atan_added = atan_result + math.pi
    px = atan_added/(math.pi*2)

    #Find the 'latitude' of the vector
    length = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    normalized = (v[0]/length, v[1]/length, v[2]/length)
    
    second_angle = math.atan2(v[2], math.sqrt(normalized[0]**2+normalized[1]**2))
    second_angle_b = second_angle / (math.pi/2)
    py = abs(second_angle_b)

    # Get the clipped value
    [maxed_x, maxed_y] = clip(px, py)

    #Return the actual color
    return originalPixelBuffer[maxed_x, height - maxed_y]

def sample_bottom(v):
    length = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    normalized = (v[0]/length, v[1]/length, v[2]/length)
    atan_result = math.atan2(v[1], v[0])
    atan_added = atan_result + math.pi
    px = atan_added/(math.pi*2)

    second_half = math.sqrt(normalized[0]**2+normalized[1]**2)
    second_angle = math.atan2(v[2], second_half)
    second_angle_b = second_angle / (math.pi/2)
    py = math.fabs(second_angle_b)

    [maxed_x, maxed_y] = clip(px, py)
    return originalPixelBuffer[maxed_x, maxed_y]

def sample_front(v):
    atan_result = math.atan2(1, v[0])
    atan_added = atan_result + math.pi
    base_angle = atan_added/(math.pi*2)

    length = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    normalized = (v[0]/length, v[1]/length, v[2]/length)
    second_half = math.sqrt(normalized[0]**2+normalized[1]**2)
    second_angle = math.atan2(normalized[2], second_half)
    second_angle_b = second_angle / (math.pi/2)
    second_angle_c = (second_angle_b+.5)

    original_image_x = math.floor(base_angle * width)
    original_image_y = math.floor(second_angle_c * height)
    maxed_x = max(0, min(width-1, original_image_x))
    maxed_y = max(0, min(height-1, original_image_y))
    return originalPixelBuffer[maxed_x, maxed_y]

# Loop over every pixel in our output image
for y in range(new_height):
    for x in range(new_width):
        new_color = (0, 0, 0)

        # Top case
        if y <= new_height/3:
            if new_width/4 <= x < new_width/2:
                dx = (x - new_width/4)/(new_width/4)
                dy = y/(new_height/3)
                dx_half_percent = dx - .5
                dy_half_percent = dy - .5
                v = [dx_half_percent, dy_half_percent,1]
                new_color = sample(v)

        # Four squares in the middle (Left, Front, Right, Back)
        if new_height/3 < y <= new_height*2/3:
            if x <= new_width/4:
                new_color = (0, 255, 0)
            elif new_width/4 < x <= new_width/2:
                dx = (x - new_width/4)/(new_width/4)
                dy = (y - (new_height/3))/(new_height/3)
                dx_half_percent = dx - .5
                dy_half_percent = dy - .5
                v = [dx_half_percent, 1, dy_half_percent]
                new_color = sample_front(v)
            elif new_width/2 < x <= new_width * 3/4:
                new_color = (255, 255, 0)
            elif new_width * 3/4 < x:
                new_color = (255, 0, 255)

        # Bottom square
        if new_height * 2/3 < y:
            if new_width/4 < x <= new_width/2:
                dx = (x - new_width/4)/(new_width/4)
                dy = (y-(new_height*2/3))/(new_height/3)
                dx_half_percent = dx - .5
                dy_half_percent = dy - .5
                v = [dx_half_percent, dy_half_percent, -1]
                new_color = sample_bottom(v)
        newPixelBuffer[x, y] = new_color

newImage.save("done.jpg")
