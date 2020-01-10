import base64
# To run this example, type the following: python facerec_from_webcam_faster.py
import face_recognition
import cv2
import numpy as np
import logging
import threading
import os
import requests

from flask import Response, Flask, render_template, url_for, request, redirect, session, json
from flask_oidc import OpenIDConnect
from werkzeug.utils import secure_filename
from oauth2client.client import OAuth2Credentials

# Debug level can be set to: DEBUG INFO WARNING ERROR CRITICAL
logger = logging.getLogger('myapp')
logger.setLevel(logging.DEBUG)
stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

# nice output format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stderr_log_handler.setFormatter(formatter)

logger.info('Starting')

# Create a lock to ensure thread-safe behaviour when updating the output
# lock = threading.Lock()

app = Flask(__name__, static_url_path = "/profiles", static_folder = "profiles")

app.config.from_object('config')
logger.debug(app.config)
logger.debug(app.config["LOGOUT_URI"])

oidc = OpenIDConnect(app)

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

@app.route("/")
def home():
    return render_template("home.html", oidc=oidc)


@app.route("/login")
def login():
    bu = oidc.client_secrets['issuer'].split('/oauth2')[0]
    cid = oidc.client_secrets['client_id']
    # userName = "marie.bashir@coolcoy.com"

    destination = 'http://localhost:8080/profile'
    state = {
        'csrf_token': session['oidc_csrf_token'],
        'destination': oidc.extra_data_serializer.dumps(destination).decode('utf-8')
    }

    return render_template("login.html", userName=userName, oidc=oidc, baseUri=bu, clientId=cid, state=base64_to_str(state))


@app.route("/register")
def register():
    return render_template("register.html", oidc=oidc)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    info = oidc.user_getinfo(["sub", "name", "email", "locale"])
    displayfilename = "/profiles/" + info['email']
    logger.debug("Target filename = %s", displayfilename)

    if request.method == "POST":

        if request.files:

            if "filesize" in request.cookies:

                if not allowed_image_filesize(request.cookies["filesize"]):
                    logger.warning("Filesize exceeded maximum limit")
                    return redirect(request.url)

                image = request.files["image"]

                if image.filename == "":
                    print("No filename")
                    return redirect(request.url)

                if allowed_image(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], info['email']))

                    logger.info("Image saved")

                    return redirect(request.url)

                else:
                    logger.warning("That file extension is not allowed")
                    return redirect(request.url)

    return render_template("profile.html", profile=info, oidc=oidc, targetfilename=displayfilename)

@app.route("/snapme")
def snapme():
    imageProfiles = []
    known_face_encodings = []
    known_face_names = []

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    name=''

    for file in os.listdir(app.config["IMAGE_UPLOADS"]):
        if "@" in file:
            logger.debug("Encoding image = %s", file)
            thisImage = face_recognition.load_image_file( os.path.join(app.config["IMAGE_UPLOADS"], file ))
            thisknown_face_encoding = face_recognition.face_encodings( thisImage )[0]
            known_face_encodings.append( thisknown_face_encoding )
            known_face_names.append( file )

    logger.info('Done image loading')

    logger.debug("Number of known_face_encodings = %s", len(known_face_encodings))
    logger.debug("Number of known_face_names = %s", len(known_face_names))
    logger.debug("     known_face_encodings = %s", known_face_encodings)
    logger.debug("     known_face_names = %s", known_face_names)

    if known_face_names:
        # This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
        # other example, but it includes some basic performance tweaks to make things run a lot faster:
        #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
        #   2. Only detect faces in every other frame of video.

        # PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
        # OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
        # specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

        # Get a reference to webcam #0 (the default one)
        logger.info('Initialising VideoCapture')
        video_capture = cv2.VideoCapture(0)
        logger.info('VideoCapture initialised')

        logger.info('Starting image loading')

        logger.debug('Starting Video capture')
        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                logger.debug('Process faces')
                face_names = []

                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    logger.debug('Number of face_distances = %s', len(face_distances))
                    best_match_index = np.argmin(face_distances)
                    logger.debug('best_match_index = %s', best_match_index)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    logger.info('name = %s', name)

                    face_names.append(name)

            process_this_frame = not process_this_frame

            # Stop video capture as soon as you find a face
            if name:
                break

        logger.info('face_names = %s', face_names)
        logger.info('name = %s', name)

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
    else:
        name = "Unknown"

    logger.debug('Setup login page')

#    return render_template("home.html", oidc=oidc)
# Render the login page
    bu = oidc.client_secrets['issuer'].split('/oauth2')[0]
    cid = oidc.client_secrets['client_id']
    if name != "Unknown":
        userName = name
        logger.debug('userName = %s', userName)
    else:
        userName = ""

    destination = 'http://localhost:8080/profile'
    state = {
        'csrf_token': session['oidc_csrf_token'],
        'destination': oidc.extra_data_serializer.dumps(destination).decode('utf-8')
    }

    logger.debug('Render login page')

    return render_template("login.html", userName=userName, oidc=oidc, baseUri=bu, clientId=cid, state=base64_to_str(state))

@app.route("/logout", methods=["POST"])
def logout():
    info = oidc.user_getinfo(["sub", "name", "email"])
    id_token = OAuth2Credentials.from_json(oidc.credentials_store[info.get("sub")]).token_response["id_token"]
    logger.debug("*** id_token = %s", id_token)
    logger.debug("LOGOUT_URI = %s", app.config['LOGOUT_URI'])

    # logoutRequest = "https://dev-640409.okta.com/oauth2/default/v1/logout?id_token_hint=" + id_token + "&post_logout_redirect_uri=http://localhost:8080/oidcLogout"
    logoutRequest = app.config['LOGOUT_URI'] + "?id_token_hint=" + id_token + "&post_logout_redirect_uri=http://localhost:8080/oidcLogout"
    logger.debug("logoutRequest = %s", logoutRequest)

    logger.warning("*** REDIRECTING HOME ****")

    # return redirect(url_for("oidcLogout"))
    return redirect(logoutRequest)


@app.route("/oidcLogout", methods=["GET", "POST"])
def oidcLogout():

    logger.debug("Terminate local session")
    oidc.logout()

    logger.debug("Go home")

    return redirect(url_for("home"))

def base64_to_str(data):
    return str(base64.b64encode(json.dumps(data).encode('utf-8')), 'utf-8')


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)
