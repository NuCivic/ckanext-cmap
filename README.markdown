ckanext-cmap
============

Custom CKAN extension for the CMAP Data Sharing Hub.

## Installation

To install into a Python virtual environment, make sure your virtualenv is
activated then run this command:

    pip install -e 'git+https://github.com/NewAmsterdamIdeas/ckanext-cmap.git#egg=ckanext-cmap'

## Testing

ckanext-cmap comes with a `test-core.ini` file that can be used to run CKAN's
tests with the ckanext-cmap extension enabled. From the ckanext-cmap directory,
run this command:

    nosetests --ckan --with-pylons=test-core.ini ../ckan/ckan/tests/

(where `../ckan/ckan/tests` should be the path to the tests directory of your
copy of CKAN).

When the tests finish you should see something like this:

    ----------------------------------------------------------------------
    Ran 1199 tests in 782.876s

    OK (SKIP=29)

indicating that all tests either passed OK or were skipped (no failures or
errors).

`ckanext-cmap/ckanext/cmap/cmap_nose_plugin.py` contains a [nose][] plugin that
causes some of CKAN's tests to be skipped, these are tests that are expected to
fail due to deliberate changes made by ckanext-cmap to CKAN's behaviour.
`CMAPNosePlugin` will be enabled whenever ckanext-cmap is installed in your
virtual environment.

[nose]: http://readthedocs.org/docs/nose/ "A testing framework for Python"
