from setuptools import setup

setup(
    name='memcached',
    version='1.0',
    packages=['app'],
    author='Sarah Amiri',
    author_email='sarah.amiri28@gmail.com',
    description='app to run a simple memcached server',
    entry_points={
        'console_scripts': [
            'memcached=app.main:run',
        ],
    }
)
