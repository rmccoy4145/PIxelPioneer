from PIL import Image, ImageFilter
import io
import uuid
import os
import datasource
from functools import reduce

UPLOAD_FOLDER = 'data/images'
IMAGE_SERVE_ROUTE = 'image'

def apply_image_process(image_path, user_id, type):
    filename = image_path.rsplit('/', 1)[1]
    # Here we check to make sure a user is not trying to access an image not under their accoount
    image_query = datasource.DB.execute("SELECT * FROM images WHERE user_id = ? AND filename = ?", user_id, filename)

    if len(image_query) != 1:
        raise RunTimeError("Cannot alter image")

    img_io = None
    try:
        with Image.open(os.path.join(UPLOAD_FOLDER, filename)) as img:
            img.load()
            type = type.upper()
            proccessed_image = None

            if type == 'BLUR':
                    proccessed_image = img.filter(ImageFilter.BLUR)
            elif type == 'GRAYSCALE':
                    proccessed_image = img.convert('L')
            elif type == 'SMOOTH':
                    proccessed_image = img.filter(ImageFilter.SMOOTH)
            else:
                raise RunTimeError("Invalid filter type")

            img_io = io.BytesIO()
            proccessed_image.save(img_io, format='PNG')
            img_io.seek(0)
    except Exception as e:
        print(f"ERROR: {e}")

    if img_io is None:
        raise RunTimeError(f"Unable to apply filter")

    return img_io

def delete_image(image_path, user_id):
    filename = image_path.rsplit('/', 1)[1]
    # Here we check to make sure a user is not trying to access an image not under their accoount
    image_query = datasource.DB.execute("SELECT * FROM images WHERE user_id = ? AND filename = ?", user_id, filename)

    if len(image_query) != 1:
        raise RunTimeError("Cannot alter image")

    datasource.DB.execute("DELETE FROM images WHERE user_id = ? AND filename = ?", user_id, filename)
    os.remove(os.path.join(UPLOAD_FOLDER, filename))



def upload_new_image(file, user_id):
    validate_image(file)
    save_image(file, user_id)

def save_image(file, user_id):

    upload_filename = f"{user_id}--{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}"
    file.seek(0)
    file.save(os.path.join(UPLOAD_FOLDER, upload_filename))

    datasource.DB.execute(
    "INSERT INTO images (user_id, filename) VALUES (?,?)",
    user_id,
    upload_filename,
    )

def get_image_serve_path(filename):
    return os.path.join(UPLOAD_FOLDER, filename)

def validate_image(file):
    if not hasattr(file, 'stream'):
        print("Error: invalid image format")
        raise RunTimeError("Error: No stream exist")

    allowed_extentions = {'png', 'jpg', 'jpeg', 'gif'}

    if '.' not in file.filename and file.filename.rsplit('.', 1)[1].lower() not in allowed_extentions:
        print("Error: invalid image format")
        raise RunTimeError("Invalid image format -- Allowed file types are png, jpg, jpeg, gif")

def get_image_paths(user_id):
    image_query = datasource.DB.execute("SELECT * FROM images WHERE user_id = ?", user_id)
    return list(map(lambda image: os.path.join(IMAGE_SERVE_ROUTE, image["filename"]), image_query))
