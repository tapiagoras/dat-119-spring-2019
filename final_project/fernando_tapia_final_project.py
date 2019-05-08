'''

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson

Modified by Rui Santos
Complete project details: https://randomnerdtutorials.com

Camera excerpt from https://blog.miguelgrinberg.com/post/video-streaming-with-flask

Modified by:
Fernando Tapia Tinoco
05/01/2019
Python 1 - DAT-119 - Spring 2019
    IoT LEGO Raspberry Pi
    This project use a Raspberry Pi Revision 2 which only have 26 pins

'''

import RPi.GPIO as GPIO # This will call Raspberry Pi GPIO library to control the pins
from flask import Flask, render_template, request, Response #To launch webserver Response is needed for Camera straming
import cv2
import sys
import numpy
app = Flask(__name__)
GPIO.cleanup()# This will clean the GPIO(General Purpose Input/Output) previous status in case some of the pins get stuck may not be necessary
GPIO.setmode(GPIO.BOARD) #The GPIO.BOARD option specifies that you are referring to the pins by the number of the pin.

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   11 : {'name' : 'Turn Left', 'state' : GPIO.LOW},
   13 : {'name' : 'Steering Control', 'state' : GPIO.LOW},
   15 : {'name' : 'Turn Right', 'state' : GPIO.LOW},
   16 : {'name' : 'Going Forward', 'state' : GPIO.LOW},
   18 : {'name' : 'Going Backwards', 'state' : GPIO.LOW},
   22 : {'name' : 'Speed Control', 'state' : GPIO.LOW},
   
   }

# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT) #Each pin can be used as Inpit or output this way we setup as output to send a signal from the raspberry to the breadboard that control the Lego Motor
   GPIO.output(pin, GPIO.LOW) # Low means no voltage flowing trough any pin, We need every pin output in low status.

@app.route("/")# This define that main will run the index or initial page of our web server
def main():
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }

   return render_template('main.html', **templateData)

#This is for the camera streaming. I have an issue with the streaming currently. Every time the status of the pins are reset the stream collapse and the whole input/output system just collapse I need to work with the flask documentation

def gen():
    i=1
    while i<10:
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n'+str(i)+b'\r\n')
        i+=1

def get_frame():
    camera_port=0
    ramp_frames=100
    camera=cv2.VideoCapture(camera_port) #this makes a web cam object
    i=1
    while True:
        retval, im = camera.read()
        imgencode=cv2.imencode('.jpg',im)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        i+=1
    del(camera)

@app.route('/calc')
def calc():
    return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
