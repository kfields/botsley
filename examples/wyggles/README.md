# Wyggles :bug:

## Install

This package requires Cairo.  Either enter this on Ubuntu or visit https://www.cairographics.org/download/

```bash
sudo apt install libcairo2-dev
```

Navigate to a directory where you keep your software projects

```bash
cd projects
```

Clone the repository

```bash
git clone https://github.com/kfields/wyggles.git
```

Change to the new directory which contains the repository

```bash
cd wyggles
```

Create a Python 3 virtual environment called `env`

```bash
python3 -m venv env
```

Activate the environment

```bash
source env/bin/activate
```

Install required packages

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```