# Deployment

## 1. Release the package

Mac OS/Linux:
```bash
$ rm -rf ./dist
$ python3 setup.py sdist bdist_wheel
$ twine upload dist/cauldron*
$ python3 conda-recipe/conda-builder.py
```

Windows:
```
> rmdir dist /s /q
> python setup.py sdist bdist_wheel
> twine upload dist/cauldron*
> python conda-recipe\conda-builder.py
```

## 2. Push new container images

```bash
$ python docker-builder --publish
```

## 3. Update release information

```bash
$ python release.py
```
