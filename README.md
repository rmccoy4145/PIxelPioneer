# PixelPioneer
#### Video Demo:  https://youtu.be/hz7Rr8NoKF8
#### Description:
PixelPioneer is an image proccessing platform that allows you to upload images to your account
and apply processing to the images. An account is required to use PixelPioneer, users are only able
to access the images that they have uploaded. Images are processed using the stored images, the
processed image is sent back to the user, the stored image state is not altered.


Additional image processing features coming soon...

## System Requirements
Python3.12
sqlite3

## Running the application

install dependencies:
```
pip install -r requirements.txt
```

execute the following command to start the application:
```
flash run
```

Test Account Credentials:
username: ryan
password: password

## Project Overview

/data                           -- main application data folder
/data/pixelpioneer.db           -- sqlite3 database for the application
/data/images/                   -- image upload folder
/flask_session/                 -- flask session file directory
/static/                        -- includes files such as images, & css used within the html pages
/templates/                     -- includes all Jinja2 templates
/templates/images.html          -- template for viewing and processing images on a account
/templates/index.html           -- template for dashboard for the webapp
/templates/login.html           -- template for login screen
/templates/layout.html          -- main layout that each template extends
/templates/register.html        -- template for registeration screen
/templates/upload_image.html    -- template for upload image screen
/app.py                         -- main application entry
/auth_decorators.py             -- contains flask authentication decorators
/datasource.py                  -- entry point for a SQL connection
/image_service.py               -- contains image proccesing operations using Pillow framework
/user_service.py                -- contains operations around user management (login, register, etc)
/requirements.txt               -- list required dependencies

## API: /app.py

Modulle app.py is the main entry point for the Flask application and it contains all the routes. Most of the
routes within the application are protected with a session, if the session does not exists the user is redirected
to the login page. This module only contains logic pertaining to the http request, all operations are passed
to services which throw exceptions on failures.

#### Routes
/                               -- dashboard route [redirect to login if not logged in]
/login                          -- login user route
/register                       -- register new user route
/uploadImage                    -- upload new image route [login required]
/processImage                   -- processes an image by filename [login required]
/removeImage                    -- remove image [login required]
/images                         -- view images on account [login required]
/logout                         -- kills session logs users out [login required]

## Overview: /image_service.py

Module image_service.py contains all the image handling logic, Pillow is used to perform all the
image processing. It handles saving uploaded images to disk, and maintaining the `images` table
within the database which keeps state of which accounts own which images. It's also responsible
for making sure each account cannot access images on other accounts. The `apply_image_process()`
method is where the image processing is performed, the `type` argument determines which type of
processing is performed on the image. This module also generates the urls needed to access the images
from the webapp since they are not in the static folder, images are stored in the `/data/images` directory
but are served via the `/images/<filename>` route. Storing only the filename in the database
made this simple to implement.

### Overview: /templates/images.html

This Jinja2 template contains a consiterate amount of functionality that is worth mentioning. The Jinja
template populate the image carousel with images from the user account, along with an interface for
applying the image processing to each image. The interface contains a selector input for the filter type,
a hidden input for the image filename, a 'Apply' and 'X' button. The 'Apply' button executes a javascript function
`handleSubmit()`, inwhich passes itself to the function, formdata is parsed then passed to a fetch call to the
`processImage` route. On, failure a toast message will appear on the bottom right. On, success, new image data
is retreived then passed to a new window, displaying the processed image. The javascript function also controls
the spinners for the buttons to indicate to the user that the application is processing something. Bigger images
take longer to process. The 'X' button, perform a similar but much simplier operation, passing the form data to the
`/removeImage` route.


### Design Choices, Issues, & Thoughts

My inital idea for the application was going to be a single page image processing webapp, I believe this would of
been fine but I wanted to create something a bit more complicated that I could potientally keep adding to if I
saw fit. Every major webapp implements accounts with authentication and data access contols, this pushed me to
add those features in.

The application started out in a single app.py but once it grew it got compliated to maintain, so I decided to
push anything the had to interface with the database into a service module. This allowed each module to be
alot leaner making it easier for me to maintain. Once that was done, there were multiple calls to get the SQL connection
in multiple files, so I ended up moving that to a single module then using the module to get the connection.

As the application grew I found that I had blocks of duplicate code so I decided to consildate those blocks into helper
methods, this is apparent within the image processing module.

At first I had setup the image upload to store to the static directory because serving them on via a url was simple. Eventually,
I realized this was not a good idea since it would allow anyone with that url to be able to access the image no matter if they were
authenticated to the application. So, I decided to create a data directory and upload them there, then add a route for serving
the images that required login.

I got stumped using the Pillow framework for a while, I ran across an issue where filters where not being applied to none of my images.
I ran through a bunch of debugging, reading forms, and I noticed no one was having this issue I was having which usually points to user
error. I was following the documents on Pillows site but was still having issues. Eventually, I spun up the Python interpreter and starting
playing around the Pillow to see if I could make something happen, and after a couple of tries I was able to figure out that when I was applying
the filter to the image it was returns that new image but I was not saving it in a variable, smh.

### Nice to haves

- better web interface for appling filters to images
- a way to apply multiple filters to an image
- additional image processing
- better forum validation username/password requirements
- image sharing
- account managemant

