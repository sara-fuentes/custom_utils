#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 16:49:51 2022

@author: manuel
"""
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import sem
import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable
sys.path.append("C:/Users/Alexandre/Documents/psycho_priors") 
import analyses
import figures_paper as fp
from utilsJ.Models import extended_ddm_v2 as edd2
from utilsJ.Behavior.plotting import com_heatmap, tachometric


# SV_FOLDER = 'C:/Users/Alexandre/Desktop/CRM/Alex/paper/figures_python/'  # Alex
# DATA_FOLDER = 'C:/Users/Alexandre/Desktop/CRM/Alex/paper/data/'  # Alex
DATA_FOLDER = '/home/molano/ChangesOfMind/data/'  # Manuel
SV_FOLDER = '/home/molano/Dropbox/project_Barna/' +\
    'ChangesOfMind/figures/from_python/'  # Manuel
# SV_FOLDER = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/'  # Alex CRM
# DATA_FOLDER = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/data/'  # Alex CRM
# SV_FOLDER = '/home/jordi/DATA/Documents/changes_of_mind/'  # Jordi
# DATA_FOLDER = '/home/jordi/DATA/Documents/changes_of_mind/data_clean/'  # Jordi
RAT_COM_IMG = '/home/molano/Dropbox/project_Barna/' +\
    'ChangesOfMind/figures/Figure_3/001965.png'

START_ANALYSIS = 0  # trials to ignore
GREEN = np.array((77, 175, 74))/255
PURPLE = np.array((152, 78, 163))/255


def fig_1(ax, coh, hit, sound_len, choice, zt, com):
    for a in ax:
        fp.rm_top_right_lines(a)
    choice_01 = (choice+1)/2
    pos = ax[1].get_position()
    ax[1].set_position([pos.x1, pos.y0, pos.width*3/4, pos.height*3/4])
    edd2.com_heatmap_jordi(zt, coh, choice_01, ax=ax[1], flip=True,
                           annotate=False, xlabel='prior', ylabel='avg stim',
                           cmap='rocket')
    fp.tachometric_data(coh=coh, hit=hit, sound_len=sound_len, ax=ax[3])
    rat = plt.imread(RAT_COM_IMG)
    fig, ax = plt.subplots(ncols=3, figsize=(18, 5.5), gridspec_kw={
                           'width_ratios': [1, 1, 1.8]})
    fig.patch.set_facecolor('white')
    ax[4].set_facecolor('white')
    ax[4].imshow(np.flipud(rat))
    df_data = pd.DataFrame({'avtrapz': coh, 'CoM_sugg': com,
                            'norm_allpriors': zt/max(abs(zt)),
                            'R_response': (choice+1)/2})
    pos = ax[5].get_position()
    ax[5].set_position([pos.x1, pos.y0, pos.width/2, pos.height/2])
    fp.com_heatmap_paper_marginal_pcom_side(df_data, side=0, ax=ax[5])
    ax_temp = plt.axes([pos.x1+pos.width/2, pos.y0,
                        pos.width/2, pos.height/2])
    fp.com_heatmap_paper_marginal_pcom_side(df_data, side=1, ax=ax_temp)


def com_heatmap_paper_marginal_pcom_side(
    df, f=None, ax=None,  # data source, must contain 'avtrapz' and allpriors
    pcomlabel=None, fcolorwhite=True, side=0,
    hide_marginal_axis=True, n_points_marginal=None, counts_on_matrix=False,
    adjust_marginal_axes=False,  # sets same max=y/x value
    nbins=7,  # nbins for the square matrix
    com_heatmap_kws={},  # avoid binning & return_mat already handled by the functn
    com_col='CoM_sugg', priors_col='norm_allpriors', stim_col='avtrapz',
    average_across_subjects=False
):
    assert side in [0, 1], "side value must be either 0 or 1"
    assert df[priors_col].abs().max() <= 1,\
        "prior must be normalized between -1 and 1"
    assert df[stim_col].abs().max() <= 1, "stimulus must be between -1 and 1"
    if pcomlabel is None:
        if not side:
            pcomlabel = r'$p(CoM_{R \rightarrow L})$'
        else:
            pcomlabel = r'$p(CoM_{L \rightarrow R})$'

    if n_points_marginal is None:
        n_points_marginal = nbins
    # ensure some filtering
    tmp = df.dropna(subset=['CoM_sugg', 'norm_allpriors', 'avtrapz'])
    tmp['tmp_com'] = False
    tmp.loc[(tmp.R_response == side) & (tmp.CoM_sugg), 'tmp_com'] = True

    com_heatmap_kws.update({
        'return_mat': True,
        'predefbins': [
            np.linspace(-1, 1, nbins+1), np.linspace(-1, 1, nbins+1)
        ]
    })
    if not average_across_subjects:
        mat, nmat = com_heatmap(
            tmp.norm_allpriors.values,
            tmp.avtrapz.values,
            tmp.tmp_com.values,
            **com_heatmap_kws
        )
        # fill nans with 0
        mat[np.isnan(mat)] = 0
        nmat[np.isnan(nmat)] = 0
        # change data to match vertical axis image standards (0,0) ->
        # in the top left
    else:
        com_mat_list, number_mat_list = [], []
        for subject in tmp.subjid.unique():
            cmat, cnmat = com_heatmap(
                tmp.loc[tmp.subjid == subject, 'norm_allpriors'].values,
                tmp.loc[tmp.subjid == subject, 'avtrapz'].values,
                tmp.loc[tmp.subjid == subject, 'tmp_com'].values,
                **com_heatmap_kws
            )
            cmat[np.isnan(cmat)] = 0
            cnmat[np.isnan(cnmat)] = 0
            com_mat_list += [cmat]
            number_mat_list += [cnmat]

        mat = np.stack(com_mat_list).mean(axis=0)
        nmat = np.stack(number_mat_list).mean(axis=0)

    mat = np.flipud(mat)
    nmat = np.flipud(nmat)
    return mat


def matrix_figure(df_data, humans, ax_tach, ax_pright, ax_mat):
    nbins = 7
    matrix_side_0 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=0)
    matrix_side_1 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=1)
    # L-> R
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_1 = r'$p(CoM_{L \rightarrow R})$'
    ax_mat.set_title(pcomlabel_1)
    im_1 = ax_mat.imshow(matrix_side_1, vmin=0, vmax=vmax)
    divider = make_axes_locatable(ax_mat)
    cax = divider.append_axes('left', size='10%', pad=0.9)
    plt.colorbar(im_1, cax=cax)
    # R -> L
    pos = ax_mat.get_position()
    ax_mat.set_position([pos.x0, pos.y0, pos.width/2, pos.height])
    ax_mat_1 = plt.axes([pos.x0+pos.width/2, pos.y0,
                         pos.width/2, pos.height])
    pcomlabel_0 = r'$p(CoM_{L \rightarrow R})$'
    divider = make_axes_locatable(ax_mat_1)
    cax = divider.append_axes('right', size='10%', pad=0.9)
    cax.axis('off')
    ax_mat_1.set_title(pcomlabel_0)
    ax_mat_1.imshow(matrix_side_0, vmin=0, vmax=vmax)
    ax_mat_1.yaxis.set_ticks_position('none')
    for ax_i in [ax_pright, ax_mat, ax_mat_1]:
        ax_i.set_xlabel(r'$\longleftarrow$Prior$\longrightarrow$')
        ax_i.set_yticks(np.arange(nbins))
        ax_i.set_xticks(np.arange(nbins))
        ax_i.set_xticklabels(['left']+['']*(nbins-2)+['right'])
    for ax_i in [ax_pright, ax_mat]:
        ax_i.set_yticklabels(['right']+['']*(nbins-2)+['left'])
        ax_i.set_ylabel(r'$\longleftarrow$Average stimulus$\longrightarrow$',
                        labelpad=-17)
    ax_mat_1.set_yticklabels(['']*nbins)
    choice = df_data['R_response'].values
    coh = df_data['avtrapz'].values
    prior = df_data['norm_allpriors'].values
    mat_pright, _ = com_heatmap(prior, coh, choice, return_mat=True,
                                annotate=False)
    mat_pright = np.flipud(mat_pright)
    im_2 = ax_pright.imshow(mat_pright, cmap='rocket')
    divider = make_axes_locatable(ax_pright)
    cax1 = divider.append_axes('left', size='10%', pad=0.6)
    plt.colorbar(im_2, cax=cax1)
    cax1.yaxis.set_ticks_position('left')
    ax_pright.set_title('p(right)')
    if humans:
        num = 8
        rtbins = np.linspace(0, 300, num=num)
        tachometric(df_data, ax=ax_tach, fill_error=True, rtbins=rtbins)
    else:
        tachometric(df_data, ax=ax_tach, fill_error=True)
    ax_tach.axhline(y=0.5, linestyle='--', color='k', lw=0.5)
    ax_tach.set_xlabel('RT (ms)')
    ax_tach.set_ylabel('Accuracy')
    ax_tach.set_ylim(0.4, 1.04)
    ax_tach.spines['right'].set_visible(False)
    ax_tach.spines['top'].set_visible(False)


def traj_analysis(main_folder, subjects, steps=[None], name=''):
    for i_s, subj in enumerate(subjects):
        print('-----------')
        print(subj)
        folder = main_folder+subj+'/'
        for i_stp, stp in enumerate(steps):
            data_tr, data_traj = get_data_traj(folder=folder)
            com(data_tr, data_traj, com_threshold=100, plot=True)


def get_data_traj(folder, plot=False):
    """
    Extracts trajectories and psychometric data.
    Inputs: subject name (subj) and main_folder
    Outputs: psychometric data and trajectories data in two different dictionaries
    """
    # subject folder
    # folder = main_folder+'\\'+subj+'\\'  # Alex
    # find all data files
    files_trials = glob.glob(folder+'*trials.csv')
    files_traj = glob.glob(folder+'*trials-trajectories.csv')
    # take files names
    file_list_trials = [os.path.basename(x) for x in files_trials
                        if x.endswith('trials.csv')]
    file_list_traj = [os.path.basename(x) for x in files_traj
                      if x.endswith('trials-trajectories.csv')]
    # sort files
    sfx_tls = [x[x.find('202'):x.find('202')+15] for x in file_list_trials]
    sfx_trj = [x[x.find('202'):x.find('202')+15] for x in file_list_traj]

    sorted_list_tls = [x for _, x in sorted(zip(sfx_tls, file_list_trials))]
    sorted_list_trj = [x for _, x in sorted(zip(sfx_trj, file_list_traj))]
    # create data
    data_tls = {'correct': np.empty((0,)), 'answer_response': np.empty((0,)),
                'soundPlay_object1_leftRightBalance': np.empty((0,)),
                'respondedInTime': np.empty((0,)), 'block': np.empty((0,)),
                'soundPlay_responseTime': np.empty((0,)),
                'soundPlay_duration': np.empty((0,)),
                'answer_responseTime': np.empty((0,))}
    # go over all files
    for f in sorted_list_tls:
        # read file
        df1 = pd.read_csv(folder+'/'+f, sep=',')  # Manuel
        # df1 = pd.read_csv(folder+'\\'+f, sep=',')  # Alex
        for k in data_tls.keys():
            values = df1[k].values[START_ANALYSIS:]
            if k == 'soundPlay_object1_leftRightBalance':
                values = values-.5
                values[np.abs(values) < 0.01] = 0
            data_tls[k] = np.concatenate((data_tls[k], values))
    num_tr = len(data_tls['correct'])
    data_trj = {'answer_positionsX': np.empty((0,)),
                'answer_positionsY': np.empty((0,)),
                'answer_times': np.empty((0,))}
    if plot:
        _, ax = plt.subplots()
    for f in sorted_list_trj:
        # read file
        df1 = pd.read_csv(folder+'/'+f, sep=',')  # Manuel
        # df1 = pd.read_csv(folder+'\\'+f, sep=',')  # Alex
        pos_x = df1['answer_positionsX'].dropna().values[:num_tr]
        pos_y = df1['answer_positionsY'].dropna().values[:num_tr]
        cont = 0
        for ind_trl in range(len(pos_x)):
            if cont == 1 and df1['trial'][ind_trl] == 1:
                break
            if df1['trial'][ind_trl] == 1:
                cont = 1
            pos_x[ind_trl] = [float(x) for x in pos_x[ind_trl].split(';')]
            pos_y[ind_trl] = [float(x) for x in pos_y[ind_trl].split(';')]
            if plot:
                color = PURPLE if data_tls['answer_response'][ind_trl] == 1\
                    else GREEN
                ax.plot(pos_x[ind_trl], pos_y[ind_trl], color=color)
        k = 'answer_positionsX'
        data_trj[k] = np.concatenate((data_trj[k], pos_x))
        k = 'answer_positionsY'
        data_trj[k] = np.concatenate((data_trj[k], pos_y))
        k = df1.columns[-1]
        values = df1[k].dropna().values
        k = 'answer_times'
        data_trj[k] = np.concatenate((data_trj[k], values))
    return data_tls, data_trj


def fig_3(user_id, existing_data_path, ax_tach, ax_pright, ax_mat, humans=False):
    if user_id == 'Alex':
        folder = 'C:\\Users\\Alexandre\\Desktop\\CRM\\Human\\80_20'
    if user_id == 'Manuel':
        folder = '/home/molano/Dropbox/project_Barna/psycho_project/80_20/'
    subj = ['general_traj']
    steps = [None]
    nm = '300'
    df_data = traj_analysis(main_folder=folder+'\\'+nm+'ms\\',
                            subjects=subj, steps=steps, name=nm,
                            existing_data_path=existing_data_path)
    df_data.avtrapz /= max(abs(df_data.avtrapz))
    matrix_figure(df_data=df_data, ax_tach=ax_tach, ax_pright=ax_pright,
                  ax_mat=ax_mat, humans=humans)


if __name__ == '__main__':
    plt.close('all')
    rats = True
    if rats:
        subject = 'LE43'
        all_rats = False
        if all_rats:
            df = edd2.get_data_and_matrix(dfpath=DATA_FOLDER + 'meta_subject/',
                                          return_df=True, sv_folder=SV_FOLDER,
                                          after_correct=True, silent=True,
                                          all_trials=True)
        else:
            df = edd2.get_data_and_matrix(dfpath=DATA_FOLDER + subject,
                                          return_df=True, sv_folder=SV_FOLDER,
                                          after_correct=True, silent=True,
                                          all_trials=True)
        after_correct_id = np.where(df.aftererror == 0)[0]
        zt = np.nansum(df[["dW_lat", "dW_trans"]].values, axis=1)
        zt = zt[after_correct_id]
        hit = np.array(df['hithistory'])
        hit = hit[after_correct_id]
        stim = np.array([stim for stim in df.res_sound])
        stim = stim[after_correct_id, :]
        coh = np.array(df.coh2)
        coh = coh[after_correct_id]
        com = df.CoM_sugg.values
        com = com[after_correct_id]
        choice = np.array(df.R_response) * 2 - 1
        choice = choice[after_correct_id]
        sound_len = np.array(df.sound_len)
        sound_len = sound_len[after_correct_id]
        gt = np.array(df.rewside) * 2 - 1
        gt = gt[after_correct_id]
        trial_index = np.array(df.origidx)
        trial_index = trial_index[after_correct_id]
        df_data = pd.DataFrame({'avtrapz': coh, 'CoM_sugg': com,
                                'norm_allpriors': zt/max(abs(zt)),
                                'R_response':
                                    np.array(df.R_response)[after_correct_id],
                                'sound_len': sound_len,
                                'hithistory': hit})
        f, ax = plt.subplots(nrows=2, ncols=2)
        ax = ax.flatten()
        ax[0].axis('off')
        matrix_figure(df_data, ax_tach=ax[1], ax_pright=ax[2],
                      ax_mat=ax[3], humans=False)
    # if we want to use data from all rats, we must use dani_clean.pkl
    f1 = True
    f2 = False
    f3 = False

    # fig 1
    if f1:
        f, ax = plt.subplots(nrows=2, ncols=3)
        # fig1.d(df, savpath=SV_FOLDER, average=True)  # psychometrics
        # tachometrics, rt distribution, express performance
        fig_1(coh=coh, hit=hit, sound_len=sound_len,
              choice=choice, zt=zt, com=com, supt='')

    # fig 2
    if f2:
        fgsz = (8, 8)
        inset_sz = 0.1
        f, ax = plt.subplots(nrows=2, ncols=2, figsize=fgsz)
        ax = ax.flatten()
        ax_cohs = np.array([ax[0], ax[2]])
        ax_inset = fp.add_inset(ax=ax_cohs[0], inset_sz=inset_sz, fgsz=fgsz)
        ax_cohs = np.insert(ax_cohs, 0, ax_inset)
        ax_inset = fp.add_inset(ax=ax_cohs[2], inset_sz=inset_sz, fgsz=fgsz,
                                marginy=0.15)
        ax_cohs = np.insert(ax_cohs, 2, ax_inset)
        for a in ax:
            fp.rm_top_right_lines(a)
        fp.trajs_cond_on_coh(df=df, ax=ax_cohs)
        # splits
        ax_split = np.array([ax[1], ax[3]])
        fp.trajs_splitting(df, ax=ax_split[0])
        # XXX: do this panel for all rats?
        fp.trajs_splitting_point(df=df, ax=ax_split[1])
        # fig3.trajs_cond_on_prior(df, savpath=SV_FOLDER)

    if f3:
        # fig 3
        f, ax = plt.subplots(nrows=2, ncols=2)
        ax = ax.flatten()
        ax[0].axis('off')
        fig_3(user_id='Alex',
              existing_data_path=DATA_FOLDER+'/df_regressors.csv',
              ax_tach=ax[1], ax_pright=ax[2],
              ax_mat=ax[3], humans=True)
