# Tozti

This repository contains the core of the tozti software project. It is licensed
under the AGPLv3. See [documentation](https://tozti.readthedocs.io/en/latest/)
for more informations.


## Quickstart

### Dependencies

For this project to work you will need:
- nodejs (for npm)
- python3

### Install Tozti

First, start by creating a virtualenv and activate it:
```
python3 -m venv .venv
source .venv/bin/activate
```

The next step is to install tozti's dependencies. This can be done like that:
```
pip install -r requirements.txt
```

```
npm install
npm run-script build
```

```
python3 -m tozti dev
```

### Install an extension

To install an extension, copy the extension inside `extensions/`.
Then, inside `extensions/<extension-name>/`, run `npm run build`

### Start Tozti

Once every extensions is installed, launch tozti with:
```
python -m tozti dev
```

## Further documentations:

See [documentation](https://tozti.readthedocs.io/en/latest/) for more documentations.

## Troubleshooting:

> I've installed a new extension but it is not launching with the server 

Make sure you have executed `npm run build` in this extension folder. Then, restart 
Tozti if needed.
