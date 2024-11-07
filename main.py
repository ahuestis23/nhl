import requests
import pandas as pd
import time
import streamlit as st

corr_24 = pd.read_csv('top_player_correlations24.csv')
corr_23 = pd.read_csv('top_player_correlations23.csv')

#Join the pair's correlations from 2023 onto 2024 dataset
corr_24 = corr_24.merge(corr_23.add_suffix('_2023'), left_on='pair_id', right_on='pair_id_2023', how='left')

#Drop set of columns
columns = ['pair_id_2023', 'Player A_2023', 'Player B_2023','Team_2023']
corr_24 = corr_24.drop(columns=columns, axis=1)
           

corr_24.to_csv('final_corr24.csv', index=False)

