from setuptools import setup, find_packages

setup(
    name = 'portality',
    version = '0.8.0',
    packages = find_packages(),
    install_requires = [
        "werkzeug==0.8.3",
        "Flask==0.9",
        "Flask-Login==0.1.3",
        "Flask-WTF==0.8.3",
        "requests==1.1.0",
        "esprit",
        #"markdown",
        #"gitpython",
        "lxml",
        "incf.countryutils",
        "pycountry"
    ],
    url = 'http://cottagelabs.com/',
    author = 'Cottage Labs',
    author_email = 'us@cottagelabs.com',
    description = 'Open Access Repository Registry',
    license = 'Copyheart',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Copyheart',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
