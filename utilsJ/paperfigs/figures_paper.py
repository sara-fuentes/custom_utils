# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 10:24:12 2022
@author: Alex Garcia-Duran
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import sem
import sys
from scipy.optimize import curve_fit
from sklearn.metrics import roc_curve
from sklearn.metrics import RocCurveDisplay
from sklearn.metrics import confusion_matrix
# from scipy import interpolate
sys.path.append("/home/jordi/Repos/custom_utils/")  # Jordi
# sys.path.append("C:/Users/Alexandre/Documents/GitHub/")  # Alex
# sys.path.append("C:/Users/agarcia/Documents/GitHub/custom_utils")  # Alex CRM
# sys.path.append("/home/garciaduran/custom_utils")  # Cluster Alex
from utilsJ.Models import simul
from utilsJ.Models import extended_ddm_v2 as edd2
from utilsJ.Behavior.plotting import binned_curve, tachometric, psych_curve,\
    com_heatmap_paper_marginal_pcom_side, trajectory_thr, com_heatmap
from utilsJ.Models import analyses_humans as ah
import fig1, fig3, fig2
import matplotlib
import matplotlib.pylab as pl

matplotlib.rcParams['font.size'] = 8
# matplotlib.rcParams['font.family'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Helvetica'
matplotlib.rcParams['lines.markersize'] = 3

# SV_FOLDER = 'C:/Users/Alexandre/Desktop/CRM/Alex/paper/figures_python/'  # Alex
# DATA_FOLDER = 'C:/Users/Alexandre/Desktop/CRM/Alex/paper/data/'  # Alex
# DATA_FOLDER = '/home/molano/ChangesOfMind/data/'  # Manuel
# SV_FOLDER = '/home/molano/Dropbox/project_Barna/' +\
#     'ChangesOfMind/figures/from_python/'  # Manuel
# SV_FOLDER = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/'  # Alex CRM
# DATA_FOLDER = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/data/'  # Alex CRM
SV_FOLDER = '/home/jordi/DATA/Documents/changes_of_mind/'  # Jordi
DATA_FOLDER = '/home/jordi/DATA/Documents/changes_of_mind/data_clean/'  # Jordi
# RAT_COM_IMG = '/home/molano/Dropbox/project_Barna/' +\
#     'ChangesOfMind/figures/Figure_3/001965.png'
# RAT_COM_IMG = 'C:/Users/Alexandre/Desktop/CRM/rat_image/001965.png'
# RAT_COM_IMG = 'C:/Users/Alexandre/Desktop/CRM/rat_image/001965.png'
RAT_COM_IMG = '/home/jordi/Documents/changes_of_mind/demo/materials/' +\
    'craft_vid/CoM/a/001965.png'
FRAME_RATE = 14
BINS_RT = np.linspace(1, 301, 11)
xpos_RT = int(np.diff(BINS_RT)[0])


def plot_coms(df, ax, human=False):
    coms = df.CoM_sugg.values
    decision = df.R_response.values
    if human:
        ran_max = 600
        max_val = 600
    if not human:
        ran_max = 900
        max_val = 77
    for tr in reversed(range(ran_max)):  # len(df_rat)):
        if tr > (ran_max/1.06) and not coms[tr] and decision[tr] == 1:
            trial = df.iloc[tr]
            traj = trial['trajectory_y']
            if not human:
                time = np.arange(len(traj))*FRAME_RATE
                ax.plot(time, traj, color='tab:cyan', lw=.5)
            if human:
                time = np.array(trial['times'])
                if time[-1] < 0.3 and time[-1] > 0.1:
                    ax.plot(time*1e3, traj, color='tab:cyan', lw=.5)
        elif tr < (ran_max/1.06-1) and coms[tr] and decision[tr] == 0:
            trial = df.iloc[tr]
            traj = trial['trajectory_y']
            if not human:
                time = np.arange(len(traj))*FRAME_RATE
                ax.plot(time, traj, color='tab:olive', lw=2)
            if human:
                time = np.array(trial['times'])
                if time[-1] < 0.3 and time[-1] > 0.2:
                    ax.plot(time*1e3, traj, color='tab:olive', lw=2)
    rm_top_right_lines(ax)
    if human:
        var = 'x'
        sp = 'Subject'
    if not human:
        var = 'y'
        sp = 'Rats'
    ax.set_ylabel('{} position {}-axis (pixels)'.format(sp, var))
    ax.set_xlabel('Time from movement onset (ms)')
    ax.axhline(y=max_val, linestyle='--', color='Green', lw=1)
    ax.axhline(y=-max_val, linestyle='--', color='Purple', lw=1)
    ax.axhline(y=0, linestyle='--', color='k', lw=0.5)


def tracking_image(ax):
    rat = plt.imread(RAT_COM_IMG)
    ax.set_facecolor('white')
    ax.imshow(np.flipud(rat[100:-100, 350:-50, :]))
    ax.axis('off')


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
    # plot tachometrics
    if humans:
        num = 8
        rtbins = np.linspace(0, 300, num=num)
        tachometric(df_data, ax=ax_tach, fill_error=True, rtbins=rtbins,
                    cmap='gist_yarg')
    else:
        tachometric(df_data, ax=ax_tach, fill_error=True, cmap='gist_yarg')
    ax_tach.axhline(y=0.5, linestyle='--', color='k', lw=0.5)
    ax_tach.set_xlabel('Reaction Time (ms)')
    ax_tach.set_ylabel('Accuracy')
    ax_tach.set_ylim(0.3, 1.04)
    ax_tach.spines['right'].set_visible(False)
    ax_tach.spines['top'].set_visible(False)
    ax_tach.legend()
    # plot Pcoms matrices
    nbins = 7
    matrix_side_0 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=0)
    matrix_side_1 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=1)
    # L-> R
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[0].set_title(pcomlabel_1)
    im = ax_mat[0].imshow(matrix_side_1, vmin=0, vmax=vmax)
    plt.sca(ax_mat[0])
    plt.colorbar(im, fraction=0.04)
    # pos = ax_mat.get_position()
    # ax_mat.set_position([pos.x0, pos.y0*2/3, pos.width, pos.height])
    # ax_mat_1 = plt.axes([pos.x0+pos.width+0.05, pos.y0*2/3,
    #                      pos.width, pos.height])
    pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[1].set_title(pcomlabel_0)
    im = ax_mat[1].imshow(matrix_side_0, vmin=0, vmax=vmax)
    ax_mat[1].yaxis.set_ticks_position('none')
    plt.sca(ax_mat[1])
    plt.colorbar(im, fraction=0.04)
    # pright matrix
    choice = df_data['R_response'].values
    coh = df_data['coh2'].values
    prior = df_data['norm_allpriors'].values
    mat_pright, _ = com_heatmap(prior, coh, choice, return_mat=True,
                                annotate=False)
    mat_pright = np.flipud(mat_pright)
    im_2 = ax_pright.imshow(mat_pright, cmap='PRGn_r')
    plt.sca(ax_pright)
    plt.colorbar(im_2, fraction=0.04)
    ax_pright.set_title('Proportion of rightward responses')

    # R -> L
    for ax_i in [ax_pright, ax_mat[0], ax_mat[1]]:
        ax_i.set_xlabel('Prior Evidence')
        # ax_i.set_yticks(np.arange(nbins))
        # ax_i.set_xticks(np.arange(nbins))
        # ax_i.set_xticklabels(['left']+['']*(nbins-2)+['right'])
        ax_i.set_yticklabels(['']*nbins)
        ax_i.set_xticklabels(['']*nbins)
    for ax_i in [ax_pright, ax_mat[0]]:
        # ax_i.set_yticklabels(['right']+['']*(nbins-2)+['left'])
        ax_i.set_ylabel('Stimulus Evidence')  # , labelpad=-17)


def rm_top_right_lines(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def pcom_model_vs_data(detected_com, com, sound_len, reaction_time):
    fig, ax = plt.subplots(1)
    rm_top_right_lines(ax)
    df = pd.DataFrame({'com_model': detected_com, 'CoM_sugg': com,
                       'sound_len': sound_len, 'reaction_time': reaction_time})
    binned_curve(df, 'CoM_sugg', 'sound_len', bins=BINS_RT, xpos=xpos_RT, ax=ax,
                 errorbar_kw={'label': 'CoM data'})
    binned_curve(df, 'com_model', 'reaction_time', bins=BINS_RT, xpos=xpos_RT,
                 ax=ax, errorbar_kw={'label': 'Detected CoM model'})


def MT_model_vs_data(MT_model, MT_data, bins_MT=np.linspace(50, 600, num=26,
                                                            dtype=int)):
    fig, ax = plt.subplots(1)
    rm_top_right_lines(ax)
    ax.set_title('MT distributions')
    hist_MT_model, _ = np.histogram(MT_model, bins=bins_MT)
    ax.plot(bins_MT[:-1]+(bins_MT[1]-bins_MT[0])/2, hist_MT_model,
            label='model MT dist')
    hist_MT_data, _ = np.histogram(MT_data, bins=bins_MT)
    ax.scatter(bins_MT[:-1]+(bins_MT[1]-bins_MT[0])/2, hist_MT_data,
               label='data MT dist')
    ax.set_xlabel('MT (ms)')


def plot_RT_distributions(sound_len, RT_model, pro_vs_re):
    fig, ax = plt.subplots(1)
    rm_top_right_lines(ax)
    bins = np.linspace(-300, 400, 40)
    ax.hist(sound_len, bins=bins, density=True, ec='k', label='Data')
    hist_pro, _ = np.histogram(RT_model[0][pro_vs_re == 1], bins)
    hist_re, _ = np.histogram(RT_model[0][pro_vs_re == 0], bins)
    ax.plot(bins[:-1]+(bins[1]-bins[0])/2,
            hist_pro/(np.sum(hist_pro)*np.diff(bins)), label='Proactive only')
    ax.plot(bins[:-1]+(bins[1]-bins[0])/2,
            hist_re/(np.sum(hist_re)*np.diff(bins)), label='Reactive only')
    hist_total, _ = np.histogram(RT_model[0], bins)
    ax.plot(bins[:-1]+(bins[1]-bins[0])/2,
            hist_total/(np.sum(hist_total)*np.diff(bins)), label='Model')
    ax.legend()


def tachometrics_data_and_model(coh, hit_history_model, hit_history_data,
                                RT_data, RT_model):
    fig, ax = plt.subplots(ncols=2)
    rm_top_right_lines(ax[0])
    rm_top_right_lines(ax[1])
    df_plot_data = pd.DataFrame({'avtrapz': coh, 'hithistory': hit_history_data,
                                 'sound_len': RT_data})
    tachometric(df_plot_data, ax=ax[0])
    ax[0].set_xlabel('RT (ms)')
    ax[0].set_ylabel('Accuracy')
    ax[0].set_title('Data')
    df_plot_model = pd.DataFrame({'avtrapz': coh, 'hithistory': hit_history_model,
                                 'sound_len': RT_model})
    tachometric(df_plot_model, ax=ax[1])
    ax[1].set_xlabel('RT (ms)')
    ax[1].set_ylabel('Accuracy')
    ax[1].set_title('Model')


def add_inset(ax, inset_sz=0.2, fgsz=(4, 8), marginx=0.05, marginy=0.05):
    ratio = fgsz[0]/fgsz[1]
    pos = ax.get_position()
    ax_inset = plt.axes([pos.x1-inset_sz-marginx, pos.y0+marginy, inset_sz,
                         inset_sz*ratio])
    return ax_inset


def trajs_cond_on_coh(df, ax, average=False, prior_limit=0.25, rt_lim=25,
                      after_correct_only=True, trajectory="trajectory_y",
                      velocity=("traj_d1", 1), acceleration=('traj_d2', 1),
                      accel=False):
    """median position and velocity in silent trials splitting by prior"""
    # TODO: adapt for mean + sem
    nanidx = df.loc[df[['dW_trans', 'dW_lat']].isna().sum(axis=1) == 2].index
    df['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df.loc[nanidx, 'allpriors'] = np.nan
    df['choice_x_coh'] = (df.R_response*2-1) * df.coh2
    bins = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]

    # dani_rats: # this is with sound, it can use all sunbjects data
    for subject in df.subjid.unique():
        if after_correct_only:
            ac_cond = df.aftererror == False
        else:
            ac_cond = (df.aftererror*1) >= 0
        # position
        indx_trajs = (df.subjid == subject) &\
            (df.allpriors.abs() < prior_limit) &\
            ac_cond & (df.special_trial == 0) &\
            (df.sound_len < rt_lim)
        xpoints, ypoints, _, mat, dic, mt_time, mt_time_err =\
            trajectory_thr(df.loc[indx_trajs], 'choice_x_coh', bins,
                           collapse_sides=True, thr=30, ax=ax[0], ax_traj=ax[1],
                           return_trash=True, error_kwargs=dict(marker='o'),
                           cmap='viridis', bintype='categorical',
                           trajectory=trajectory)
        ax[1].legend(labels=['-1', '-0.5', '-0.25', '0', '0.25', '0.5', '1'],
                     title='Coherence')
        ax[1].set_xlim([-50, 500])
        ax[1].set_xlabel('time from movement onset (MT, ms)')
        for i in [0, 30]:
            ax[1].axhline(i, ls=':', c='gray')
        ax[1].set_ylabel('y coord. (px)')
        ax[0].set_xlabel('ev. towards response')
        ax[0].set_ylabel('time to threshold (30px)')
        ax[0].plot(xpoints, ypoints, color='k', ls=':')
        ax[1].set_ylim([-10, 80])
        ax2 = ax[0].twinx()
        ax2.errorbar(xpoints, mt_time, mt_time_err, color='c', ls=':')
        ax2.set_label('Motor time')
        # velocities
        threshold = .2
        xpoints, ypoints, _, mat, dic, _, _ = trajectory_thr(
            df.loc[indx_trajs], 'choice_x_coh', bins, collapse_sides=True,
            thr=threshold, ax=ax[2], ax_traj=ax[3], return_trash=True,
            error_kwargs=dict(marker='o'), cmap='viridis',
            bintype='categorical', trajectory=velocity)
        # ax[3].legend(labels=['-1', '-0.5', '-0.25', '0', '0.25', '0.5', '1'],
        #              title='Coherence', loc='upper left')
        ax[3].set_xlim([-50, 500])
        ax[3].set_xlabel('time from movement onset (MT, ms)')
        ax[3].set_ylim([-0.05, 0.5])
        for i in [0, threshold]:
            ax[3].axhline(i, ls=':', c='gray')
        ax[3].set_ylabel('y coord velocity (px/ms)')
        ax[2].set_xlabel('ev. towards response')
        ax[2].set_ylabel(f'time to threshold ({threshold} px/ms)')
        ax[2].plot(xpoints, ypoints, color='k', ls=':')
        plt.show()
        if accel:
            # acceleration
            threshold = .0015
            xpoints, ypoints, _, mat, dic, _, _ = trajectory_thr(
                df.loc[indx_trajs], 'choice_x_coh', bins, collapse_sides=True,
                thr=threshold, ax=ax[4], ax_traj=ax[5], return_trash=True,
                error_kwargs=dict(marker='o'), cmap='viridis',
                bintype='categorical', trajectory=acceleration)
            # ax[3].legend(labels=['-1', '-0.5', '-0.25', '0', '0.25', '0.5', '1'],
            #              title='Coherence', loc='upper left')
            ax[5].set_xlim([-50, 500])
            ax[5].set_xlabel('time from movement onset (MT, ms)')
            ax[5].set_ylim([-0.003, 0.0035])
            for i in [0, threshold]:
                ax[5].axhline(i, ls=':', c='gray')
            ax[5].set_ylabel('y coord accelration (px/ms)')
            ax[4].set_xlabel('ev. towards response')
            ax[4].set_ylabel(f'time to threshold ({threshold} px/ms)')
            ax[4].plot(xpoints, ypoints, color='k', ls=':')
            plt.show()


def trajs_splitting(df, ax, rtbin=0, rtbins=np.linspace(0, 90, 2)):
    """
    Plot moment at which median trajectories for coh=0 and coh=1 split, for RTs
    between 0 and 90.


    Parameters
    ----------
    df : dataframe
        DESCRIPTION.
    rtbin : TYPE, optional
        DESCRIPTION. The default is 0.
    rtbins : TYPE, optional
        DESCRIPTION. The default is np.linspace(0, 90, 2).

    Raises
    ------
    NotImplementedError
        DESCRIPTION.

    Returns
    -------
    None.

    """
    for subject in df.subjid.unique():
        lbl = 'RTs: ['+str(rtbins[rtbin])+'-'+str(rtbins[rtbin+1])+']'
        simul.when_did_split_dat(df=df[df.subjid == subject], side=0,
                                 collapse_sides=True, ax=ax,
                                 rtbin=rtbin, rtbins=rtbins,
                                 plot_kwargs=dict(color='tab:green',
                                                  label=lbl))
        ax.set_xlim(-10, 140)
        ax.set_ylim(-5, 20)
        ax.set_xlabel('time from movement onset (ms)')
        ax.set_ylabel('y dimension (px)')
        ax.set_title(subject)
        ax.legend()
        plt.show()


def trajs_splitting_point(df, ax, collapse_sides=False, threshold=300,
                          sim=False,
                          rtbins=np.linspace(0, 150, 16), connect_points=True,
                          draw_line=((0, 90), (90, 0)),
                          trajectory="trajectory_y"):

    # split time/subject by coherence
    # threshold= bigger than that are turned to nan so it doesnt break figure range
    # this wont work if when_did_split_dat returns Nones instead of NaNs
    # plot will not work fine with uneven bins
    if sim:
        splitfun = simul.when_did_split_simul
    if not sim:
        splitfun = simul.when_did_split_dat
    out_data = []
    for subject in df.subjid.unique():
        for i in range(rtbins.size-1):
            if collapse_sides:
                current_split_index = splitfun(
                    df=df.loc[(df.special_trial == 0) & (df.subjid == subject)],
                    side=0,  # side has no effect because this is collapsing_sides
                    rtbin=i, rtbins=rtbins, collapse_sides=True,
                    trajectory=trajectory
                )
                out_data += [current_split_index]
            else:
                for j in [0, 1]:  # side values
                    current_split_index = splitfun(
                        df.loc[df.subjid == subject],
                        j,  # side has no effect because this is collapsing_sides
                        rtbin=i, rtbins=rtbins)
                    out_data += [current_split_index]

    # reshape out data so it makes sense. '0th dim=rtbin, 1st dim= n datapoints
    # ideally, make it NaN resilient
    out_data = np.array(out_data).reshape(
        df.subjid.unique().size, rtbins.size-1, -1)
    # set axes: rtbins, subject, sides
    out_data = np.swapaxes(out_data, 0, 1)

    # change the type so we can have NaNs
    out_data = out_data.astype(float)

    out_data[out_data > threshold] = np.nan

    binsize = rtbins[1]-rtbins[0]

    scatter_kws = {'color': (.6, .6, .6, .3), 'edgecolor': (.6, .6, .6, 1)}
    if collapse_sides:
        nrepeats = df.subjid.unique().size  # n subjects
    else:
        nrepeats = df.subjid.unique().size * 2  # two responses per subject
    # because we might want to plot each subject connecting lines, lets iterate
    # draw  datapoints
    if not connect_points:
        ax.scatter(  # add some offset/shift on x axis based on binsize
            binsize/2 + binsize * (np.repeat(
                np.arange(rtbins.size-1), nrepeats
            ) + np.random.normal(loc=0, scale=0.2, size=out_data.size)),  # jitter
            out_data.flatten(),
            **scatter_kws,
        )
    else:
        for i in range(df.subjid.unique().size):
            for j in range(out_data.shape[2]):
                ax.plot(
                    binsize/2 + binsize * np.arange(rtbins.size-1)
                    + np.random.normal(loc=0, scale=0.2, size=rtbins.size-1),
                    out_data[:, i, j],
                    marker='o', mfc=(.6, .6, .6, .3), mec=(.6, .6, .6, 1),
                    mew=1, color=(.6, .6, .6, .3)
                )

    error_kws = dict(ecolor='k', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='k', marker='o', label='mean & SEM')
    ax.errorbar(
        binsize/2 + binsize * np.arange(rtbins.size-1),
        # we do the mean across rtbin axis
        np.nanmean(out_data.reshape(rtbins.size-1, -1), axis=1),
        # other axes we dont care
        yerr=sem(out_data.reshape(rtbins.size-1, -1),
                 axis=1, nan_policy='omit'),
        **error_kws
    )
    if draw_line is not None:
        ax.plot(*draw_line, c='r', ls='--', zorder=0, label='slope -1')

    ax.set_xlabel('RT (ms)')
    ax.set_ylabel('time to split (ms)')
    ax.legend()
    plt.show()
# 3d histogram-like*?


def fig3_b(trajectories, motor_time, decision, com, coh, sound_len, traj_stamps,
           fix_onset, fixation_us=300000):
    'mean velocity and position for all trials'
    # interpolatespace = np.linspace(-700000, 1000000, 1701)
    ind_nocom = (~com.astype(bool))
    # *(motor_time < 400)*(np.abs(coh) == 1) *\
    #     (motor_time > 300)
    mean_position_array = np.empty((len(motor_time[ind_nocom]),
                                    max(motor_time)))
    mean_position_array[:] = np.nan
    mean_velocity_array = np.empty((len(motor_time[ind_nocom]), max(motor_time)))
    mean_velocity_array[:] = np.nan
    for i, traj in enumerate(trajectories[ind_nocom]):
        xvec = traj_stamps[i] - np.datetime64(fix_onset[i])
        xvec = (xvec -
                np.timedelta64(int(fixation_us + (sound_len[i]*1e3)),
                               "us")).astype(float)
        # yvec = traj
        # f = interpolate.interp1d(xvec, yvec, bounds_error=False)
        # out = f(interpolatespace)
        vel = np.diff(traj)
        mean_position_array[i, :len(traj)] = -traj*decision[i]
        mean_velocity_array[i, :len(vel)] = -vel*decision[i]
    mean_pos = np.nanmean(mean_position_array, axis=0)
    mean_vel = np.nanmean(mean_velocity_array, axis=0)
    std_pos = np.nanstd(mean_position_array, axis=0)
    fig, ax = plt.subplots(nrows=2)
    ax = ax.flatten()
    ax[0].plot(mean_pos)
    ax[0].fill_between(np.arange(len(mean_pos)), mean_pos + std_pos,
                       mean_pos - std_pos, alpha=0.4)
    ax[1].plot(mean_vel)


def tachometric_data(coh, hit, sound_len, ax, label='Data'):
    rm_top_right_lines(ax)
    df_plot_data = pd.DataFrame({'avtrapz': coh, 'hithistory': hit,
                                 'sound_len': sound_len})
    tachometric(df_plot_data, ax=ax, fill_error=True, cmap='gist_yarg')
    ax.axhline(y=0.5, linestyle='--', color='k', lw=0.5)
    ax.set_xlabel('RT (ms)')
    ax.set_ylabel('Accuracy')
    ax.set_title(label)
    ax.set_ylim(0.4, 1.04)
    # ax.legend([1, 0.5, 0.25, 0])
    return ax.get_position()


def reaction_time_histogram(sound_len, label, ax, bins=np.linspace(1, 301, 61),
                            pro_vs_re=None):
    rm_top_right_lines(ax)
    if label == 'Data':
        color = 'k'
    if label == 'Model':
        color = 'red'
        color_pro = 'coral'
        color_re = 'maroon'
        sound_len_pro = sound_len[pro_vs_re == 0]
        sound_len_re = sound_len[pro_vs_re == 1]
        ax.hist(sound_len_pro, bins=bins, alpha=0.3, density=False, linewidth=0.,
                histtype='stepfilled', label=label + '-pro', color=color_pro)
        ax.hist(sound_len_re, bins=bins, alpha=0.3, density=False, linewidth=0.,
                histtype='stepfilled', label=label + '-reac', color=color_re)
    ax.hist(sound_len, bins=bins, alpha=0.3, density=False, linewidth=0.,
            histtype='stepfilled', label=label, color=color)
    ax.set_xlabel("RT (ms)")
    ax.set_ylabel('Frequency')
    # ax.set_xlim(0, max(bins))


def pdf_cohs(sound_len, ax, coh, bins=np.linspace(1, 301, 61), yaxis=True):
    ev_vals = np.unique(np.abs(coh))
    colormap = pl.cm.gist_gray_r(np.linspace(0.2, 1, len(ev_vals)))
    for i_coh, ev in enumerate(ev_vals):
        index = np.abs(coh) == ev
        counts_coh, bins_coh = np.histogram(sound_len[index], bins=bins)
        norm_counts = counts_coh/sum(counts_coh)
        xvals = bins_coh[:-1]+(bins_coh[1]-bins_coh[0])/2
        ax.plot(xvals, norm_counts, color=colormap[i_coh])
    ax.set_xlabel('Reaction time (ms)')
    if yaxis:
        ax.set_ylabel('Density')


def express_performance(hit, coh, sound_len, pos_tach_ax, ax, label,
                        inset=False):
    " all rats..? "
    pos = pos_tach_ax
    rm_top_right_lines(ax)
    ev_vals = np.unique(np.abs(coh))
    accuracy = []
    error = []
    for ev in ev_vals:
        index = (coh == ev)*(sound_len < 90)
        accuracy.append(np.mean(hit[index]))
        error.append(np.sqrt(np.std(hit[index])/np.sum(index)))
    if inset:
        ax.set_position([pos.x0+2*pos.width/3, pos.y0+pos.height/9,
                         pos.width/3, pos.height/6])
    if label == 'Data':
        color = 'k'
    if label == 'Model':
        color = 'red'
    ax.errorbar(x=ev_vals, y=accuracy, yerr=error, color=color, fmt='-o',
                capsize=3, capthick=2, elinewidth=2, label=label)
    ax.set_xlabel('Coherence')
    ax.set_ylabel('Performance')
    ax.set_title('Express performance')
    ax.set_ylim(0.5, 1)
    ax.legend()


def cdfs(coh, sound_len, ax, f5, title='', linestyle='solid', label_title='',
         model=False):
    colors = ['k', 'darkred', 'darkorange', 'gold']
    index_1 = (sound_len <= 300)*(sound_len > 0)
    sound_len = sound_len[index_1]
    coh = coh[index_1]
    ev_vals = np.unique(np.abs(coh))
    for i, ev in enumerate(ev_vals):
        if f5:
            if ev == 0 or ev == 1:
                index = ev == np.abs(coh)
                hist_data, bins = np.histogram(sound_len[index], bins=200)
                cdf_vals = np.cumsum(hist_data)/np.sum(hist_data)
                xvals = bins[:-1]+(bins[1]-bins[0])/2
                if model:
                    x_interp = np.arange(0, 300, 10)
                    cdf_vals_interp = np.interp(x_interp, xvals, cdf_vals)
                    ax.plot(x_interp, cdf_vals_interp,
                            label=str(ev) + ' ' + label_title,
                            color=colors[i], linewidth=2, linestyle=linestyle)
                else:
                    ax.plot(xvals, cdf_vals,
                            label=str(ev) + ' ' + label_title,
                            color=colors[i], linewidth=2, linestyle=linestyle)
        else:
            index = ev == np.abs(coh)
            hist_data, bins = np.histogram(sound_len[index], bins=200)
            ax.plot(bins[:-1]+(bins[1]-bins[0])/2,
                    np.cumsum(hist_data)/np.sum(hist_data),
                    label=str(ev) + ' ' + label_title,
                    color=colors[i], linewidth=2, linestyle=linestyle)
    ax.set_xlabel('RT (ms)')
    ax.set_ylabel('CDF')
    ax.set_xlim(-1, 152)
    ax.legend(title='Coherence')
    ax.set_title(str(title))


def fig_1(coh, hit, sound_len, decision, zt, resp_len, trial_index, supt='',
          label='Data'):
    fig, ax = plt.subplots(ncols=3, nrows=2, figsize=(8, 4))
    ax = ax.flatten()
    for i in range(len(ax)):
        rm_top_right_lines(ax[i])
    if label == 'Data':
        color = 'k'
    if label == 'Model':
        color = 'red'
    psych_curve((decision+1)/2, coh, ret_ax=ax[0], kwargs_plot={'color': color},
                kwargs_error={'label': label, 'color': color})
    ax[0].set_xlabel('Coherence')
    ax[0].set_ylabel('Probability of right')
    pos_tach_ax = tachometric_data(coh=coh, hit=hit, sound_len=sound_len, ax=ax[1],
                                   label=label)
    # reaction_time_histogram(sound_len=sound_len, ax=ax[2], label=label)
    cdfs(coh=coh, sound_len=sound_len, f5=False, ax=ax[2], title='')
    express_performance(hit=hit, coh=coh, sound_len=sound_len, label=label,
                        pos_tach_ax=pos_tach_ax, ax=ax[3])
    fig.suptitle(supt)
    # decision_s = decision
    decision_01 = (decision+1)/2
    # TODO: fix issue with heatmap: only half of first and last row is displayed
    edd2.com_heatmap_jordi(zt, coh, decision_01, ax=ax[4], flip=True,
                           annotate=False, xlabel='prior', ylabel='avg stim',
                           cmap='PRGn_r')
    ax[4].set_title('Pright')
    edd2.com_heatmap_jordi(zt, coh, hit, ax=ax[5], flip=True, xlabel='prior',
                           annotate=False, ylabel='avg stim ', cmap='coolwarm')
    ax[5].set_title('Pcorrect')
    fig.savefig(SV_FOLDER+'/Fig1.png', dpi=400, bbox_inches='tight')
    fig.savefig(SV_FOLDER+'/Fig1.svg', dpi=400, bbox_inches='tight')


def fig_1_def(df_data):
    f, ax = plt.subplots(nrows=2, ncols=4, figsize=(8, 5))  # figsize=(4, 3))
    ax = ax.flatten()
    ax[0].axis('off')
    ax[1].axis('off')
    matrix_figure(df_data, ax_tach=ax[3], ax_pright=ax[2],
                  ax_mat=[ax[6], ax[7]], humans=False)
    plot_coms(df=df_data, ax=ax[5])
    # ax_trck = plt.axes([.8, .55, .17, .17])
    ax_trck = ax[4]
    tracking_image(ax_trck)
    f.savefig(SV_FOLDER+'fig1.svg', dpi=400, bbox_inches='tight')


def fig_1_mt_weights(df, plot=False):
    w_coh = []
    w_t_i = []
    w_zt = []
    for subject in df.subjid.unique():
        df_1 = df.loc[df.subjid == subject]
        resp_len = np.array(df_1.resp_len)
        decision = np.array(df_1.R_response)*2 - 1
        coh = np.array(df_1.coh2)
        trial_index = np.array(df_1.origidx)
        zt = np.nansum(df_1[["dW_lat", "dW_trans"]].values, axis=1)
        params = mt_linear_reg(mt=resp_len, coh=coh*decision/max(np.abs(coh)),
                               trial_index=trial_index/max(trial_index),
                               prior=zt*decision/max(np.abs(zt)), plot=False)
        w_coh.append(params[1])
        w_t_i.append(params[2])
        w_zt.append(params[3])
    mean_1 = np.nanmean(w_coh)
    mean_2 = np.nanmean(w_t_i)
    mean_3 = np.nanmean(w_zt)
    std_1 = np.nanstd(w_coh)/np.sqrt(len(w_coh))
    std_2 = np.nanstd(w_t_i)/np.sqrt(len(w_t_i))
    std_3 = np.nanstd(w_zt)/np.sqrt(len(w_zt))
    errors = [std_1, std_2, std_3]
    means = [mean_1, mean_2, mean_3]
    if plot:
        fig, ax = plt.subplots(figsize=(3, 2))
        # TODO: not the most informative name for a function
        plot_bars(means=means, errors=errors, ax=ax)
        rm_top_right_lines(ax=ax)
        fig.savefig(SV_FOLDER+'/Fig1_mt_weights.png', dpi=400, bbox_inches='tight')
        fig.savefig(SV_FOLDER+'/Fig1_mt_weights.svg', dpi=400, bbox_inches='tight')

    return means, errors


def plot_bars(means, errors, ax, f5=False, means_model=None, errors_model=None,
              width=0.35):
    labels = ['Stimulus Congruency', 'Trial index', 'Prior Congruency']
    if not f5:
        ax.bar(x=labels, height=means, yerr=errors, capsize=3, color='k',
               ecolor='blue')
        ax.set_ylabel('Weight (a.u.)')
    if f5:
        x = np.arange(len(labels))
        ax.bar(x=x-width/2, height=means, yerr=errors, width=width,
               capsize=3, color='k', label='Data', ecolor='blue')
        ax.bar(x=x+width/2, height=means_model, yerr=errors_model, width=width,
               capsize=3, color='red', label='Model')
        ax.set_ylabel('Weight (a.u.)')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()


def fig_5_in(coh, hit, sound_len, decision, hit_model, sound_len_model, zt,
             decision_model, com, com_model, com_model_detected, pro_vs_re):
    """
    Deprecated
    """
    fig, ax = plt.subplots(ncols=4, nrows=3, gridspec_kw={'top': 0.95,
                                                          'bottom': 0.055,
                                                          'left': 0.055,
                                                          'right': 0.975,
                                                          'hspace': 0.38,
                                                          'wspace': 0.225})
    ax = ax.flatten()
    for ax_1 in ax:
        rm_top_right_lines(ax_1)
    psych_curve((decision+1)/2, coh, ret_ax=ax[1], kwargs_plot={'color': 'k'},
                kwargs_error={'label': 'Data', 'color': 'k'})
    ax[1].set_xlabel('Coherence')
    ax[1].set_ylabel('Probability of right')
    hit_model = hit_model[sound_len_model >= 0]
    com_model_detected = com_model_detected[sound_len_model >= 0]
    decision_model = decision_model[sound_len_model >= 0]
    com_model = com_model[sound_len_model >= 0]
    psych_curve((decision_model+1)/2, coh[sound_len_model >= 0], ret_ax=ax[1],
                kwargs_error={'label': 'Model', 'color': 'red'},
                kwargs_plot={'color': 'red'})
    ax[1].legend()
    pos_tach_ax = tachometric_data(coh=coh, hit=hit, sound_len=sound_len, ax=ax[2])
    ax[2].set_title('Data')
    pos_tach_ax_model = tachometric_data(coh=coh[sound_len_model >= 0],
                                         hit=hit_model,
                                         sound_len=sound_len_model[
                                             sound_len_model >= 0],
                                         ax=ax[3])
    ax[3].set_title('Model')
    reaction_time_histogram(sound_len=sound_len, label='Data', ax=ax[0],
                            bins=np.linspace(-150, 300, 91))
    reaction_time_histogram(sound_len=sound_len_model[sound_len_model >= 0],
                            label='Model', ax=ax[0],
                            bins=np.linspace(-150, 300, 91), pro_vs_re=pro_vs_re)
    ax[0].legend()
    express_performance(hit=hit, coh=coh, sound_len=sound_len,
                        pos_tach_ax=pos_tach_ax, ax=ax[4], label='Data')
    express_performance(hit=hit_model, coh=coh[sound_len_model >= 0],
                        sound_len=sound_len_model[sound_len_model >= 0],
                        pos_tach_ax=pos_tach_ax_model, ax=ax[4], label='Model')
    df_plot = pd.DataFrame({'com': com[sound_len_model >= 0],
                            'sound_len': sound_len[sound_len_model >= 0],
                            'rt_model': sound_len_model[sound_len_model >= 0],
                            'com_model': com_model,
                            'com_model_detected': com_model_detected})
    binned_curve(df_plot, 'com', 'sound_len', bins=BINS_RT, xpos=xpos_RT,
                 errorbar_kw={'label': 'Data', 'color': 'k'}, ax=ax[5])
    binned_curve(df_plot, 'com_model_detected', 'rt_model', bins=BINS_RT,
                 xpos=xpos_RT, errorbar_kw={'label': 'Model detected',
                                            'color': 'red'}, ax=ax[5])
    binned_curve(df_plot, 'com_model', 'rt_model', bins=BINS_RT, xpos=xpos_RT,
                 errorbar_kw={'label': 'Model all', 'color': 'green'}, ax=ax[5])
    ax[5].legend()
    ax[5].set_xlabel('RT (ms)')
    ax[5].set_ylabel('PCoM')
    binned_curve(df_plot, 'com', 'sound_len', bins=BINS_RT, xpos=xpos_RT,
                 errorbar_kw={'label': 'Data', 'color': 'k'}, ax=ax[6])
    binned_curve(df_plot, 'com_model_detected', 'rt_model', bins=BINS_RT,
                 xpos=xpos_RT, errorbar_kw={'label': 'Model detected',
                                            'color': 'red'}, ax=ax[6])
    ax[6].legend()
    ax[6].set_xlabel('RT (ms)')
    ax[6].set_ylabel('PCoM')
    decision_01 = (decision+1)/2
    edd2.com_heatmap_jordi(zt, coh, decision_01, ax=ax[8], flip=True,
                           annotate=False, xlabel='prior', ylabel='avg stim',
                           cmap='PRGn_r', vmin=0., vmax=1)
    cdfs(coh, sound_len, f5=True, ax=ax[7], label_title='Data', linestyle='solid')
    cdfs(coh, sound_len_model, f5=True, ax=ax[7], label_title='Model',
         linestyle='--', model=True)
    ax[8].set_title('Pright Data')
    zt_model = zt[sound_len_model >= 0]
    coh_model = coh[sound_len_model >= 0]
    decision_01_model = (decision_model+1)/2
    edd2.com_heatmap_jordi(zt_model, coh_model, decision_01_model, ax=ax[9],
                           flip=True, annotate=False, xlabel='prior',
                           ylabel='avg stim', cmap='PRGn_r', vmin=0., vmax=1)
    ax[9].set_title('Pright Model')
    edd2.com_heatmap_jordi(zt, coh, hit, ax=ax[10],
                           flip=True, xlabel='prior', annotate=False,
                           ylabel='avg stim', cmap='coolwarm', vmin=0.2, vmax=1)
    ax[10].set_title('Pcorrect Data')
    edd2.com_heatmap_jordi(zt_model, coh_model, hit_model, ax=ax[11],
                           flip=True, xlabel='prior', annotate=False,
                           ylabel='avg stim', cmap='coolwarm', vmin=0.2, vmax=1)
    ax[11].set_title('Pcorrect Model')
    df_data = pd.DataFrame({'avtrapz': coh, 'CoM_sugg': com,
                            'norm_allpriors': zt/max(abs(zt)),
                            'R_response': (decision+1)/2})
    com_heatmap_paper_marginal_pcom_side(df_data, side=0)
    com_heatmap_paper_marginal_pcom_side(df_data, side=1)
    # matrix_data, _ = edd2.com_heatmap_jordi(zt, coh, com,
    #                                         return_mat=True, flip=True)
    # matrix_model, _ = edd2.com_heatmap_jordi(zt, coh, com_model,
    #                                          return_mat=True, flip=True)
    # sns.heatmap(matrix_data, ax=ax[8])
    # ax[8].set_title('Data')
    # sns.heatmap(matrix_model, ax=ax[9])
    # ax[9].set_title('Model')
    df_model = pd.DataFrame({'avtrapz': coh[sound_len_model >= 0],
                             'CoM_sugg':
                                 com_model_detected,
                             'norm_allpriors':
                                 zt_model/max(abs(zt_model)),
                             'R_response': (decision_model+1)/2})
    com_heatmap_paper_marginal_pcom_side(df_model, side=0)
    com_heatmap_paper_marginal_pcom_side(df_model, side=1)


def com_heatmap_marginal_pcom_side_mat(
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


def fig_5(coh, hit, sound_len, decision, hit_model, sound_len_model, zt,
          decision_model, com, com_model, com_model_detected, pro_vs_re,
          df_sim, means, errors, means_model, errors_model):
    fig, ax = plt.subplots(ncols=4, nrows=4, gridspec_kw={'top': 0.95,
                                                          'bottom': 0.055,
                                                          'left': 0.055,
                                                          'right': 0.975,
                                                          'hspace': 0.38,
                                                          'wspace': 0.225})
    ax = ax.flatten()
    for ax_1 in ax:
        rm_top_right_lines(ax_1)
    hit_model = hit_model[sound_len_model >= 0]
    com_model_detected = com_model_detected[sound_len_model >= 0]
    decision_model = decision_model[sound_len_model >= 0]
    com_model = com_model[sound_len_model >= 0]
    _ = tachometric_data(coh=coh[sound_len_model >= 0], hit=hit_model,
                         sound_len=sound_len_model[sound_len_model >= 0],
                         ax=ax[2], label='Model')
    pdf_cohs(sound_len=sound_len, ax=ax[0], coh=coh, yaxis=True)
    pdf_cohs(sound_len=sound_len_model[sound_len_model >= 0], ax=ax[1],
             coh=coh[sound_len_model >= 0], yaxis=False)
    ax[0].set_title('Data')
    ax[1].set_title('Model')
    df_plot = pd.DataFrame({'com': com[sound_len_model >= 0],
                            'sound_len': sound_len[sound_len_model >= 0],
                            'rt_model': sound_len_model[sound_len_model >= 0],
                            'com_model': com_model,
                            'com_model_detected': com_model_detected})
    binned_curve(df_plot, 'com', 'sound_len', bins=BINS_RT, xpos=xpos_RT,
                 errorbar_kw={'label': 'Data', 'color': 'k'}, ax=ax[4])
    binned_curve(df_plot, 'com_model_detected', 'rt_model', bins=BINS_RT,
                 xpos=xpos_RT, errorbar_kw={'label': 'Model detected',
                                            'color': 'red'}, ax=ax[4])
    binned_curve(df_plot, 'com_model', 'rt_model', bins=BINS_RT, xpos=xpos_RT,
                 errorbar_kw={'label': 'Model all', 'color': 'green'}, ax=ax[4])
    ax[4].xaxis.tick_top()
    ax[4].xaxis.tick_bottom()
    ax[4].legend()
    ax[4].set_xlabel('RT (ms)')
    ax[4].set_ylabel('PCoM')
    zt_model = zt[sound_len_model >= 0]
    coh_model = coh[sound_len_model >= 0]
    decision_01_model = (decision_model+1)/2
    edd2.com_heatmap_jordi(zt_model, coh_model, decision_01_model, ax=ax[3],
                           flip=True, annotate=False, xlabel='prior',
                           ylabel='avg stim', cmap='PRGn_r', vmin=0., vmax=1)
    ax[3].set_title('Pright Model')
    df_model = pd.DataFrame({'avtrapz': coh[sound_len_model >= 0],
                             'CoM_sugg':
                                 com_model_detected,
                             'norm_allpriors':
                                 zt_model/max(abs(zt_model)),
                             'R_response': (decision_model+1)/2})
    nbins = 7
    matrix_side_0 = com_heatmap_marginal_pcom_side_mat(df=df_model, side=0)
    matrix_side_1 = com_heatmap_marginal_pcom_side_mat(df=df_model, side=1)
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
    ax[5].set_title(pcomlabel_1)
    im = ax[5].imshow(matrix_side_1, vmin=0, vmax=vmax)
    plt.sca(ax[5])
    plt.colorbar(im, fraction=0.04)
    pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
    ax[6].set_title(pcomlabel_0)
    im = ax[6].imshow(matrix_side_0, vmin=0, vmax=vmax)
    ax[6].yaxis.set_ticks_position('none')
    plt.sca(ax[6])
    plt.colorbar(im, fraction=0.04)
    for ax_i in [ax[5], ax[6]]:
        ax_i.set_xlabel('Prior Evidence')
        ax_i.set_yticklabels(['']*nbins)
        ax_i.set_xticklabels(['']*nbins)
    ax[5].set_ylabel('Stimulus Evidence')
    plot_bars(means=means, errors=errors, ax=ax[7], f5=True,
              means_model=means_model, errors_model=errors_model)
    ax_pr = [ax[i] for i in [8, 12, 9, 13]]
    traj_cond_coh_simul(df_sim=df_sim, ax=ax_pr, median=False, prior=True)
    ax_coh = [ax[i] for i in [10, 14, 11, 15]]
    traj_cond_coh_simul(df_sim=df_sim, ax=ax_coh, median=False, prior=False)


def traj_model_plot(df_sim):
    fgsz = (8, 8)
    inset_sz = 0.1
    f, ax = plt.subplots(nrows=2, ncols=2, figsize=fgsz)
    ax = ax.flatten()
    ax_cohs = np.array([ax[0], ax[2]])
    ax_inset = add_inset(ax=ax_cohs[0], inset_sz=inset_sz, fgsz=fgsz)
    ax_cohs = np.insert(ax_cohs, 0, ax_inset)
    ax_inset = add_inset(ax=ax_cohs[2], inset_sz=inset_sz, fgsz=fgsz,
                         marginy=0.15)
    ax_cohs = np.insert(ax_cohs, 2, ax_inset)
    # trajs_cond_on_coh(df_sim, ax=ax)
    simul.whole_splitting(df=df_sim, ax=ax[1], simul=True)
    ax[1].set_xlim(-10, 200)
    ax[1].set_ylim(-20, 20)
    trajs_splitting_point(df=df_sim, ax=ax[3], sim=True)
    trajs_cond_on_coh(df=df_sim, ax=ax_cohs)


def traj_cond_coh_simul(df_sim, ax=None, median=True, prior=True, traj_thr=30,
                        vel_thr=0.2):
    # TODO: save each matrix? or save the mean and std
    if median:
        func_final = np.nanmedian
    if not median:
        func_final = np.nanmean
    nanidx = df_sim.loc[df_sim[['dW_trans',
                                'dW_lat']].isna().sum(axis=1) == 2].index
    df_sim['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df_sim.loc[nanidx, 'allpriors'] = np.nan
    df_sim['choice_x_coh'] = (df_sim.R_response*2-1) * df_sim.coh2
    bins_coh = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]
    bins_zt = [-1, -0.6, -0.15, 0.15, 0.6, 1]
    xvals_zt = [-1, -0.5, 0, 0.5, 1]
    signed_response = df_sim.R_response.values
    df_sim['normallpriors'] = df_sim['allpriors'] /\
        np.nanmax(df_sim['allpriors'].abs())*(signed_response*2 - 1)
    lens = []
    if ax is None:
        fig, ax = plt.subplots(nrows=2, ncols=2)
        ax = ax.flatten()
    vals_thr_traj = []
    vals_thr_vel = []
    labels_zt = ['inc. high', 'inc. low', 'zero', 'con. low', 'con. high']
    if prior:
        bins_ref = bins_zt
    else:
        bins_ref = bins_coh
    for i_ev, ev in enumerate(bins_ref):
        if not prior:
            index = (df_sim.choice_x_coh.values == ev) *\
                (df_sim.R_response.values == 1)
            colormap = pl.cm.viridis(np.linspace(0, 1, len(bins_coh)))
        if prior:
            if ev == 1:
                break
            index = (df_sim.normallpriors.values >= bins_zt[i_ev]) *\
                (df_sim.normallpriors.values < bins_zt[i_ev + 1]) *\
                (df_sim.R_response.values == 1)
            colormap = pl.cm.viridis(np.linspace(0, 1, len(bins_zt)-1))
            # (df_sim.R_response.values == 1) *\
        lens.append(max([len(t) for t in df_sim.trajectory_y[index].values]))
        traj_all = np.empty((sum(index), max(lens)))
        traj_all[:] = np.nan
        vel_all = np.empty((sum(index), max(lens)))
        vel_all[:] = np.nan
        for tr in range(sum(index)):
            vals_traj = df_sim.traj[index].values[tr] *\
                (signed_response[index][tr]*2 - 1)
            vals_vel = df_sim.traj_d1[index].values[tr] *\
                (signed_response[index][tr]*2 - 1)
            traj_all[tr, :len(vals_traj)] = vals_traj
            vel_all[tr, :len(vals_vel)] = vals_vel
        mean_traj = func_final(traj_all, axis=0)
        std_traj = np.nanstd(traj_all, axis=0) / np.sqrt(sum(index))
        # val_traj = np.argmax(mean_traj >= traj_thr)
        val_traj = np.mean(df_sim['resp_len'].values[index])*1e3
        if prior:
            xval = xvals_zt[i_ev]
        else:
            xval = ev
        ax[2].scatter(xval, val_traj, color=colormap[i_ev], marker='D', s=60)
        vals_thr_traj.append(val_traj)
        mean_vel = func_final(vel_all, axis=0)
        std_vel = np.nanstd(vel_all, axis=0) / np.sqrt(sum(index))
        val_vel = np.argmax(mean_vel >= vel_thr)
        ax[3].scatter(xval, val_vel, color=colormap[i_ev], marker='D', s=60)
        vals_thr_vel.append(val_vel)
        if not prior:
            label = '{}'.format(ev)
        if prior:
            label = labels_zt[i_ev]
        ax[0].plot(np.arange(len(mean_traj)), mean_traj, label=label,
                   color=colormap[i_ev])
        ax[0].fill_between(x=np.arange(len(mean_traj)),
                           y1=mean_traj - std_traj, y2=mean_traj + std_traj,
                           color=colormap[i_ev])
        ax[1].plot(np.arange(len(mean_vel)), mean_vel, label=label,
                   color=colormap[i_ev])
        ax[1].fill_between(x=np.arange(len(mean_vel)),
                           y1=mean_vel - std_vel, y2=mean_vel + std_vel,
                           color=colormap[i_ev])
    ax[0].axhline(y=30, linestyle='--', color='k', alpha=0.4)
    ax[1].axhline(y=0.2, linestyle='--', color='k', alpha=0.4)
    if prior:
        leg_title = 'prior congruency'
        ax[2].plot(xvals_zt, vals_thr_traj, color='k', linestyle='--',
                   alpha=0.6)
        ax[3].plot(xvals_zt, vals_thr_vel, color='k', linestyle='--',
                   alpha=0.6)
        ax[2].set_xlabel('Prior congruency', fontsize=10)
        ax[3].set_xlabel('Prior congruency', fontsize=10)
    if not prior:
        leg_title = 'stim congruency'
        ax[2].plot(bins_coh, vals_thr_traj, color='k', linestyle='--', alpha=0.6)
        ax[3].plot(bins_coh, vals_thr_vel, color='k', linestyle='--', alpha=0.6)
        ax[2].set_xlabel('Evidence congruency', fontsize=10)
        ax[3].set_xlabel('Evidence congruency', fontsize=10)
    ax[0].legend(title=leg_title)
    ax[0].set_ylabel('y-coord (px)', fontsize=10)
    ax[0].set_xlabel('Time from movement onset (ms)', fontsize=10)
    ax[0].set_title('Mean trajectory', fontsize=10)
    ax[1].legend(title=leg_title)
    ax[1].set_ylabel('Velocity (px/s)', fontsize=10)
    ax[1].set_xlabel('Time from movement onset (ms)', fontsize=10)
    ax[1].set_title('Mean velocity', fontsize=10)
    ax[2].set_ylabel('MT (ms)', fontsize=10)
    ax[3].set_ylabel('Time to reach threshold (ms)', fontsize=10)


def supp_trajs_prior_cong(df_sim, ax=None):
    signed_response = df_sim.R_response.values
    nanidx = df_sim.loc[df_sim[['dW_trans',
                                'dW_lat']].isna().sum(axis=1) == 2].index
    df_sim['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df_sim.loc[nanidx, 'allpriors'] = np.nan
    df_sim['normallpriors'] = df_sim['allpriors'] /\
        np.nanmax(df_sim['allpriors'].abs())*(signed_response*2 - 1)
    if ax is None:
        fig, ax = plt.subplots(1)
    bins_zt = [0.6, 1]
    lens = []
    for i_ev, ev in enumerate(bins_zt):
        if ev == 1:
            break
        index = (df_sim.normallpriors.values >= bins_zt[i_ev]) *\
            (df_sim.normallpriors.values < bins_zt[i_ev + 1])
        lens.append(max([len(t) for t in df_sim.trajectory_y[index].values]))
        traj_all = np.empty((sum(index), max(lens)))
        traj_all[:] = np.nan
        for tr in range(sum(index)):
            vals_traj = df_sim.traj[index].values[tr] *\
                (signed_response[index][tr]*2 - 1)
            traj_all[tr, :len(vals_traj)] = vals_traj
            ax.plot(vals_traj, color='k', alpha=0.4)
        mean_traj = np.nanmean(traj_all, axis=0)
    ax.plot(np.arange(len(mean_traj)), mean_traj, label='Mean', color='yellow',
            linewidth=4)
    ax.set_ylabel('y-coord (px)', fontsize=10)
    ax.set_xlabel('Time from movement onset (ms)', fontsize=10)


def human_trajs(user_id, sv_folder, nm='300', max_mt=600, jitter=0.003,
                wanted_precision=8, traj_thr=240, vel_thr=2):
    if user_id == 'Alex':
        folder = 'C:\\Users\\Alexandre\\Desktop\\CRM\\Human\\80_20\\'+nm+'ms\\'
    if user_id == 'AlexCRM':
        folder = 'C:/Users/agarcia/Desktop/CRM/human/'
    if user_id == 'Manuel':
        folder =\
            '/home/molano/Dropbox/project_Barna/psycho_project/80_20/'+nm+'ms/'
    subj = ['general_traj']
    steps = [None]
    df_data = ah.traj_analysis(data_folder=folder,
                               subjects=subj, steps=steps, name=nm,
                               sv_folder=sv_folder)
    df_data.avtrapz /= max(abs(df_data.avtrapz))
    coh = df_data.avtrapz.values
    decision = df_data.R_response.values
    trajs = df_data.trajectory_y.values
    times = df_data.times.values
    ev_vals = np.unique(np.abs(np.round(coh, 2)))
    bins = [0, 0.25, 0.5, 1]
    congruent_coh = coh * (decision*2 - 1)
    fig, ax = plt.subplots(nrows=2, ncols=2)
    ax = ax.flatten()
    colormap = pl.cm.viridis(np.linspace(0, 1, len(ev_vals)))
    vals_thr_traj = []
    vals_thr_vel = []
    for i_ev, ev in enumerate(ev_vals):
        index = np.abs(np.round(congruent_coh, 2)) == ev
        all_trajs = np.empty((sum(index), max_mt))
        all_trajs[:] = np.nan
        all_vels = np.empty((sum(index), max_mt))
        all_vels[:] = np.nan
        for tr in range(sum(index)):
            vals = np.array(trajs[index][tr]) * (decision[index][tr]*2 - 1)
            ind_time = [True if t != '' else False for t in times[index][tr]]
            time = np.array(times[index][tr])[np.array(ind_time)].astype(float)
            max_time = max(time)*1e3
            if max_time > max_mt:
                continue
            vals_fin = np.interp(np.arange(0, int(max_time), wanted_precision),
                                 xp=time*1e3, fp=vals)
            vels_fin = np.diff(vals_fin)/wanted_precision
            all_trajs[tr, :len(vals_fin)] = vals_fin - vals_fin[0]
            all_vels[tr, :len(vels_fin)] = vels_fin
        mean_traj = np.nanmean(all_trajs, axis=0)
        std_traj = np.sqrt(np.nanstd(all_trajs, axis=0) / sum(index))
        val_traj = np.where(mean_traj >= traj_thr)[0][2]*wanted_precision
        vals_thr_traj.append(val_traj)
        ax[2].scatter(ev, val_traj, color=colormap[i_ev], marker='D', s=60)
        mean_vel = np.nanmean(all_vels, axis=0)
        std_vel = np.sqrt(np.nanstd(all_vels, axis=0) / sum(index))
        for ind_v, velocity in enumerate(mean_vel):
            if velocity >= vel_thr and ind_v*wanted_precision >= 160:
                val_vel = ind_v*wanted_precision
                break
        vals_thr_vel.append(val_vel)
        ax[3].scatter(ev, val_vel, color=colormap[i_ev], marker='D', s=60)
        ax[0].plot(np.arange(len(mean_traj))*wanted_precision, mean_traj,
                   color=colormap[i_ev], label='{}'.format(bins[i_ev]))
        ax[0].fill_between(x=np.arange(len(mean_traj))*wanted_precision,
                           y1=mean_traj-std_traj, y2=mean_traj+std_traj,
                           color=colormap[i_ev])
        ax[1].plot(np.arange(len(mean_vel))*wanted_precision, mean_vel,
                   color=colormap[i_ev], label='{}'.format(bins[i_ev]))
        ax[1].fill_between(x=np.arange(len(mean_vel))*wanted_precision,
                           y1=mean_vel-std_vel, y2=mean_vel+std_vel,
                           color=colormap[i_ev])
    ax[2].plot(bins, vals_thr_traj, color='k', linestyle='--', alpha=0.6)
    ax[3].plot(bins, vals_thr_vel, color='k', linestyle='--', alpha=0.6)
    ax[0].set_xlim(-0.1, 550)
    ax[1].set_xlim(-0.1, 550)
    ax[1].set_ylim(1, 4)
    ax[0].axhline(y=traj_thr, linestyle='--', color='k', alpha=0.4)
    ax[1].axhline(y=vel_thr, linestyle='--', color='k', alpha=0.4)
    ax[0].legend(title='stimulus')
    ax[0].set_ylabel('y-coord (px)')
    ax[0].set_xlabel('Time from movement onset (ms)')
    ax[0].set_title('Mean trajectory')
    ax[1].legend(title='stimulus')
    ax[1].set_ylabel('Velocity (px/s)')
    ax[1].set_xlabel('Time from movement onset (ms)')
    ax[1].set_title('Mean velocity')
    ax[2].set_xlabel('Evidence congruency')
    ax[2].set_ylabel('Time to reach threshold (ms)')
    ax[3].set_xlabel('Evidence congruency')
    ax[3].set_ylabel('Time to reach threshold (ms)')


def accuracy_1st_2nd_ch(gt, decision, coh, com):  # ??
    coh_com = coh[com]
    gt_com = gt[com]
    decision_com = decision[com]
    ev_vals = np.unique(np.abs(coh_com))
    acc_ch1 = []
    acc_ch2 = []
    for ev in ev_vals:
        index = np.abs(coh_com) == ev
        acc_ch1.append(np.mean((-decision_com[index]) == gt_com[index]))
        acc_ch2.append(np.mean(decision_com[index] == gt_com[index]))


def linear_fun(x, a, b, c, d):
    return a + b*x[0] + c*x[1] + d*x[2]


def mt_linear_reg(mt, coh, trial_index, prior, plot=False):
    """

    Parameters
    ----------
    mt : array
        DESCRIPTION.
    coh : array (abs)
        DESCRIPTION.
    trial_index : array
        DESCRIPTION.
    prior : array (abs)
        congruent prior with final decision.

    Returns
    -------
    popt : TYPE
        DESCRIPTION.

    """
    trial_index = trial_index.astype(float)
    xdata = np.array([[coh], [trial_index], [prior]]).reshape(3, len(prior))
    ydata = np.array(mt*1e3)
    popt, pcov = curve_fit(f=linear_fun, xdata=xdata, ydata=ydata)
    if plot:
        df = pd.DataFrame({'coh': coh/max(coh), 'prior': prior/max(prior),
                           'MT': resp_len*1e3,
                           'trial_index': trial_index/max(trial_index)})
        plt.figure()
        sns.pointplot(data=df, x='coh', y='MT', label='coh')
        sns.pointplot(data=df, x='prior', y='MT', label='prior')
        sns.pointplot(data=df, x='trial_index', y='MT', label='trial_index')
        plt.ylabel('MT (ms)')
        plt.xlabel('normalized variables')
        plt.legend()
    return popt


def basic_statistics(decision, resp_fin):
    mat = confusion_matrix(decision, resp_fin)
    print(mat)
    fpr, tpr, _ = roc_curve(resp_fin, decision)
    RocCurveDisplay(fpr=fpr, tpr=tpr).plot()


def run_model(stim, zt, coh, gt, trial_index, num_tr=None):
    if num_tr is not None:
        num_tr = num_tr
    else:
        num_tr = int(len(zt))
    data_augment_factor = 10
    MT_slope = 0.123
    MT_intercep = 254
    detect_CoMs_th = 5
    p_t_aff = 8
    p_t_eff = 8
    p_t_a = 14  # 90 ms (18) PSIAM fit includes p_t_eff
    p_w_zt = 0.2
    p_w_stim = 0.11
    p_e_noise = 0.02
    p_com_bound = 0.
    p_w_a_intercept = 0.052
    p_w_a_slope = -2.2e-05  # fixed
    p_a_noise = 0.04  # fixed
    p_1st_readout = 10
    p_2nd_readout = 10

    stim = edd2.data_augmentation(stim=stim.reshape(20, num_tr),
                                  daf=data_augment_factor)
    stim_res = 50/data_augment_factor
    compute_trajectories = True
    all_trajs = True
    conf = [p_w_zt, p_w_stim, p_e_noise, p_com_bound, p_t_aff,
            p_t_eff, p_t_a, p_w_a_intercept, p_w_a_slope, p_a_noise, p_1st_readout,
            p_2nd_readout]
    jitters = len(conf)*[0]
    print('Number of trials: ' + str(stim.shape[1]))
    p_w_zt = conf[0]+jitters[0]*np.random.rand()
    p_w_stim = conf[1]+jitters[1]*np.random.rand()
    p_e_noise = conf[2]+jitters[2]*np.random.rand()
    p_com_bound = conf[3]+jitters[3]*np.random.rand()
    p_t_aff = int(round(conf[4]+jitters[4]*np.random.rand()))
    p_t_eff = int(round(conf[5]++jitters[5]*np.random.rand()))
    p_t_a = int(round(conf[6]++jitters[6]*np.random.rand()))
    p_w_a_intercept = conf[7]+jitters[7]*np.random.rand()
    p_w_a_slope = conf[8]+jitters[8]*np.random.rand()
    p_a_noise = conf[9]+jitters[9]*np.random.rand()
    p_1st_readout = conf[10]+jitters[10]*np.random.rand()
    p_2nd_readout = conf[11]+jitters[11]*np.random.rand()
    stim_temp =\
        np.concatenate((stim, np.zeros((int(p_t_aff+p_t_eff),
                                        stim.shape[1]))))
    # TODO: get in a dict
    E, A, com_model, first_ind, second_ind, resp_first, resp_fin,\
        pro_vs_re, matrix, total_traj, init_trajs, final_trajs,\
        frst_traj_motor_time, x_val_at_updt, xpos_plot, median_pcom,\
        rt_vals, rt_bins, tr_index =\
        edd2.trial_ev_vectorized(zt=zt, stim=stim_temp, coh=coh,
                                 trial_index=trial_index,
                                 MT_slope=MT_slope, MT_intercep=MT_intercep,
                                 p_w_zt=p_w_zt, p_w_stim=p_w_stim,
                                 p_e_noise=p_e_noise, p_com_bound=p_com_bound,
                                 p_t_aff=p_t_aff, p_t_eff=p_t_eff, p_t_a=p_t_a,
                                 num_tr=num_tr, p_w_a_intercept=p_w_a_intercept,
                                 p_w_a_slope=p_w_a_slope,
                                 p_a_noise=p_a_noise,
                                 p_1st_readout=p_1st_readout,
                                 p_2nd_readout=p_2nd_readout,
                                 compute_trajectories=compute_trajectories,
                                 stim_res=stim_res, all_trajs=all_trajs)
    hit_model = resp_fin == gt
    reaction_time = (first_ind[tr_index]-int(300/stim_res) + p_t_eff)*stim_res
    detected_com = np.abs(x_val_at_updt) > detect_CoMs_th
    return hit_model, reaction_time, detected_com, resp_fin, com_model,\
        pro_vs_re, total_traj


# ---MAIN
if __name__ == '__main__':
    plt.close('all')
    all_rats = True
    if all_rats:
        subjects = ['LE42', 'LE43', 'LE38', 'LE39', 'LE85', 'LE84', 'LE45', 'LE40',
                    'LE46', 'LE86', 'LE47', 'LE37', 'LE41', 'LE36', 'LE44']
    else:
        subjects = ['LE43']
    df_all = pd.DataFrame()
    for sbj in subjects:
        df = edd2.get_data_and_matrix(dfpath=DATA_FOLDER + sbj, return_df=True,
                                      sv_folder=SV_FOLDER, after_correct=True,
                                      silent=True, all_trials=True)
        if all_rats:
            df_all = pd.concat((df_all, df))
    if all_rats:
        df = df_all
    after_correct_id = np.where((df.aftererror == 0))
    # *(df.special_trial == 0))[0]
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
    decision = np.array(df.R_response) * 2 - 1
    decision = decision[after_correct_id]
    sound_len = np.array(df.sound_len)
    sound_len = sound_len[after_correct_id]
    gt = np.array(df.rewside) * 2 - 1
    gt = gt[after_correct_id]
    trial_index = np.array(df.origidx)
    trial_index = trial_index[after_correct_id]
    resp_len = np.array(df.resp_len)
    resp_len = resp_len[after_correct_id]
    df['norm_allpriors'] = zt/max(abs(zt))
    # if we want to use data from all rats, we must use dani_clean.pkl
    f1 = False
    f2 = True
    f3 = True
    f5 = False
    f6 = False

    # fig 1
    if f1:
        # fig1.d(df, savpath=SV_FOLDER, average=True)  # psychometrics
        # tachometrics, rt distribution, express performance
        fig_1(coh, hit, sound_len, decision, zt, resp_len, trial_index, supt='')
        fig_1_mt_weights(df, plot=True)

    # fig 2
    if f2:
        fgsz = (8, 8)
        inset_sz = 0.1
        accel = False
        if accel:
            f, ax = plt.subplots(nrows=3, ncols=2, figsize=fgsz)
            ax = ax.flatten()
            ax_cohs = np.array([ax[0], ax[2], ax[4]])
        else:
            f, ax = plt.subplots(nrows=2, ncols=2, figsize=fgsz)
            ax = ax.flatten()
            ax_cohs = np.array([ax[0], ax[2]])
        ax_inset = add_inset(ax=ax_cohs[0], inset_sz=inset_sz, fgsz=fgsz)
        ax_cohs = np.insert(ax_cohs, 0, ax_inset)
        ax_inset = add_inset(ax=ax_cohs[2], inset_sz=inset_sz, fgsz=fgsz,
                             marginy=0.15)
        ax_cohs = np.insert(ax_cohs, 2, ax_inset)
        if accel:
            ax_inset = add_inset(ax=ax_cohs[4], inset_sz=inset_sz, fgsz=fgsz,
                                 marginy=0.15)
            ax_cohs = np.insert(ax_cohs, 4, ax_inset)
        for a in ax:
            rm_top_right_lines(a)
        trajs_cond_on_coh(df=df, ax=ax_cohs, average=True,
                          acceleration=accel)
        # splits
        ax_split = np.array([ax[1], ax[3]])
        trajs_splitting(df, ax=ax_split[0])
        # XXX: do this panel for all rats?
        trajs_splitting_point(df=df, ax=ax_split[1])
        # fig3.trajs_cond_on_prior(df, savpath=SV_FOLDER)

    # fig 3
    if f3:
        rat_path = '/home/molano/Dropbox/project_Barna/' +\
            'ChangesOfMind/figures/Figure_3/'
        fig2.bcd(parentpath=rat_path, sv_folder=SV_FOLDER)
        fig2.e(df, sv_folder=SV_FOLDER)
        fig2.f(df, sv_folder=SV_FOLDER)
        fig2.g(df, sv_folder=SV_FOLDER)
        df_data = pd.DataFrame({'avtrapz': coh, 'CoM_sugg': com,
                                'norm_allpriors': zt/max(abs(zt)),
                                'R_response': (decision+1)/2})
        com_heatmap_paper_marginal_pcom_side(df_data, side=0)
        com_heatmap_paper_marginal_pcom_side(df_data, side=1)

    # fig 5 (model)
    if f5:
        num_tr = int(3e5)
        decision = decision[:int(num_tr)]
        zt = zt[:int(num_tr)]
        sound_len = sound_len[:int(num_tr)]
        coh = coh[:int(num_tr)]
        com = com[:int(num_tr)]
        gt = gt[:int(num_tr)]
        trial_index = trial_index[:int(num_tr)]
        hit = hit[:int(num_tr)]
        if stim.shape[0] != 20:
            stim = stim.T
        stim = stim[:, :int(num_tr)]
        hit_model, reaction_time, com_model_detected, resp_fin, com_model,\
            pro_vs_re, trajs =\
            run_model(stim=stim, zt=zt, coh=coh, gt=gt, trial_index=trial_index,
                      num_tr=None)
        # basic_statistics(decision=decision, resp_fin=resp_fin)  # dec
        # basic_statistics(com, com_model_detected)  # com
        # basic_statistics(hit, hit_model)  # hit
        MT = [len(t) for t in trajs]
        df_sim = pd.DataFrame({'coh2': coh, 'trajectory_y': trajs,
                               'sound_len': reaction_time,
                               'rewside': (gt + 1)/2,
                               'R_response': (resp_fin+1)/2,
                               'resp_len': np.array(MT)*1e-3})
        df_sim['traj_d1'] = [np.diff(t) for t in trajs]
        df_sim['aftererror'] =\
            np.array(df.aftererror)[after_correct_id][:int(num_tr)]
        df_sim['subjid'] = 'simul'
        df_sim['dW_trans'] =\
            np.array(df.dW_trans)[:int(num_tr)][after_correct_id]
        df_sim['origidx'] =\
            np.array(df.origidx)[:int(num_tr)][after_correct_id]
        df_sim['dW_lat'] = np.array(df.dW_lat)[:int(num_tr)][after_correct_id]
        df_sim['special_trial'] =\
            np.array(df.special_trial)[:int(num_tr)][after_correct_id]
        df_sim['traj'] = df_sim['trajectory_y']
        # simulation plots
        means, errors = fig_1_mt_weights(df)
        means_model, errors_model = fig_1_mt_weights(df_sim)
        fig_5(coh=coh, hit=hit, sound_len=sound_len, decision=decision, zt=zt,
              hit_model=hit_model, sound_len_model=reaction_time,
              decision_model=resp_fin, com=com, com_model=com_model,
              com_model_detected=com_model_detected, pro_vs_re=pro_vs_re,
              means=means, errors=errors, means_model=means_model,
              errors_model=errors_model, df_sim=df_sim)
        supp_trajs_prior_cong(df_sim, ax=None)
        if f6:
            # human traj plots
            human_trajs(user_id='AlexCRM', sv_folder=SV_FOLDER, max_mt=600,
                        wanted_precision=12, traj_thr=250, vel_thr=2.6)
    # from utilsJ.Models import extended_ddm_v2 as edd2
    # import numpy as np
    # import matplotlib.pyplot as plt
    # DATA_FOLDER = '/home/molano/ChangesOfMind/data/'  # Manuel
    # SV_FOLDER = '/home/molano/Dropbox/project_Barna/' +\
    #     'ChangesOfMind/figures/from_python/'  # Manuel

    # df = edd2.get_data_and_matrix(dfpath=DATA_FOLDER + 'LE43_',
    #                               return_df=True, sv_folder=SV_FOLDER)

    # coms = df.loc[df.CoM_sugg]
    # rts = coms.sound_len

    # max_ = 0
    # for tr in range(len(coms)):
    #     trial = df.iloc[tr]
    #     traj = trial['trajectory_y']
    #     plt.plot(traj, 'k')
    #     max_temp = np.nanmax(traj)
    #     if max_temp > max_:
    #         max_ = max_temp
    #         print(max_)
    #     if np.nanmax(traj) > 200:
    #         print(trial)
