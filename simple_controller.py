"""camera_pid controller."""

from controller import Display, Keyboard, Robot, Camera
from vehicle import Car, Driver
import numpy as np
import cv2
from datetime import datetime
import os
import csv
from PIL import Image
#Getting image from camera
def get_image(camera):
    raw_image = camera.getImage()  
    image = np.frombuffer(raw_image, np.uint8).reshape(
        (camera.getHeight(), camera.getWidth(), 4)
    )
    print(image.shape)
    return image

#Image processing
def greyscale_cv2(image):
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_img

#Display image 
def display_image(display, image):
    # Image to display
    image_rgb = np.dstack((image, image,image,))
    # Display image
    image_ref = display.imageNew(
        image_rgb.tobytes(),
        Display.RGB,
        width=image_rgb.shape[1],
        height=image_rgb.shape[0],
    )
    display.imagePaste(image_ref, 0, 0, False)

#initial angle and speed 
manual_steering = 0
steering_angle = 0
angle = 0.0
speed = 30
wheel_angle=0
# set target speed
def set_speed(kmh):
    global speed            #robot.step(50)
#update steering angle
def set_steering_angle(wheel_angle):
    global angle, steering_angle
    # Check limits of steering
    if (wheel_angle - steering_angle) > 0.1:
        wheel_angle = steering_angle + 0.1
    if (wheel_angle - steering_angle) < -0.1:
        wheel_angle = steering_angle - 0.1
    steering_angle = wheel_angle
  
    # limit range of the steering angle
    if wheel_angle > 0.5:
        wheel_angle = 0.5
    elif wheel_angle < -0.5:
        wheel_angle = -0.5
    # update steering angle
    angle = wheel_angle

#validate increment of steering angle
def change_steer_angle(inc):
    global manual_steering
    # Apply increment
    new_manual_steering = manual_steering + inc
    # Validate interval 
    if new_manual_steering <= 25.0 and new_manual_steering >= -25.0: 
        manual_steering = new_manual_steering
        set_steering_angle(manual_steering * 0.01)
    # Debugging
    if manual_steering == 0:    
        #print("going straight")
        pass
    else:
        turn = "left" if steering_angle < 0 else "right"

# main
def main():
    # Create the Robot instance.
    robot = Car()
    driver = Driver()

    # Get the time step of the current world.
    timestep = int(robot.getBasicTimeStep())

    # Create camera instance
    camera = robot.getDevice("camera")
    camera.enable(timestep)  # timestep

    # processing display
    #display_img = Display("display_image")

    #create keyboard instance
    keyboard=Keyboard()
    keyboard.enable(timestep)
    image_save_path = os.path.join(os.getcwd(), "train_images")
    csv_file_path = os.path.join(os.getcwd(), "image_data.csv")
    last_file_name = ''

    # Create the CSV file and write the header if it doesn't exist
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Image Name", "Angle"])

    while robot.step() != -1:
        
        # Get image from camera
        image = get_image(camera)

        # # Process and display image 
        # grey_image = greyscale_cv2(image)
        # display_image(display_img, grey_image)
        # # Read keyboard
        key=keyboard.getKey()
        if key == keyboard.UP: #up
            global angle,wheel_angle
            global manual_steering
            angle = 0
            wheel_angle=0
            manual_steering=0
            print("up")
        elif key == keyboard.DOWN: #down
            set_speed(speed - 5.0)
            print("down")
        elif key == keyboard.RIGHT: #right
            change_steer_angle(+1)
            print("right")
        elif key == keyboard.LEFT: #left
            change_steer_angle(-1)
            print("left")
        elif key == ord('A'):
            #filename with timestamp and saved in current directory
            pass
        current_datetime = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f"))
        file_name = current_datetime + ".png"
        
        print("Image taken")
        print(os.getcwd() + "/" + file_name)
        print(angle)
        image_pil = Image.fromarray(image)
        image_pil.save(os.path.join(image_save_path, file_name))
        #camera.saveImage(os.path.join(image_save_path, file_name), 1)
            # Save the image name and angle to the CSV file
        if file_name != last_file_name:
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([file_name, wheel_angle])
            last_file_name = file_name
            
        
            
        #update angle and speed
        driver.setSteeringAngle(angle)
        driver.setCruisingSpeed(speed)


if __name__ == "__main__":
    main()