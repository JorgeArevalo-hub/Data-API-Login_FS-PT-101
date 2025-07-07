import os
from flask_admin import Admin
from api.models import db, Users, Items, Stats, Champions, Builds, Favourites, Builditems
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(Users,db.session))
    admin.add_view(ModelView(Champions,db.session))
    admin.add_view(ModelView(Items,db.session))
    admin.add_view(ModelView(Stats,db.session))
    admin.add_view(ModelView(Builds,db.session))
    admin.add_view(ModelView(Favourites,db.session))
    admin.add_view(ModelView(Builditems,db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))