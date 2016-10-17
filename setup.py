import os
import setuptools


def readme():
    try:
        import requests
        if os.path.isfile('README.md'):
            r = requests.post(
                url='http://c.docverter.com/convert',
                data={'from': 'markdown', 'to': 'rst'},
                files={'input_files[]': open('README.md', 'r')}
            )
            if r.ok:
                return r.content.decode()
            else:
                return 'ERROR CONVERTING README!'
    except ImportError:
        print('No `requests` module. No readme conversion applied.')
        return '!!NO CONVERSION!!\n\n' + open('README.md', 'r').read()


setuptools.setup(
    name='bitnigma',
    version='1.0.3',
    description='Python byte-enabled Enigma-like simulation.',
    long_description=readme(),
    keywords='enigma machine encrypt encryption rotor rotors',
    author='Samuel P. Gillispie II',
    author_email='spgill@vt.edu',
    url='https://github.com/spgill/bitnigma',
    license='MIT',
    packages=['bitnigma'],
    install_requires=[
        'colorama'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)
