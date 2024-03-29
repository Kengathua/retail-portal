"""Package setup."""
from setuptools import find_packages, setup
# from version import get_version

name = 'retail_portal'
version = '0.0.1'
# version = get_version()

setup(
    name=name,
    version=version,
    packages=find_packages(exclude=['tests', 'tests.*']),
    description="Elites Retail Portal System",
    long_description=open('README.md').read(),
    author="ELITES",
    author_email="developers@elitesage.com",
    # license="Proprietary",
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Elites Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[
        'Django==4.1.1',
        'django-cors-headers==3.13.0',
        'django-filter==22.1',
        'django-money==2.1.1',
        'django-phonenumber-field==6.1.0',
        'djangorestframework==3.13.1',
        'dj-database-url==1.0.0',
        'gunicorn==20.1.0',
        'Pillow==9.2.0',
        'django-sendfile==0.3.11',
        'djangorestframework-simplejwt==5.1.0',
        'ipython==8.4.0',
        # 'psycopg2==2.9.3',
        'xhtml2pdf==0.2.8',
        'xlsxwriter==3.0.6',
        'psycopg2-binary==2.9.5',
        'celery==5.2.7',
        'django-cryptography==1.1',
        'gunicorn==20.1.0',
    ],
    scripts=[
        'bin/retail_portal_manage'
    ],
    include_package_data=True
)
