# Development

## Design goals

* Minimal dependencies
* Easy to extend or customize

## Development dependencies

* [twine](https://twine.readthedocs.io/en/latest/): Optional. Used to publish package to PyPI

## Development installation

```bash
# Install
sudo python setup.py develop

# Uninstall
sudo python setup.py develop --uninstall
```

# Publish

## Steps

1. Update the version number in `pdmreader/__init__.py` 
2. Update changelog
3. Commit and tag: `git tag v0.1`
4. Make sure the working directory is clean to avoid unexpected change or files published. Git stash if necessary: `git stash save --include-untracked`

## TestPyPI

It's a good practice to publish to [TestPyPI](https://test.pypi.org/) before publishing to [PyPI](https://pypi.org).

[Setting up TestPyPI in pypirc](https://packaging.python.org/guides/using-testpypi/#setting-up-testpypi-in-pypirc)

```bash
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload -r testpypi dist/*
```

## PyPI

__All published versions cannot be modified. Double check before publishing.__ 

```bash
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
```
