from flask import (Blueprint, render_template, redirect,
                   url_for, flash, request, current_app)
from flask_login import login_required, current_user
from models.user import User
from models.favourite import Favourite
from werkzeug.utils import secure_filename
from bson import ObjectId
import os
import uuid

profile_bp = Blueprint('profile', __name__)


def allowed_file(filename):
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_profile_image(file):
    """Save and resize profile image"""
    try:
        from PIL import Image
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)

        img = Image.open(file)
        img = img.convert('RGB')
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        img.save(filepath, quality=85, optimize=True)
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        raise


@profile_bp.route('/')
@login_required
def profile():
    favourites_count = Favourite.count_user_favourites(current_user.id)
    return render_template(
        'profile.html',
        user=current_user,
        favourites_count=favourites_count,
        edit_mode=False
    )


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        bio = request.form.get('bio', '').strip()
        location = request.form.get('location', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        update_data = {
            'full_name': full_name,
            'bio': bio,
            'location': location
        }

        # Handle password change
        if new_password:
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
                return redirect(url_for('profile.edit_profile'))
            if new_password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('profile.edit_profile'))
            from app import bcrypt
            update_data['password'] = bcrypt.generate_password_hash(
                new_password
            ).decode('utf-8')

        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                try:
                    # Delete old image if not default
                    if (current_user.profile_image and
                            current_user.profile_image != 'default.png'):
                        old_path = os.path.join(
                            current_app.config['UPLOAD_FOLDER'],
                            current_user.profile_image
                        )
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    filename = save_profile_image(file)
                    update_data['profile_image'] = filename

                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'danger')
                    return redirect(url_for('profile.edit_profile'))

        # Update database
        success = User.update(current_user.id, update_data)
        if success:
            flash('Profile updated successfully! ✅', 'success')
        else:
            flash('Error updating profile.', 'danger')

        return redirect(url_for('profile.profile'))

    # GET request
    favourites_count = Favourite.count_user_favourites(current_user.id)
    return render_template(
        'profile.html',
        user=current_user,
        edit_mode=True,
        favourites_count=favourites_count
    )