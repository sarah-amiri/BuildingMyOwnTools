from setuptools import setup

setup(
    name='myjsonparser',
    version='1.0',
    packages=['app'],
    author='Sarah Amiri',
    author_email='sarah.amiri28@gmail.com',
    description='command to parse json',
    entry_points={
        'console_scripts': [
            'jsonparser=app.main:run',
        ],
    }
)
