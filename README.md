# SBot: Stolen Base Opportunities Taken

Python script that builds yearly SBot leaderboards.

## Requirements

- Python 3.X
- PostgreSQL
- Statcast data (which you can get using [this script](https://github.com/jefnic23/baseball_savant_scraper))

## Installation

Download the repo using **Code > Download ZIP**, or clone the repo using git bash.

```bash
git clone https://github.com/jefnic23/SBot.git
```

## Setup

Open a console inside the `SBot` directory and create a virtual enviroment. 

```bash
python.exe -m venv venv
```

Activate the virtual environment.

```bash
venv\scripts\activate
```

Then install dependencies.

```bash
pip install -r requirements.txt
```

## Usage

Once everything is setup and dependencies are installed, create a ```.env``` file in the root directory.

```bash
type NUL > .env
```

Open the file in a text editor and copy these five variables, then assign them the appropriate value (make sure to enter the values between the quotation marks).

```
USER=''
PSWD=''
HOST=''
PORT=''
NAME=''
```

Finally, run the script from the console.

```bash
python sbot.py
```

The output is saved to the data directory in .xlsx format.

Since the script relies on Statcast data, only MLB seasons after 2015 are valid. The script will check the database for which seasons are available and generate a spreadsheet with tabs for each season.

#### Related

- [hEV](https://github.com/jefnic23/hEV)
- [wES](https://github.com/jefnic23/wES)