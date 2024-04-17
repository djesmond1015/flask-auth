from flask.cli import FlaskGroup

from app import app, db 
from app.accounts.models import User

import getpass
from datetime import datetime

cli = FlaskGroup(app)

@cli.command('create_admin')
def create_admin():
    email =input("Enter email address: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Enter password again: ")
    if password != confirm_password:
        print('Passwords don\'t match')
    else:
        try:
            user = User(
                email =email,
                password = password,
                is_admin = True,
                is_confirmed  = True,
                confirmed_on = datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            print(f'Admin with email {email} created successfully!')
        except Exception:
            print('Couldn\'t create admin user.')

# command to recreate database
@cli.command('recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('Database recreated successfully!')

if __name__ == "__main__":
    cli()
