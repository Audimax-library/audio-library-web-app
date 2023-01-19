from flask import redirect, url_for, flash
from functools import wraps
from flask_login import current_user

def is_allowed(user, allowed_roles=[]):
  def inner_decorator(f):
    def wrapped(*args, **kwargs):
      if user.userlevel in allowed_roles:
        return f(*args, **kwargs)
      else:
        flash('Invalid URL.', 'error')
        return redirect(url_for('webapp.home_page'))
    return wrapped
  return inner_decorator