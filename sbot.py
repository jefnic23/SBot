import os
import warnings

import pandas as pd
import pybaseball
from dotenv import load_dotenv
from sqlalchemy import create_engine
from tqdm import tqdm


def db_engine():
    '''create database connection'''
    load_dotenv()
    USER = os.getenv('USER')
    PSWD = os.getenv('PSWD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    NAME = os.getenv('NAME')
    return create_engine(f'postgresql://{USER}:{PSWD}@{HOST}:{PORT}/{NAME}')


def mlbToFg(mlbam):
    '''converts mlb ids to fangraphs ids'''
    try:
        return lookup.loc[mlbam]['key_fangraphs']
    except:
        return mlbam


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    # initialize progress bar
    pbar = tqdm(total=3, position=0, desc='Overall')

    # make directory to house leaderboards
    if not os.path.exists('data'):
        os.mkdir('data')

    # get player id data
    url            = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"
    lookup         = pd.read_csv(url, index_col="key_mlbam")
    lookup['name'] = lookup['name_first'] + ' ' + lookup['name_last']
    pbar.update(1)

    # select necessary columns from database
    columns = [
        'game_year',
        'on_1b',
        'on_2b',
        'game_pk',
        'at_bat_number',
        'bb_type'
    ]

    # get savant data from postgres
    engine = db_engine()
    df     = pd.read_sql('baseball_savant', engine, columns=columns)
    pbar.update(1)

    with pd.ExcelWriter('data/SBot_leaderboards.xlsx') as writer:
        for year in tqdm(range(df['game_year'].min(), df['game_year'].max()+1), position=1, desc="Leaderboards"):
            # drop all rows where there isn't a stolen base opportunity (runner on first, second base empty), then group by runner
            sv = df[(~df['on_1b'].isna()) & (df['on_2b'].isna())]
            sv = sv.groupby(['on_1b', 'game_pk', 'at_bat_number']).size().groupby(level=0).size().reset_index().rename(columns={0: 'Opportunities'})

            # map player ids to names
            sv['on_1b'] = sv['on_1b'].map(mlbToFg)

            # get stolen base and caught stealing data from fangraphs
            fg = pybaseball.batting_stats(year, stat_columns=['SB', 'CS'], qual=0)

            # merge fangraphs and statcast data
            df_new = pd.merge(sv, fg, left_on = "on_1b", right_on = "IDfg")
            df_new['Attempts']     = df_new['SB'] + df_new['CS']
            df_new['Success Rate'] = df_new['SB'] / df_new['Attempts']
            df_new['SBot']         = df_new['Attempts'] / df_new['Opportunities']
            df_new.set_index('Name')[['Season', 'Team', 'SB', 'CS', 'Attempts', 'Success Rate', 'Opportunities', 'SBot']].to_excel(writer, sheet_name=str(year))
    pbar.update(1)
