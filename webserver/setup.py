from setuptools import setup

setup(
    name='my_webserver',
    version='1.0',
    packages=['app'],
    author='Sarah Amiri',
    author_email='sarah.amiri28@gmail.com',
    description='app to run a simple web server',
    entry_points={
        'console_scripts': [
            'webserver=app.main:run',
        ],
    }
)
