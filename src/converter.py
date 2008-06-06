
import Image
import mimetypes
import os, os.path

ALLOWED_FORMATS = ['image/x-ms-bmp', 'image/gif', 'image/jpeg', 'image/png', 'image/tiff']
MAX_SIZE = 1*1024*1024 #1MB
#thumbs width, height
NEW_IMAGE_SIZE = 640, 480


#return True whether typemime is allowed , else False
def check_mimetype_allowed():
    flag = False
    for fi_ in ALLOWED_FORMATS:
        if fi_ == type:
            flag = True

    if flag == True:
        return True
    else:
        return False
        
        
#return False whether file size > maxSize      
def check_max_size_allowed():
    if os.path.getsize(path+"\\"+file) > MAX_SIZE:  ## size in byte
        return False
    else:
        return True
    
# def all conditions before operate image
def check_precondition():
    
    if check_mimetype_allowed() and check_max_size_allowed():
        return True
    else:
        return False

#retrieve filname, mimetyme + path
def load_image(input_file):
    global type, file, path, im
    type, encoding = mimetypes.guess_type(input_file)
    path, file = os.path.split(input_file)
    base, ext = os.path.splitext(input_file)
    im = Image.open(input_file)
  

 
def get_aspect_ratio_src():
    ratio = float(im.size[0])/float(im.size[1])
    return ratio
      
def get_aspect_ratio_target():
    ratio = float(NEW_IMAGE_SIZE[0])/float(NEW_IMAGE_SIZE[1])
    return ratio  
  
  
def get_scaled_dimension():

    if get_aspect_ratio_target() > get_aspect_ratio_src():
        scaled_image = max(NEW_IMAGE_SIZE), int(max(NEW_IMAGE_SIZE)/get_aspect_ratio_src())
    elif get_aspect_ratio_target() < get_aspect_ratio_src():
        scaled_image = int(max(NEW_IMAGE_SIZE)*get_aspect_ratio_src()), max(NEW_IMAGE_SIZE)
    else:
        scaled_image = NEW_IMAGE_SIZE[0], NEW_IMAGE_SIZE[1]
    return scaled_image

    

       
def crop():   

  
    im.thumbnail(get_scaled_dimension()) #resizing
    if get_aspect_ratio_target() > get_aspect_ratio_src():
        box = (0, (get_scaled_dimension()[1]-NEW_IMAGE_SIZE[1])/2, NEW_IMAGE_SIZE[0], get_scaled_dimension()[1]-(get_scaled_dimension()[1]-NEW_IMAGE_SIZE[1])/2)
    elif get_aspect_ratio_target() < get_aspect_ratio_src():
        box = ((get_scaled_dimension()[0]-NEW_IMAGE_SIZE[0])/2, 0, NEW_IMAGE_SIZE[0]+(get_scaled_dimension()[0]-NEW_IMAGE_SIZE[0])/2, NEW_IMAGE_SIZE[1])
    else: #if ratio_src == ratio_dest
        box = ( 0 , 0, max(NEW_IMAGE_SIZE), min(NEW_IMAGE_SIZE))
    #print box
    im.crop(box).save(path+"\\cropped_"+file)
      
    
def convert_loadedimage_to(output_extension_format):
    if check_precondition():
        outputfile = os.path.splitext(file)[0] + output_extension_format
        try:
            Image.open(path+"\\"+file).save(path+"\\"+outputfile)
            print "conversion ok"
        except IOError:
            print "Cannot convert", file
    else:
        print "Pre-Condition Problem"
    
load_image("C:\\Documents and Settings\\Florent.ZEBULON\\workspace\\ImageUtil\\src\\converter\\SP_A0823.jpg")
#convert_loadedimage_to(".gif")
#print getScaledDimension()
#print get_scaled_dimension()
if(NEW_IMAGE_SIZE != im.size ):
    crop()
else:
    print "image src equals image dest"
    
print "termine"


