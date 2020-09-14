from PIL import Image
from packages import mail
from flask_mail import Message
from flask import url_for, current_app
import urllib.request as url
import os
import secrets

def send_reset_email(user):
    """Send a reset email to the user"""
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
    sender='norely@ca$hTrack.com', recipients=[user.email])
    msg.body=f'''To reset your password, please visit the following link: {url_for('users.reset_password', token=token, _external=True)}
Please ignore this email if you did not make a request. 
This is automated Message sent from Ca$hTrack.
    '''
    mail.send(msg)

def save_picture(form_picture):
    """Save an uploaded picture into the database"""
    # Generate a random string for its name  
    file_hex = secrets.token_hex(16)

    # Extract the file extension of the file uploaded
    _, file_ext = os.path.splitext(form_picture.filename)

    # Create a name and path for new image file
    file_name = file_hex + file_ext
    file_path = os.path.join(current_app.root_path, 'static/profile_pics/' + file_name)
    
    # Resize our image to fit the thumbnail 
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)

    # Convert image to rgb support
    if file_ext == '.jpg' or 'jpeg':
        image = image.convert('RGB')

    # Save and return image file name
    image.save(file_path)
    return file_name