# Facial Recognition + Python Flask + Okta Custom Login Example

This example uses facial recognition to identify who you are and fill in the Username on the Okta Sign-In Widget custom login page.  The login is achieved with the [Okta Sign In Widget][], which gives you more control to customize the login experience within your app.  After the user authenticates they are redirected back to the application with an authorization code that is then exchanged for an access token.

In this example, you need to fill in the password but this can be changed to use FIDO/WebAuthn for fingerprint authentication. To do this, you'll need an Okta Production or Preview domain rather than an Developer instance.

Built using [dlib](http://dlib.net/)'s state-of-the-art face recognition
built with deep learning. The model has an accuracy of 99.38% on the
[Labeled Faces in the Wild](http://vis-www.cs.umass.edu/lfw/) benchmark.


## Prerequisites

Before running this sample, you will need the following:

* An Okta Developer Account, you can sign up for one at https://developer.okta.com/signup/.
Instructions].  When following the wizard, use the default properties.  They are are designed to work with our sample applications.
* macOS
* Webcam - the only one tested is the built-in webcam on a Macbook Pro
* Python 3.3+

Make sure you have dlib already installed with Python bindings:

  * [How to install dlib from source on macOS or Ubuntu](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)

## Installation

To install this application, you first need to clone this repo and then enter into this directory:

```bash
git clone git@github.com:https://github.com/drazla/okta-face.git
cd okta-face
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

Then, install this module from pypi using `pip3`:

```bash
pip3 install face_recognition
```

## Configuration

Login to your Okta Developer Portal

Navigate to API -> Trusted Origins
* Click on Add Origin
* Name: My Portal
* Origin URL: http://localhost:8080/
* CORS: Checked
* Redirect: Checked
* Click on Save

Navigate to Users -> Groups and add a group called Portal
Click on the Portal group -> Apps tab
Assign My Portal application to the Portal group

Navigate to Users -> Registration and enable self service Registration
* Click on checkbox for Add to Sign-in Widget
* Assign to group: Portal
* Default redirect: http://localhost:8080/

Create an Okta Application, configured for Web mode. This is done from the Okta Developer Console and you can find instructions [here][OIDC WEB Setup

You need to gather the following information from the Okta Developer Console:

- **Client ID** and **Client Secret** - These can be found on the "General" tab of the Web application that you created earlier in the Okta Developer Console.
- **Issuer** - This is the URL of the authorization server that will perform authentication.  All Developer Accounts have a "default" authorization server.  The issuer is a combination of your Org URL (found in the upper right of the console home page) and `/oauth2/default`. For example, `https://dev-1234.oktapreview.com/oauth2/default`.

Now that you have the information needed from your organization, open the `okta-hosted-login` directory. Copy the [`client_secrets.json.dist`](client_secrets.json.dist) to `client_secrets.json` and fill in the information you gathered.

```json
{
  "web": {
    "auth_uri": "https://{yourOktaDomain}/oauth2/default/v1/authorize",
    "client_id": "{clientId}",
    "client_secret": "{clientSecret}",
    "redirect_uris": [
      "http://localhost:8080/authorization-code/callback"
    ],
    "issuer": "https://{yourOktaDomain}/oauth2/default",
    "token_uri": "https://{yourOktaDomain}/oauth2/default/v1/token",
    "token_introspection_uri": "https://{yourOktaDomain}/oauth2/default/v1/introspect",
    "userinfo_uri": "https://{yourOktaDomain}/oauth2/default/v1/userinfo"
  }
}
```

## Running the application

Start the app server:

```
python main.py
```

Navigate to http://localhost:8080 in your browser.

Click the **Log in** button and webcam will activate and wait until a face is detected. When a face is detected you will be redirected to the Okta Widget custom sign-in page.

You can login with the same account that you created when signing up for your Developer Org, or you can use a known username and password from your Okta Directory.

[Okta Sign In Widget]: https://github.com/okta/okta-signin-widget
[OIDC WEB Setup Instructions]: https://developer.okta.com/authentication-guide/implementing-authentication/auth-code#1-setting-up-your-application
