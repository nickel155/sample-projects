from Collections.Room import *
from Collections.Student import *

if len(Admin.objects()) == 0:
    admin = Admin(admin_id='12345',
                  name='admin',
                  email='admin@gmail.com',
                  password='admin')
    admin.save()
setup_data()
