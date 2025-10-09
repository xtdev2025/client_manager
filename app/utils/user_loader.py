from flask_login import UserMixin
from app.models.user import User

class UserObject(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_id):
        self.id = user_id
        self._user = None
    
    @property
    def user(self):
        if self._user is None:
            self._user = User.get_by_id(self.id)
        return self._user
    
    @property
    def is_admin(self):
        """Check if user is an admin"""
        if self.user:
            return self.user.get('role') in ['admin', 'super_admin']
        return False
    
    @property
    def is_super_admin(self):
        """Check if user is a super admin"""
        if self.user:
            return self.user.get('role') == 'super_admin'
        return False

def init_user_loader(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        user = User.get_by_id(user_id)
        if user:
            return UserObject(user_id)
        return None