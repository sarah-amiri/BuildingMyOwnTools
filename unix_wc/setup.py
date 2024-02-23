from setuptools import setup

setup(
    name='ccwc',
    version='1.0',
    packages=['app'],
    author='Sarah Amiri',
    author_email='sarah.amiri28@gmail.com',
    description='unix wc command tool implemented in Python',
    entry_points={
        'console_scripts': [
            'ccwc=app.main:run',
        ],
    }
)
