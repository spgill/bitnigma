import setuptools


setuptools.setup(
    name='bitnigma',
    version='1.0',
    description='Python byte-enabled Enigma-like simulation.',
    long_description=open('README.md', 'r').read(),
    keywords='enigma machine encrypt encryption rotor rotors',
    author='Samuel P. Gillispie II',
    author_email='spgill@vt.edu',
    url='https://github.com/spgill/enigma',
    license='MIT',
    packages=['bitnigma'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)
