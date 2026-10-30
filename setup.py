from setuptools import setup, find_packages

install_requires = [
    'django>=6.1,<6.2',
]

version = "0.4.0"

setup(name='django-medusa',
    version=version,
    description='A Django static website generator.',
    author='Mike Tigas', # update this as needed
    author_email='mike@tig.as', # update this as needed
    url='https://github.com/mtigas/django-medusa/',
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='>=3.12',
    install_requires=install_requires,
    license='MIT',
    keywords='django static staticwebsite staticgenerator publishing',
    classifiers=["Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 6.1",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
