from flask_login import UserMixin
from app.models.user import User
from app.models.plan import Plan

class UserObject(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_id):
        self.id = user_id
        self._user = None
        self._plan = None
    
    @property
    def user(self):
        if self._user is None:
            self._user = User.get_by_id(self.id)
        return self._user
    
    @property
    def plan(self):
        """Get user's plan"""
        if self._plan is None and self.user:
            plan_id = self.user.get('plan_id')
            if plan_id:
                self._plan = Plan.get_by_id(plan_id)
        return self._plan
    
    @property
    def expiredAt(self):
        """Get user's plan expiration date"""
        if self.user:
            return self.user.get('expiredAt')
        return None
    
    @property
    def planActivatedAt(self):
        """Get user's plan activation date"""
        if self.user:
            return self.user.get('planActivatedAt')
        return None
    
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