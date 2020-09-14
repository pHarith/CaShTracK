from flask import Blueprint, render_template as rnd_tmp

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def error_404(error):
    return rnd_tmp('errors/404.html'), 404

@errors.app_errorhandler(403)
def error_403(error):
    return rnd_tmp('errors/403.html'), 403

@errors.app_errorhandler(500)
def error_500(error):
    return rnd_tmp('errors/500.html'), 500

