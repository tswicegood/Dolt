# TODO: automate building of sdist
# TODO: automate uploading of sdist to github.com
from fabric.api import local

def release():
    local('python setup.py sdist upload', capture=False)

