from setuptools import setup, find_packages

setup(
    name='roster', 
    version='1.0',
    description='Roster: A library for simple service discovery using Dynamodb for Python',
    long_description=open('README.md').read(),
    author='Tim Rijavec',
    author_email='tim@trustedhousesitters.com',
    url='https://github.com/trustedhousesitters/roster-python',
    license='MIT',
    packages=find_packages(exclude=('example', 'examples', )),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Service Discovery',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)