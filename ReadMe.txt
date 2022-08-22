Payroll Integration ReadMe File,

Django version = 2.2.1
Python version = 3.5.4

Postgresql Database
Username: Dax
Location: C:\ProgramData\PayrollIntegration\Data
Command to start the server: "pg_ctl" -D "C:\ProgramData\PayrollIntegration\Data" -l logfile start

To access the development environment from a console in windows use the command:
	workon payrollIntegration




history of events:
	Installed virtualenvwrapper: pip install virtualenvwrapper-win
	Created project: mkvirtualenv payrollIntegration
	Installed Django in the project: pip install django

	Initialized a new database cluster for postgresql: initdb -D C:\ProgramData\PayrollIntegration\Data
	Started the service: "pg_ctl" -D "C:\ProgramData\PayrollIntegration\Data" -l logfile start
	Created database: createdb

	Created django project: django-admin startproject payrollInt
	Project created in: C:\Users\Dax\payrollInt
	Ran the project: python manage.py runserver

	Entered Postgresql console: psql
	Created a new user: CREATE USER admin WITH PASSWORD '1744202';
	Created a new database: CREATE DATABASE payint WITH OWNER admin;
	Granted permissions to admin: GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;

	Updated the settings.py file in the django project to look like this:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'payint',
        'USER': 'Dax',
        'PASSWORD': '1744202',
        'HOST': 'localhost',
        'PORT': '12015',
    }
}

	Created migrations: python manage.py makemigrations
	Migrated: python manage.py migrate
	Created superuser: python manage.py createsuperuser
		Username: admin
		Email address: dax@timeclick.com
		Password: 1744202
	

	
	