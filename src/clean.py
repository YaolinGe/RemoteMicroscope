import os 

def clean(): 
    if os.path.exists('captured_image.jpg'):
        os.remove('captured_image.jpg')
        print('File removed')