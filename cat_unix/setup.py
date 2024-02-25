from setuptools import setup

setup(
    name='cccat',
    version='1.0',
    packages=['app'],
    author='Sarah Amiri',
    author_email='sarah.amiri28@gmail.com',
    description='app to run unix cat command tool',
    entry_points={
        'console_scripts': [
            'cccat=app.main:run',
        ],
    }
)
