# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 14:17:05 2023

@author: alexg
"""

import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
sys.path.append('C:/Users/alexg/Onedrive/Documentos/GitHub/custom_utils')
from utilsJ.paperfigs import figures_paper as fp



# ---GLOBAL VARIABLES
pc_name = 'alex'
if pc_name == 'alex':
    SV_FOLDER = 'C:/Users/alexg/Onedrive/Escritorio/CRM/'  # Alex
    DATA_FOLDER = 'C:/Users/alexg/Onedrive/Escritorio/CRM/data/'  # Alex


def plot_rt_all_subjs(reaction_time, subjid):
    subjects = np.unique(subjid)
    for subj in subjects:
        rt = reaction_time[subjid == subj]
        sns.kdeplot(rt, color='red', alpha=0.4)
        plt.axvline(300, color='k', linestyle='--')

load_params = True  # wether to load or not parameters
df_data = fp.get_human_data(user_id=pc_name, sv_folder=SV_FOLDER)
choice = df_data.R_response.values*2-1
hit = df_data.hithistory.values*2-1
subjects = df_data.subjid.unique()
# subjid = df_data.subjid.values
subjid = np.repeat('all', len(choice))  # meta subject
df_data['subjid'] = subjid
gt = (choice*hit+1)/2
coh = df_data.avtrapz.values*5
len_task = [len(df_data.loc[subjid == subject]) for subject in subjects]
trial_index = np.empty((0))
for j in range(len(len_task)):
    trial_index = np.concatenate((trial_index, np.arange(len_task[j])+1))
df_data['origidx'] = trial_index
stim = np.repeat(coh.reshape(-1, 1), 20, 1).T
hit_model, reaction_time, com_model_detected, resp_fin, com_model,\
    _, trajs, x_val_at_updt =\
    fp.simulate_model_humans(df_data=df_data, stim=stim,
                             load_params=load_params)
MT = np.array([len(t) for t in trajs])
mt_human = np.array(fp.get_human_mt(df_data))
df_data['resp_len'] = mt_human
df_data['coh2'] = coh
df_data['origidx'] = trial_index
df_data['allpriors'] = df_data.norm_allpriors.values

# simulation output: hit_model, reaction_time, mt_human, resp_fin, com_model
# trajs
