"""
Django settings for api project.

Generated by 'django-admin startproject' using Django 2.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os, shutil, configparser
from os.path import join

# Reading setup properties from configuration file

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
configFile = BASE_DIR + "/phenotype-reactor.ini"

if not os.path.isfile(configFile):
    shutil.copyfile("default_phenotype-reactor.ini", configFile)

config = configparser.RawConfigParser()
config.read(configFile)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:4200',
]
CORS_URLS_REGEX = r'^/api/.*$'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

ARCHIVE_URL = '/archive/'
SCHEMA_URL = '/schema/'

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s %(name)-12s %(levelname)-2s %(message)s'
            },
            'file': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/tmp/phenotype-reactor.log',
                'formatter': 'file'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'api': {
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'account': {
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True,
            }
        },
    }

BIO2VEC_API_URL='https://bio2vec.cbrc.kaust.edu.sa/'
BIO2VEC_DATASET='phenotype associations'
BIO2VEC_DATASET_URI='b2vd:dataset_4'

RDF_STORE_URL = config['rdf_store']['url']
RDF_STORE_DS = config['rdf_store']['datastore']
RDF_STORE_USER = config['rdf_store']['username']
RDF_STORE_PWD = config['rdf_store']['password']

SOURCE_DATA_DIR = config['datasets']['source.dir']
ONTOLOGY_DIR = config['datasets']['source.ontology.dir']
TARGET_DATA_DIR = config['datasets']['target.dir']
EXPORT_FORMAT = config['datasets']['format']

VIRTUOSO_HOST = config['virtuoso']['server.host']
VIRTUOSO_SPARQL_PORT = config['virtuoso']['server.sparql.port']
RDF_DATA_ARCHIVE_DIR = config['datasets']['archive.dir']
KGE_DIR = config['datasets']['kge.dir']
TRAINING_SET_DIR = join(KGE_DIR, 'trainingset')
TEST_SET_DIR = join(KGE_DIR, 'testset')

ABEROWL_ES_URL = config['aberowl']['es.url']
ABEROWL_ES_USERNAME = config['aberowl']['es.username']
ABEROWL_ES_PASSWORD = config['aberowl']['es.password']
ABEROWL_ES_IDX_ONTOLOGY = config['aberowl']['es.index.ontology']
ABEROWL_ES_IDX_CLASS = config['aberowl']['es.index.class']

LOOKUP_ES_URL = config['lookup']['es.url']
LOOKUP_ES_USERNAME = config['lookup']['es.username']
LOOKUP_ES_PASSWORD = config['lookup']['es.password']
LOOKUP_ES_VALUESET_INDEX_NAME= config['lookup']['es.index.valueset.name']
LOOKUP_ES_ENTITY_INDEX_NAME = config['lookup']['es.index.entity.name']

OMIM_KEY = config['omim']['key']
OMIM_DIR = config['omim']['dir']

STATICFILES_DIRS = [
    ("schema", "schema"),
    ("doc", "doc")
]

ASSOCIATION_SET_CONFIG = {
    "deeppheno" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["NCBIGene"]
    }, 
    "textmined_disease_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["DOID"]
    },
    "sider_drug_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["PUBCHEM"]
    },
    "hpo_disease_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["OMIM", "DECIPHER", "ordo"]
    },
    "hpo_gene_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["NCBIGene"]
    },
    "textmined_metabolite_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["CHEBI"]
    },
    "mgi_gene_phenotypes" : {
        "phenotype_reference_source" : ["MP"],
        "biomedical_entity_reference_source" : ["MGI"]
    },
    "textmined_mondo_disease_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["MONDO"]
    },
    "pathopheno_disease_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["DOID"]
    },
    "pathopheno_pathogen_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["NCBITaxon_Pathopheno"]
    },
    "textmined_gene_phenotypes" : {
        "phenotype_reference_source" : ["HP", "MP"],
        "biomedical_entity_reference_source" : ["MGI", "NCBIGene"]
    }
}
