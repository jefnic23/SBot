from datetime import datetime
from tqdm import tqdm
import pandas as pd
import pybaseball
import warnings
import os


def mlbToFg(mlbam):
    '''
    converts mlb ids to fangraphs ids
    '''
    try:
        return lookup.loc[mlbam]['key_fangraphs']
    except:
        return mlbam


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    while True:
        year = input("Enter a year from 2015 to present: ")
        try:
            year = int(year)
        except ValueError:
            print('Not a valid year')
            continue
        if 2015 <= year <= datetime.now().year:
            break
        else:
            print('Not a valid year')

    # initialize progress bar
    pbar = tqdm(total=70)

    while True:
        # get player id data and read into a pandas dataframe
        url = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv"
        lookup = pd.read_csv(url, index_col="key_mlbam")
        pbar.update(10)

        # locate savant data and read into pandas dataframe
        dir = os.path.abspath(f'../baseball_savant/data/savant_{year}.csv')
        sv = pd.read_csv(dir)
        pbar.update(10)

        # drop all rows where there isn't a stolen base opportunity (runner on first, second base empty), then group by runner
        sv = sv[(~sv['on_1b'].isna()) & (sv['on_2b'].isna())]
        sv = sv.groupby(['on_1b', 'game_pk', 'at_bat_number']).size().groupby(level=0).size().reset_index().rename(columns={0: 'Opportunities'})
        pbar.update(10)

        # map player ids to names
        sv['on_1b'] = sv['on_1b'].map(mlbToFg)
        pbar.update(10)

        # get stolen base and caught stealing data from fangraphs
        fg = pybaseball.batting_stats(year, stat_columns=['SB', 'CS'], qual=0)
        pbar.update(10)

        # merge fangraphs and statcast data
        df = pd.merge(sv, fg, left_on="on_1b", right_on="IDfg")
        df['Attempts'] = df['SB'] + df['CS']
        df['Success Rate'] = df['SB'] / df['Attempts']
        df['SBot'] = df['Attempts'] / df['Opportunities']
        pbar.update(10)

        # make directory to house savant data
        if not os.path.exists('data'):
            os.mkdir('data')

        df.set_index('Name')[['Season', 'Team', 'SB', 'CS', 'Attempts', 'Success Rate', 'Opportunities', 'SBot']].to_csv(f'data/SBot_{year}.csv')
        pbar.update(10)

        break
