# app/routes/api/image_viewer.py
import io
import base64

from flask import Blueprint, make_response, abort, send_file
from app import limiter
from app.models.file_object import FileObject

image_bp = Blueprint('image', __name__)

# Map the base64 prefix to the MIME type
BASE64_PREFIX_MAP = {
    'data:image/png;base64,': 'image/png',
    'data:image/jpeg;base64,': 'image/jpeg',
    'data:image/jpg;base64,': 'image/jpeg',
    'data:image/webp;base64,': 'image/webp',
    'data:image/gif;base64,': 'image/gif',
    'data:video/mp4;base64,': 'video/mp4'
}

@image_bp.route('/media/<objectID>', methods=['GET'])
@limiter.limit("500 per minute")
def view_image(objectID):
    # TODO: Add redis caching for frequently accessed images
    file_object = FileObject.objects(id=objectID).first()

    if not file_object or not file_object.isUploaded:
        abort(404, description="Image not found or not uploaded.")

    base64_data = file_object.base64

    # Check the base64 prefix to determine the MIME type
    mimetype = None
    base64_image_cleaned = None
    for prefix, mime in BASE64_PREFIX_MAP.items():
        if base64_data.startswith(prefix):
            base64_image_cleaned = base64_data[len(prefix):]
            mimetype = mime
            break

    if not mimetype:
        abort(400, description="Unsupported media type")

    try:
        image_data = base64.b64decode(base64_image_cleaned)
    except base64.binascii.Error:
        abort(400, description="Invalid base64 encoding")

    # Prepare the image data as a BytesIO object
    image_io = io.BytesIO(image_data)

    response = make_response(send_file(image_io, mimetype=mimetype, as_attachment=False, download_name=file_object.name))
    response.headers['Cache-Control'] = 'public, max-age=604800'

    return response
