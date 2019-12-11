# Deployment

The following are the steps required to release a new version of
Cauldron. Prior to release make sure that production builds of the
web application and web notebook have been built into the Cauldron
library.

## 1. Release the package

Mac OS/Linux:

```bash
$ rm -rf ./dist
$ python3 setup.py sdist bdist_wheel
$ twine upload dist/cauldron*
$ docker run --rm -it -v $(pwd):/cauldron continuumio/anaconda3 /bin/bash
$ python3 conda-recipe/conda-builder.py
```

WINDOWS:
```powershell
> rmdir dist /s /q
> python setup.py sdist bdist_wheel
> twine upload dist/cauldron*
> docker run --rm -it -v ${pwd}:/cauldron continuumio/anaconda3 /bin/bash
> python conda-recipe/conda-builder.py
```

## 2. Push new container images

```bash
$ python docker-builder --publish
```

## 3. Update release information

```bash
$ python release.py
```
