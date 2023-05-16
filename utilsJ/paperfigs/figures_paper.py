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
import sys, os
from scipy.optimize import curve_fit
from sklearn.metrics import roc_curve
from sklearn.metrics import RocCurveDisplay
from sklearn.metrics import confusion_matrix
from scipy.stats import pearsonr, ttest_ind, ttest_rel, zscore
from matplotlib.lines import Line2D
from statsmodels.stats.proportion import proportion_confint
# from scipy import interpolate
# import shutil

# sys.path.append("/home/jordi/Repos/custom_utils/")  # alex idibaps
# sys.path.append("C:/Users/Alexandre/Documents/GitHub/")  # Alex
# sys.path.append("C:/Users/agarcia/Documents/GitHub/custom_utils")  # Alex CRM
# sys.path.append("/home/garciaduran/custom_utils")  # Cluster Alex
sys.path.append("/home/molano/custom_utils") # Cluster Manuel

from utilsJ.Models import simul
from utilsJ.Models import extended_ddm_v2 as edd2
from utilsJ.Behavior.plotting import binned_curve, tachometric, psych_curve,\
    trajectory_thr, com_heatmap, interpolapply
from utilsJ.Models import analyses_humans as ah
import fig1, fig3, fig2
import matplotlib
import matplotlib.pylab as pl
from scipy import interpolate


matplotlib.rcParams['font.size'] = 9
plt.rcParams['legend.title_fontsize'] = 8
plt.rcParams['xtick.labelsize']= 8
plt.rcParams['ytick.labelsize']= 8
# matplotlib.rcParams['font.family'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Helvetica'
matplotlib.rcParams['lines.markersize'] = 3

# ---GLOBAL VARIABLES
pc_name = 'idibaps'
if pc_name == 'alex':
    RAT_COM_IMG = 'C:/Users/Alexandre/Desktop/CRM/rat_image/001965.png'
    SV_FOLDER = 'C:/Users/Alexandre/Desktop/CRM/Alex/paper/figures_python/'  # Alex
    DATA_FOLDER = 'C:/Users/Alexandre/Desktop/CRM/Alex/paper/data/'  # Alex
    RAT_noCOM_IMG = 'C:/Users/Alexandre/Desktop/CRM/rat_image/screenShot230120.png'
    TASK_IMG = 'C:/Users/Alexandre/Desktop/CRM/rat_image/panel_a.png'
    HUMAN_TASK_IMG = 'C:/Users/Alexandre/Desktop/CRM/rat_image/g41085.png'
elif pc_name == 'idibaps':
    DATA_FOLDER = '/home/molano/ChangesOfMind/data/'  # Manuel
    SV_FOLDER = '/home/molano/Dropbox/project_Barna/' +\
        'ChangesOfMind/figures/from_python/'  # Manuel
    RAT_noCOM_IMG = '/home/molano/Dropbox/project_Barna/' +\
        'ChangesOfMind/figures/Figure_1/screenShot230120.png'
    RAT_COM_IMG = '/home/molano/Dropbox/project_Barna/' +\
        'ChangesOfMind/figures/Figure_3/001965.png'
    TASK_IMG = '/home/molano/Dropbox/project_Barna/ChangesOfMind/' +\
        'figures/Figure_1/panel_a.png'
elif pc_name == 'idibaps_alex':
    SV_FOLDER = '/home/jordi/DATA/Documents/changes_of_mind/'  # Jordi
    DATA_FOLDER = '/home/jordi/DATA/Documents/changes_of_mind/data_clean/'  # Jordi
    RAT_COM_IMG = '/home/jordi/Documents/changes_of_mind/demo/materials/' +\
        'craft_vid/CoM/a/001965.png'
    RAT_noCOM_IMG = '/home/jordi/DATA/Documents/changes_of_mind/data_clean/' +\
        'screenShot230120.png'
    HUMAN_TASK_IMG = '/home/jordi/DATA/Documents/changes_of_mind/humans/g41085.png'
elif pc_name == 'alex_CRM':
    SV_FOLDER = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/'  # Alex CRM
    DATA_FOLDER = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/data/'  # Alex CRM
    RAT_COM_IMG = 'C:/Users/agarcia/Desktop/CRM/proves/001965.png'
    RAT_noCOM_IMG = 'C:/Users/agarcia/Desktop/CRM/proves/screenShot230120.png'
    HUMAN_TASK_IMG = 'C:/Users/agarcia/Desktop/CRM/rat_image/g41085.png'
    TASK_IMG = 'C:/Users/agarcia/Desktop/CRM/Alex/paper/panel_a.png'

FRAME_RATE = 14
BINS_RT = np.linspace(1, 301, 11)
xpos_RT = int(np.diff(BINS_RT)[0])
COLOR_COM = 'coral'
COLOR_NO_COM = 'tab:cyan'


def plot_coms(df, ax, human=False):
    coms = df.CoM_sugg.values
    decision = df.R_response.values
    if human:
        ran_max = 600
        max_val = 600
    if not human:
        ran_max = 400
        max_val = 77
    for tr in reversed(range(ran_max)):  # len(df_rat)):
        if tr > (ran_max/2) and not coms[tr] and decision[tr] == 1:
            trial = df.iloc[tr]
            traj = trial['trajectory_y']
            if not human:
                time = df.time_trajs.values[tr]
                ax.plot(time, traj, color=COLOR_NO_COM, lw=.5)
                ax.set_xlim(-100, 800)
            if human:
                time = np.array(trial['times'])
                if time[-1] < 0.3 and time[-1] > 0.1:
                    ax.plot(time*1e3, traj, color=COLOR_NO_COM, lw=.5)
        elif tr < (ran_max/2-1) and coms[tr] and decision[tr] == 0:
            trial = df.iloc[tr]
            traj = trial['trajectory_y']
            if not human:
                time = df.time_trajs.values[tr]
                ax.plot(time, traj, color=COLOR_COM, lw=2)
                ax.set_xlim(-100, 800)
            if human:
                time = np.array(trial['times'])
                if time[-1] < 0.3 and time[-1] > 0.2:
                    ax.plot(time*1e3, traj, color=COLOR_COM, lw=2)
    rm_top_right_lines(ax)
    if human:
        var = 'x'
    if not human:
        var = 'y'
    ax.set_ylabel('{}-coord (pixels)'.format(var))
    ax.set_xlabel('Time from movement onset (ms)')
    ax.axhline(y=max_val, linestyle='--', color='Green', lw=1)
    ax.axhline(y=-max_val, linestyle='--', color='Purple', lw=1)
    ax.axhline(y=0, linestyle='--', color='k', lw=0.5)


def plot_fixation_breaks_single(subject, ax):
    path = DATA_FOLDER + subject + '_clean.pkl'
    df = pd.read_pickle(path)
    hist_edges = np.linspace(-0.3, 0.4, 71)
    rt_density_per_session =\
        np.vstack(df.groupby('sessid').apply(lambda x: np.concatenate(
            [x.sound_len/1000, np.concatenate(x.fb.values)-0.3]))
            .apply(lambda x: np.histogram(x, density=True, bins=hist_edges)[0])
            .values)
    ax.errorbar(hist_edges[:-1]+0.005, rt_density_per_session.mean(axis=0),
                np.std(rt_density_per_session, axis=0))
    ax.axvline(0, c='r')
    ax.set_xlabel('RT (s)')
    ax.set_ylabel('mean density (+/- std)')
    # plt.show()


def plot_coms_single_session(df, ax):
    rm_top_right_lines(ax)
    np.random.seed(1)
    sess = df.loc[df.sessid == 'LE37_p4_20190213-151548']
    coms = sess.CoM_sugg.values
    decision = sess.R_response.values
    index = np.random.choice(np.arange(len(decision)), 100)
    for itr, traj in enumerate(sess.trajectory_y.values[index]):
        time = sess.time_trajs.values[index][itr]
        if time[-1] > 600:
            continue
        if not coms[index][itr] and decision[index][itr] == 1:
            ax.plot(time, traj, color=COLOR_NO_COM)
    for itr, traj in enumerate(sess.trajectory_y.values[index]):
        time = sess.time_trajs.values[index][itr]
        if coms[index][itr] and decision[index][itr] == 0:
            ax.plot(time, traj, color=COLOR_COM)
    ax.set_xlim(-100, 650)
    ax.set_ylabel('y-coord (pixels)')
    ax.set_xlabel('Time from movement onset (ms)')
    ax.axhline(y=75, linestyle='--', color='Green', lw=1)
    ax.axhline(y=-75, linestyle='--', color='Purple', lw=1)
    ax.axhline(y=0, linestyle='--', color='k', lw=0.5)
    ax.set_yticks([-75, -50, -25, 0, 25, 50, 75])


def plot_rt_all_rats(subjects):
    fig, ax = plt.subplots(nrows=5, ncols=3)
    ax = ax.flatten()
    for i_s, subject in enumerate(subjects):
        plot_fixation_breaks_single(subject=subject, ax=ax[i_s])


def tracking_image(ax, figsize=(8, 12), margin=.01):
    ax.axhline(y=50, linestyle='--', color='k', lw=.5)
    ax.axhline(y=210, linestyle='--', color='k', lw=.5)
    ax_scrnsht = ax
    pos = ax_scrnsht.get_position()
    ax_scrnsht.set_position([pos.x0, pos.y0, pos.width,
                             pos.height])
    # add colorbar for screenshot
    n_stps = 100
    ax_clbr = plt.axes([pos.x0+pos.width*1/7, pos.y0+pos.height+margin,
                        pos.width*0.6, pos.height/15])
    ax_clbr.imshow(np.linspace(0, 1, n_stps)[None, :], aspect='auto')
    ax_clbr.set_xticks([0, n_stps-1])
    ax_clbr.set_xticklabels(['0', '400ms'])
    ax_clbr.tick_params(labelsize=6)
    # ax_clbr.set_title('$N_{max}$', fontsize=6)
    ax_clbr.set_yticks([])
    ax_clbr.xaxis.set_ticks_position("top")
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
    colormap = pl.cm.gist_gray_r(np.linspace(0.4, 1, 4))
    legendelements = [Line2D([0], [0], color=colormap[0], lw=2,
                             label='0'),
                      Line2D([0], [0], color=colormap[1], lw=2,
                             label='0.25'),
                      Line2D([0], [0], color=colormap[2], lw=2,
                             label='0.5'),
                      Line2D([0], [0], color=colormap[3], lw=2,
                             label='1')]
    ax_tach.legend(handles=legendelements, fontsize=7)
    # plot Pcoms matrices
    nbins = 7
    matrix_side_0 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=0)
    matrix_side_1 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=1)
    # L-> R
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[0].set_title(pcomlabel_1)
    im = ax_mat[0].imshow(matrix_side_1, vmin=0, vmax=vmax, cmap='magma')
    plt.sca(ax_mat[0])

    pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[1].set_title(pcomlabel_0)
    im = ax_mat[1].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
    ax_mat[1].yaxis.set_ticks_position('none')
    plt.sca(ax_mat[1])
    cbar = plt.colorbar(im, fraction=0.04)
    cbar.set_label('p(detected CoM)', rotation=270, labelpad=10)
    # pright matrix
    if humans:
        coh = df_data['avtrapz'].values
    else:
        coh = df_data['coh2'].values
    choice = df_data['R_response'].values
    prior = df_data['norm_allpriors'].values
    mat_pright, _ = com_heatmap(prior, coh, choice, return_mat=True,
                                annotate=False)
    mat_pright = np.flipud(mat_pright)
    im_2 = ax_pright.imshow(mat_pright, cmap='PRGn_r')
    plt.sca(ax_pright)
    plt.colorbar(im_2, fraction=0.04)

    # R -> L
    for ax_i in [ax_pright, ax_mat[0], ax_mat[1]]:
        ax_i.set_xlabel('Prior Evidence')
        ax_i.set_yticklabels(['']*nbins)
        ax_i.set_xticklabels(['']*nbins)
    for ax_i in [ax_pright, ax_mat[0]]:
        ax_i.set_ylabel('Stimulus Evidence')  # , labelpad=-17)


def rm_top_right_lines(ax, right=True):
    if right:
        ax.spines['right'].set_visible(False)
    else:
        ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)


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


def add_inset(ax, inset_sz=0.2, fgsz=(4, 8), marginx=0.01, marginy=0.05,
              right=True):
    # adds inset to an axis
    ratio = fgsz[0]/fgsz[1]
    pos = ax.get_position()
    ax_inset = plt.axes([pos.x1-inset_sz-marginx, pos.y0+marginy, inset_sz,
                         inset_sz*ratio])
    rm_top_right_lines(ax_inset, right=right)
    return ax_inset


def mean_com_traj(df, ax, condition='choice_x_prior', cmap='copper', prior_limit=1,
                  after_correct_only=True, rt_lim=300,
                  trajectory='trajectory_y',
                  interpolatespace=np.linspace(-700000, 1000000, 1700)):
    # plots mean com trajectory and mean non-CoM trajectory
    rm_top_right_lines(ax)
    nanidx = df.loc[df[['dW_trans', 'dW_lat']].isna().sum(axis=1) == 2].index
    df['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df.loc[nanidx, 'allpriors'] = np.nan
    df['norm_allpriors'] = norm_allpriors_per_subj(df)
    df['choice_x_prior'] = (df.R_response*2-1) * df.norm_allpriors
    df['choice_x_coh'] = (df.R_response*2-1) * df.coh2
    bins = np.array([-1.1, 1.1])
    # xlab = 'prior towards response'
    bintype = 'edges'
    all_trajs = np.empty((len(df.subjid.unique()), 1700))
    all_trajs[:] = np.nan
    all_trajs_nocom = np.empty((len(df.subjid.unique()), 1700))
    all_trajs_nocom[:] = np.nan
    for i_s, subj in enumerate(df.subjid.unique()):
        if subj == 'LE86':
            continue
        if after_correct_only:
            ac_cond = df.aftererror == False
        else:
            ac_cond = (df.aftererror*1) >= 0
        indx_trajs = (df.norm_allpriors.abs() <= prior_limit) &\
            ac_cond & (df.special_trial == 0) &\
            (df.sound_len < rt_lim) & (df.CoM_sugg == True) & (df.subjid == subj)
        _, _, _, mat, _, _ =\
            trajectory_thr(df.loc[indx_trajs], condition, bins,
                           collapse_sides=True, thr=30, ax=None, ax_traj=ax,
                           return_trash=True, error_kwargs=dict(marker='o'),
                           cmap=None, bintype=bintype,
                           trajectory=trajectory, plotmt=False,
                           color_tr=COLOR_COM, alpha_low=True)
        median_traj = np.nanmedian(mat[0], axis=0)
        all_trajs[i_s, :] = median_traj
        all_trajs[i_s, :] += -np.nanmean(median_traj[(interpolatespace > -100000) &
                                                     (interpolatespace < 0)])
        indx_trajs = (df.norm_allpriors.abs() <= prior_limit) &\
            ac_cond & (df.special_trial == 0) &\
                (df.sound_len < rt_lim) & (df.CoM_sugg == False) & (df.subjid == subj)
        _, _, _, mat, _, _ =\
            trajectory_thr(df.loc[indx_trajs], condition, bins,
                           collapse_sides=True, thr=30, ax=None, ax_traj=ax,
                           return_trash=True, error_kwargs=dict(marker='o'),
                           cmap=None, bintype=bintype,
                           trajectory=trajectory, plotmt=False, plot_traj=False,
                           alpha_low=True)
        all_trajs_nocom[i_s, :] = np.nanmedian(mat[0], axis=0)
    mean_traj = np.nanmedian(all_trajs, axis=0)
    mean_traj += -np.nanmean(mean_traj[(interpolatespace > -100000) &
                                       (interpolatespace < 0)])
    mean_traj_nocom = np.nanmedian(all_trajs_nocom, axis=0)
    mean_traj_nocom += -np.nanmean(mean_traj_nocom[(interpolatespace > -100000) &
                                                   (interpolatespace < 0)])
    ax.plot((interpolatespace)/1000, mean_traj, color=COLOR_COM, linewidth=2)
    ax.plot((interpolatespace)/1000, mean_traj_nocom, color=COLOR_NO_COM, linewidth=2,
            label='No-Rev.')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('y-coord (pixels)')
    ax.set_ylim(-30, 85)
    ax.set_xlim(-100, 500)
    legendelements = [Line2D([0], [0], color=COLOR_COM, lw=2,
                             label='Detected Rev.'),
                      Line2D([0], [0], color=COLOR_NO_COM, lw=2,
                             label='No-Rev.')]
    ax.legend(handles=legendelements)
    ax.axhline(-8, color='r', linestyle=':')
    ax.text(20, -20, "Detection threshold", color='r')


def binning_mt_prior(df, bins):
    # matrix with rows for subjects and columns for bins
    mat_mt = np.empty((len(df.subjid.unique()), len(bins)-1))
    for i_s, subject in enumerate(df.subjid.unique()):
        df_sub = df.loc[df.subjid == subject]
        for i_zt, bin_zt in enumerate(bins[:-1]):
            mt_sub = df_sub.loc[(df_sub.norm_allpriors >= bin_zt) &
                                (df_sub.norm_allpriors < bins[i_zt+1]), 'resp_len']
            mat_mt[i_s, i_zt] = np.nanmean(mt_sub)
    return mat_mt  # if you want mean across subjects, np.nanmean(mat_mt, axis=0)


def get_bin_info(condition, prior_limit=0.25, after_correct_only=True, rt_lim=300):
    # after correct condition
    ac_cond = df.aftererror == False if after_correct_only else (df.aftererror*1) >= 0
    # define bins, bin type, trajectory index and colormap depending on condition
    if condition == 'choice_x_coh':
        bins = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]
        bintype = 'categorical'
        indx_trajs = (df.norm_allpriors.abs() <= prior_limit) &\
            ac_cond & (df.special_trial == 0) &\
            (df.sound_len < rt_lim)
        n_iters = len(bins)
        colormap = pl.cm.coolwarm(np.linspace(0., 1, n_iters))
    elif condition == 'choice_x_prior':
        bins_zt = [-1.01]
        for i_p, perc in enumerate([0.5, 0.25, 0.25, 0.5]):
            if i_p > 2:
                bins_zt.append(df.norm_allpriors.abs().quantile(perc))
            else:
                bins_zt.append(-df.norm_allpriors.abs().quantile(perc))
        bins_zt.append(1.01)
        bins = np.array(bins_zt)
        bintype = 'edges'
        rt_lim = 200
        indx_trajs = (df.norm_allpriors.abs() <= prior_limit) &\
            ac_cond & (df.special_trial == 2) &\
            (df.sound_len < rt_lim)
        n_iters = len(bins)-1
        colormap = pl.cm.copper(np.linspace(0., 1, n_iters))
    elif condition == 'origidx':
        bins = np.linspace(0, 1e3, num=6)
        bintype = 'edges'
        n_iters = len(bins) - 1
        indx_trajs = (df.norm_allpriors.abs() <= prior_limit) &\
            ac_cond & (df.special_trial == 0) &\
            (df.sound_len < rt_lim)
        colormap = pl.cm.jet(np.linspace(0., 1, n_iters))
    return bins, bintype, indx_trajs, n_iters, colormap

def plot_mt(df, ax, condition='choice_x_coh', prior_limit=0.25, rt_lim=50,
            after_correct_only=True):
    bins, _, _, _, colormap = get_bin_info(condition=condition, prior_limit=prior_limit,
                                            after_correct_only=after_correct_only,
                                            rt_lim=rt_lim)
    if condition == 'choice_x_coh':
        mt_time = df.groupby('coh2').resp_len.median()
    elif condition == 'choice_x_prior':
        mt_time = binning_mt_prior(df, bins)
    for i_tr, traj in enumerate(mt_time):
        
        if len(subjects) > 1:
            c = colormap[i_tr]
            xp = bins+bins[1]/2
            ax[0].boxplot(mt_time[i_tr, :], positions=xp, 
                            boxprops=dict(markerfacecolor=c, markeredgecolor=c))
            ax[0].plot(xp + 0.1*np.random.randn(len(subjects)),
                       mt_time[i_tr, :], color=colormap[i_tr], marker='o',
                       linestyle='None')
        else:
            ax[0].errorbar(xpoints[i_tr], mt_time[i_tr], yerr=mt_time_err[i_tr],
                            color=colormap[i_tr], marker='o')

        ax[0].set_ylabel('MT (ms)', fontsize=9)
        ax[0].plot(xpoints, mt_time, color='k', ls=':')

def plots_trajs_conditioned(df, ax, condition='choice_x_coh', cmap='viridis',
                            prior_limit=0.25, rt_lim=50,
                            after_correct_only=True,
                            trajectory="trajectory_y",
                            velocity=("traj_d1", 1)):
    """
    Plots mean trajectories, MT, velocity and peak velocity
    conditioning on Coh/Zt/T.index,
    """
    interpolatespace = np.linspace(-700000, 1000000, 1700)
    nanidx = df.loc[df[['dW_trans', 'dW_lat']].isna().sum(axis=1) == 2].index
    df['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df.loc[nanidx, 'allpriors'] = np.nan
    df['norm_allpriors'] = norm_allpriors_per_subj(df)
    df['choice_x_prior'] = (df.R_response*2-1) * df.norm_allpriors
    df['choice_x_coh'] = (df.R_response*2-1) * df.coh2
    bins, bintype, indx_trajs, n_iters, colormap =\
          get_bin_info(condition=condition, prior_limit=prior_limit,
                        after_correct_only=after_correct_only,
                        rt_lim=rt_lim)
    # POSITION
    subjects = df['subjid'].unique()
    mat_all = np.empty((n_iters, 1700, len(subjects)))
    mt_all = np.empty((n_iters, len(subjects)))
    for i_subj, subj in enumerate(subjects):
        traj_data = DATA_FOLDER+subj+'/traj_data/'+subj+'_traj_pos_'+condition+'.npz'
        # create folder if it doesn't exist
        os.makedirs(os.path.dirname(traj_data), exist_ok=True)
        if os.path.exists(traj_data):
            traj_data = np.load(traj_data, allow_pickle=True)
            mean_traj = traj_data['mean_traj']
            xpoints = traj_data['xpoints']
            mt_time = traj_data['mt_time']
        else:
            xpoints, _, _, mat, _, mt_time =\
                trajectory_thr(df.loc[(indx_trajs) & (df.subjid == subj)],
                               condition, bins, collapse_sides=True, thr=30,
                               ax=None, ax_traj=None, return_trash=True,
                               error_kwargs=dict(marker='o'), cmap=cmap, bintype=bintype,
                               trajectory=trajectory, plotmt=True, alpha_low=False)
            mean_traj = np.array([np.nanmean(mat[m], axis=0) for m in mat])
            data = {'xpoints': xpoints, 'mean_traj': mean_traj, 'mt_time': mt_time}
            np.savez(traj_data, **data)
        mat_all[:, :, i_subj] = mean_traj
        mt_all[:, i_subj] = mt_time
    all_trajs = np.nanmean(mat_all, axis=2)
    all_trajs_err = np.nanstd(mat_all, axis=2) / np.sqrt(len(subjects))
    mt_time = np.nanmedian(mt_all, axis=1)
    mt_time_err = np.nanstd(mt_all, axis=1) / np.sqrt(len(subjects))
    for i_tr, traj in enumerate(all_trajs):
        ax[0].plot(interpolatespace/1000, traj, color=colormap[i_tr])
        ax[0].fill_between(interpolatespace/1000, traj-all_trajs_err[i_tr],
                           traj+all_trajs_err[i_tr], color=colormap[i_tr],
                           alpha=0.5)
    if condition == 'choice_x_coh':
        legendelements = [Line2D([0], [0], color=colormap[0], lw=2, label='-1'),
                          Line2D([0], [0], color=colormap[1], lw=2, label=''),
                          Line2D([0], [0], color=colormap[2], lw=2, label=''),
                          Line2D([0], [0], color=colormap[3], lw=2, label='0'),
                          Line2D([0], [0], color=colormap[4], lw=2, label=''),
                          Line2D([0], [0], color=colormap[5], lw=2, label=''),
                          Line2D([0], [0], color=colormap[6], lw=2, label='1')]
        ax[0].legend(handles=legendelements, title='Stimulus \n evidence',
                     loc='upper left', fontsize=7)
        ax[1].set_xticks([0])
        ax[1].set_xticklabels(['Stimulus'], fontsize=9)
        ax[1].xaxis.set_ticks_position('none')
        ax[1].set_ylim([0.5, 0.8])
    if condition == 'choice_x_prior':
        legendelements = [Line2D([0], [0], color=colormap[4], lw=2,
                                 label='congruent'),
                          Line2D([0], [0], color=colormap[3], lw=2,
                                 label=''),
                          Line2D([0], [0], color=colormap[2], lw=2,
                                 label='0'),
                          Line2D([0], [0], color=colormap[1], lw=2,
                                 label=''),
                          Line2D([0], [0], color=colormap[0], lw=2,
                                 label='incongruent')]
        ax[0].legend(handles=legendelements, title='Prior', loc='upper left',
                     fontsize=7)
        xpoints = (bins[:-1] + bins[1:]) / 2
        ax[1].set_ylim([0.5, 0.8])
        ax[1].set_xticks([0])
        ax[1].set_xticklabels(['Prior'], fontsize=9)
        ax[1].xaxis.set_ticks_position('none')
    if condition == 'origidx':
        legendelements = []
        labs = ['100', '300', '500', '700', '900']
        for i in range(len(colormap)):
            legendelements.append(Line2D([0], [0], color=colormap[i], lw=2,
                                  label=labs[i]))
        ax[0].legend(handles=legendelements, title='Trial index')
        ax[1].set_xlabel('Trial index')
    ax[0].set_xlim([-20, 450])
    ax[0].set_xticklabels('')
    ax[0].axhline(0, c='gray')
    ax[0].set_ylabel('Position (pixels)')
    ax[0].set_ylim([-10, 85])
    ax[0].set_yticks([0, 25, 50, 75])
    ax[0].axhline(78, color='gray', linestyle=':')
    # VELOCITIES
    mat_all = np.empty((n_iters, 1700, len(subjects)))
    mt_all = np.empty((n_iters, len(subjects)))
    for i_subj, subj in enumerate(subjects):
        traj_data = DATA_FOLDER + subj + '/traj_data/' + subj + '_traj_vel_'+condition+'.npz'
        # create folder if it doesn't exist
        os.makedirs(os.path.dirname(traj_data), exist_ok=True)
        if os.path.exists(traj_data):
            traj_data = np.load(traj_data, allow_pickle=True)
            mean_traj = traj_data['mean_traj']
            xpoints = traj_data['xpoints']
            mt_time = traj_data['mt_time']
            ypoints = traj_data['ypoints']
        else:
            xpoints, ypoints, _, mat, _, mt_time =\
                trajectory_thr(df.loc[(indx_trajs) & (df.subjid == subj)],
                               condition, bins,
                               collapse_sides=True, thr=30, ax=None, ax_traj=None,
                               return_trash=True, error_kwargs=dict(marker='o'),
                               cmap=cmap, bintype=bintype,
                               trajectory=velocity, plotmt=True, alpha_low=False)
            mean_traj = np.array([np.nanmean(mat[m], axis=0) for m in mat])
            data = {'xpoints': xpoints, 'ypoints': ypoints, 'mean_traj': mean_traj, 'mt_time': mt_time}
            np.savez(traj_data, **data)
        mat_all[:, :, i_subj] = mean_traj
        mt_all[:, i_subj] = ypoints
    all_trajs = np.nanmean(mat_all, axis=2)
    all_trajs_err = np.nanstd(mat_all, axis=2) / np.sqrt(len(subjects))
    mt_time = np.nanmedian(mt_all, axis=1)
    mt_time_err = np.nanstd(mt_all, axis=1) / np.sqrt(len(subjects))
    for i_tr, traj in enumerate(all_trajs):
        ax[2].plot(interpolatespace/1000, traj, color=colormap[i_tr])
        ax[2].fill_between(interpolatespace/1000, traj-all_trajs_err[i_tr],
                           traj+all_trajs_err[i_tr], color=colormap[i_tr],
                           alpha=0.5)
        if len(subjects) > 1:
            xp = [xpoints[i_tr]]
            c = colormap[i_tr]
            ax[1].boxplot(mt_all[i_tr, :], positions=xp,
                          boxprops=dict(markerfacecolor=c, markeredgecolor=c))
            ax[1].plot(xpoints[i_tr] + 0.1*np.random.randn(len(subjects)),
                       mt_all[i_tr, :], color=colormap[i_tr], marker='o',
                       linestyle='None')
        else:
            ax[1].errorbar(xpoints[i_tr], mt_time[i_tr], yerr=mt_time_err[i_tr],
                           color=colormap[i_tr], marker='o')
    ax[2].set_xlim([-20, 450])
    ax[1].set_ylabel('Peak (pixels/ms)')
    ax[2].set_ylim([-0.05, 0.5])
    ax[2].axhline(0, c='gray')
    ax[2].set_ylabel('Velocity (pixels/ms)')
    ax[2].set_xlabel('Time from movement onset (ms)', fontsize=8)
    ax[1].plot(xpoints, mt_time, color='k', ls=':')


def get_split_ind_corr(mat, evl, pval=0.01, max_MT=400, startfrom=700, sim=True):
    # Returns index at which the trajectories and coh vector become uncorrelated
    # backwards in time
    # mat: trajectories (n trials x time)
    plist = []
    for i in reversed(range(max_MT)):  # reversed so it goes backwards in time
        pop_a = mat[:, startfrom + i]
        nan_idx = ~np.isnan(pop_a)
        pop_evidence = evl[nan_idx]
        pop_a = pop_a[nan_idx]
        try:
            _, p2 = pearsonr(pop_a, pop_evidence)  # p2 = pvalue from pearson corr
            plist.append(p2)
        except Exception:
            continue
            # return np.nan
        if p2 > pval:
            return i + 1
        if sim and np.isnan(p2):
            return i + 1
    return np.nan


def plot_trajs_splitting_example(df, ax, rtbin=0, rtbins=np.linspace(0, 150, 2),
                                 subject='LE37', startfrom=700, xlab=False):
    """
    Plot trajectories depending on COH and the corresponding Splitting Time as arrow.


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
    subject = subject
    lbl = 'RTs: ['+str(rtbins[rtbin])+'-'+str(rtbins[rtbin+1])+']'
    colors = pl.cm.gist_yarg(np.linspace(0.4, 1, 3))
    evs = [0.25, 0.5, 1]
    mat = np.empty((1701,))
    evl = np.empty(())
    appb = True
    colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
    for iev, ev in enumerate(evs):
        indx = (df.special_trial == 0) & (df.subjid == subject)
        if np.sum(indx) > 0:
            _, matatmp, matb =\
                simul.when_did_split_dat(df=df[indx], side=0, collapse_sides=True,
                                         ax=ax, rtbin=rtbin, rtbins=rtbins,
                                         color=colors[iev], label=lbl, coh1=ev,
                                         align='sound')
        if appb:
            mat = matb
            evl = np.repeat(0, matb.shape[0])
            appb = False
        mat = np.concatenate((mat, matatmp))
        evl = np.concatenate((evl, np.repeat(ev, matatmp.shape[0])))
    ind = get_split_ind_corr(mat, evl, pval=0.01, max_MT=400, startfrom=700)
    ax.set_xlim(-10, 255)
    ax.set_ylim(-0.6, 5.2)
    if xlab:
        ax.set_xlabel('Time from stimulus onset (ms)')
    if rtbins[-1] > 25 and xlab:
        ax.set_title('\n RT > 150 ms', fontsize=8)
        ax.arrow(ind, 3, 0, -2, color='k', width=1, head_width=5,
                 head_length=0.4)
        ax.text(ind-17, 3.4, 'Splitting Time', fontsize=8)
        ax.set_ylabel("{} Snout position (px)".format("           "))
        plot_boxcar_rt(rt=rtbins[0], ax=ax)
    else:
        ax.set_title('RT < 15 ms', fontsize=8)
        ax.text(ind-60, 3.3, 'Splitting Time', fontsize=8)
        ax.arrow(ind, 2.85, 0, -1.4, color='k', width=1, head_width=5,
                 head_length=0.4)
        ax.set_xticklabels([''])
        plot_boxcar_rt(rt=rtbins[-1], ax=ax)
        labels = ['0', '0.25', '0.5', '1']
        legendelements = []
        for i_l, lab in enumerate(labels):
            legendelements.append(Line2D([0], [0], color=colormap[i_l], lw=2,
                                  label=lab))
        ax.legend(handles=legendelements, fontsize=7, loc='upper right')


def plot_boxcar_rt(rt, ax, low_val=0, high_val=2):
    # plot box representing stimulus duration
    x_vals = np.linspace(-1, rt+5, num=100)
    y_vals = [low_val]
    for x in x_vals[:-1]:
        if x <= rt:
            y_vals.append(high_val)
        else:
            y_vals.append(low_val)
    ax.step(x_vals, y_vals, color='k')
    ax.fill_between(x_vals, y_vals, np.repeat(0, len(y_vals)),
                    color='grey', alpha=0.6)


def trajs_splitting_prior(df, ax, rtbins=np.linspace(0, 150, 16),
                          trajectory='trajectory_y', threshold=300):
    # split time/subject by prior
    ztbins = [0.1, 0.4, 1.1]
    kw = {"trajectory": trajectory, "align": "sound"}
    out_data = []
    df_1 = df.copy()
    for subject in df_1.subjid.unique():
        out_data_sbj = []
        split_data = DATA_FOLDER + subject + '/traj_data/' + subject + '_traj_split_prior.npz'
        # create folder if it doesn't exist
        os.makedirs(os.path.dirname(split_data), exist_ok=True)
        if os.path.exists(split_data):
            split_data = np.load(split_data, allow_pickle=True)
            out_data_sbj = split_data['out_data']
        else:
            for i in range(rtbins.size-1):
                dat = df_1.loc[(df_1.subjid == subject) &
                            (df_1.sound_len < rtbins[i + 1]) &
                            (df_1.sound_len >= rtbins[i])]
                matb_0 = np.vstack(
                    dat.loc[(dat.norm_allpriors < 0.1) &
                            (dat.norm_allpriors >= 0)]
                    .apply(lambda x: interpolapply(x, **kw), axis=1).values.tolist())
                matb_1 = np.vstack(
                    dat.loc[(dat.norm_allpriors > -0.1) &
                            (dat.norm_allpriors <= 0)]
                    .apply(lambda x: interpolapply(x, **kw), axis=1).values.tolist())
                matb = np.vstack([matb_0*-1, matb_1])
                mat = matb
                ztl = np.repeat(0, matb.shape[0])
                for i_z, zt1 in enumerate(ztbins[:-1]):
                    mata_0 = np.vstack(
                        dat.loc[(dat.norm_allpriors > zt1) &
                                (dat.norm_allpriors <= ztbins[i_z+1])]
                        .apply(lambda x: interpolapply(x, **kw),
                            axis=1).values.tolist())
                    mata_1 = np.vstack(
                        dat.loc[(dat.norm_allpriors < -zt1) &
                                (dat.norm_allpriors >= -ztbins[i_z+1])]
                        .apply(lambda x: interpolapply(x, **kw),
                            axis=1).values.tolist())
                    mata = np.vstack([mata_0*-1, mata_1])
                    ztl = np.concatenate((ztl, np.repeat(zt1, mata.shape[0])))
                    mat = np.concatenate((mat, mata))
                current_split_index =\
                    get_split_ind_corr(mat, ztl, pval=0.01, max_MT=400,
                                    startfrom=700)
                if current_split_index >= rtbins[i]:
                    out_data_sbj += [current_split_index]
                else:
                    out_data_sbj += [np.nan]
            np.savez(split_data, out_data=out_data_sbj)
        out_data += [out_data_sbj]
    out_data = np.array(out_data).reshape(
        df_1.subjid.unique().size, rtbins.size-1, -1)
    out_data = np.swapaxes(out_data, 0, 1)
    out_data = out_data.astype(float)
    out_data[out_data > threshold] = np.nan
    binsize = rtbins[1]-rtbins[0]
    for i in range(df_1.subjid.unique().size):
        for j in range(out_data.shape[2]):
            ax.plot(binsize/2 + binsize * np.arange(rtbins.size-1),
                    out_data[:, i, j],
                    marker='o', mfc=(.6, .6, .6, .3), mec=(.6, .6, .6, 1),
                    mew=1, color=(.6, .6, .6, .3))
    error_kws = dict(ecolor='goldenrod', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='goldenrod', marker='o', label='mean & SEM')
    ax.errorbar(binsize/2 + binsize * np.arange(rtbins.size-1),
                np.nanmedian(out_data.reshape(rtbins.size-1, -1), axis=1),
                yerr=sem(out_data.reshape(rtbins.size-1, -1),
                         axis=1, nan_policy='omit'), **error_kws)
    ax.set_xlabel('RT (ms)')
    ax.set_title('Impact of prior', fontsize=9)
    ax.set_ylabel('Splitting time (ms)')
    ax.plot([0, 155], [0, 155], color='k')
    ax.fill_between([0, 250], [0, 250], [0, 0],
                    color='grey', alpha=0.6)
    ax.set_xlim(-5, 155)
    # plt.show()


def trajs_splitting_stim(df, ax, collapse_sides=True, threshold=300,
                         sim=False,
                         rtbins=np.linspace(0, 150, 16), connect_points=False,
                         draw_line=((0, 90), (90, 0)),
                         trajectory="trajectory_y"):

    # split time/subject by coherence
    if sim:
        splitfun = simul.when_did_split_simul
        df['traj'] = df.trajectory_y.values
    if not sim:
        splitfun = simul.when_did_split_dat
    out_data = []
    for subject in df.subjid.unique():
        out_data_sbj = []
        split_data = DATA_FOLDER + subject + '/traj_data/' + subject + '_traj_split_stim.npz'
        # create folder if it doesn't exist
        os.makedirs(os.path.dirname(split_data), exist_ok=True)
        if os.path.exists(split_data):
            split_data = np.load(split_data, allow_pickle=True)
            out_data_sbj = split_data['out_data_sbj']
        else:
            for i in range(rtbins.size-1):
                if collapse_sides:
                    evs = [0.25, 0.5, 1]
                    mat = np.empty((1701,))
                    evl = np.empty(())
                    appb = True
                    for ev in evs:
                        if not sim:  # TODO: do this if within splitfun
                            _, matatmp, matb =\
                                splitfun(df=df.loc[(df.special_trial == 0)
                                                & (df.subjid == subject)],
                                        side=0, collapse_sides=True,
                                        rtbin=i, rtbins=rtbins, coh1=ev,
                                        trajectory=trajectory, align="sound")
                        if sim:
                            _, matatmp, matb =\
                                splitfun(df=df.loc[(df.special_trial == 0)
                                                & (df.subjid == subject)],
                                        side=0, rtbin=i, rtbins=rtbins, coh=ev,
                                        align="sound")
                        if appb:
                            mat = matb
                            evl = np.repeat(0, matb.shape[0])
                            appb = False
                        mat = np.concatenate((mat, matatmp))
                        evl = np.concatenate((evl, np.repeat(ev, matatmp.shape[0])))
                    if not sim:
                        current_split_index =\
                            get_split_ind_corr(mat, evl, pval=0.01, max_MT=400,
                                            startfrom=700)
                    if sim:
                        max_mt = 800
                        current_split_index =\
                            get_split_ind_corr(mat, evl, pval=0.01, max_MT=max_mt,
                                            startfrom=0)+1
                    if current_split_index >= rtbins[i]:
                        out_data_sbj += [current_split_index]
                    else:
                        out_data_sbj += [np.nan]
                else:
                    for j in [0, 1]:  # side values
                        current_split_index, _, _ = splitfun(
                            df.loc[df.subjid == subject],
                            j,  # side has no effect because this is collapsing_sides
                            rtbin=i, rtbins=rtbins, align='sound')
                        out_data_sbj += [current_split_index]
            np.savez(split_data, out_data_sbj=out_data_sbj)
        out_data += [out_data_sbj]

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
                    binsize/2 + binsize * np.arange(rtbins.size-1),
                    out_data[:, i, j],
                    marker='o', mfc=(.6, .6, .6, .3), mec=(.6, .6, .6, 1),
                    mew=1, color=(.6, .6, .6, .3)
                )

    error_kws = dict(ecolor='firebrick', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='firebrick', marker='o', label='mean & SEM')
    ax.errorbar(
        binsize/2 + binsize * np.arange(rtbins.size-1),
        # we do the mean across rtbin axis
        np.nanmedian(out_data.reshape(rtbins.size-1, -1), axis=1),
        # other axes we dont care
        yerr=sem(out_data.reshape(rtbins.size-1, -1),
                 axis=1, nan_policy='omit'),
        **error_kws
    )
    # if draw_line is not None:
    #     ax.plot(*draw_line, c='r', ls='--', zorder=0, label='slope -1')
    ax.plot([0, 155], [0, 155], color='k')
    ax.fill_between([0, 250], [0, 250], [0, 0],
                    color='grey', alpha=0.6)
    ax.set_xlim(-5, 155)
    ax.set_xlabel('RT (ms)')
    ax.set_ylabel('Splitting time (ms)')
    ax.set_title('Impact of stimulus', fontsize=9)
    # plt.show()


def tachometric_data(coh, hit, sound_len, subjid, ax, label='Data'):
    rm_top_right_lines(ax)
    df_plot_data = pd.DataFrame({'avtrapz': coh, 'hithistory': hit,
                                 'sound_len': sound_len, 'subjid': subjid})
    tachometric(df_plot_data, ax=ax, fill_error=True, cmap='gist_yarg')
    ax.axhline(y=0.5, linestyle='--', color='k', lw=0.5)
    ax.set_xlabel('RT (ms)')
    ax.set_ylabel('Accuracy')
    ax.set_title(label)
    ax.set_ylim(0.24, 1.04)
    colormap = pl.cm.gist_gray_r(np.linspace(0.4, 1, 4))
    legendelements = [Line2D([0], [0], color=colormap[0], lw=2,
                             label='0'),
                      Line2D([0], [0], color=colormap[1], lw=2,
                             label='0.25'),
                      Line2D([0], [0], color=colormap[2], lw=2,
                             label='0.5'),
                      Line2D([0], [0], color=colormap[3], lw=2,
                             label='1')]
    ax.legend(handles=legendelements, fontsize=7)
    # ax.legend([1, 0.5, 0.25, 0])
    return ax.get_position()


def pdf_cohs(df, ax, bins=np.linspace(0, 200, 41), yaxis=True):
    # ev_vals = np.unique(np.abs(coh))
    sound_len = df.sound_len.values
    coh = df.coh2.values
    colormap = pl.cm.gist_gray_r(np.linspace(0.4, 1, 4))
    num_subjs = len(df.subjid.unique())
    for i_coh, ev in enumerate([0, 0.25, 0.5, 1]):
        counts_all_rats = np.zeros((len(bins)-1, num_subjs))
        for i_s, subj in enumerate(df.subjid.unique()):
            index = (np.abs(coh) == ev) & (df.subjid == subj)
            counts_coh, bins_coh = np.histogram(sound_len[index], bins=bins)
            norm_counts = counts_coh/sum(counts_coh)
            counts_all_rats[:, i_s] = norm_counts
        norm_counts = np.nanmean(counts_all_rats, axis=1)
        error = np.nanstd(counts_all_rats, axis=1)/np.sqrt(num_subjs)
        xvals = bins_coh[:-1]+(bins_coh[1]-bins_coh[0])/2
        ax.plot(xvals, norm_counts, color=colormap[i_coh], label=str(ev))
        ax.fill_between(xvals, norm_counts-error, norm_counts+error,
                        color=colormap[i_coh], alpha=0.4)
    ax.set_xlabel('Reaction time (ms)')
    if yaxis:
        ax.set_ylabel('RT density')
    ax.legend()


def plot_rt_cohs_with_fb(df, ax, subj='LE46'):
    colormap = pl.cm.gist_yarg(np.linspace(0.3, 1, 4))
    df_1 = df[df.subjid == subj]
    coh_vec = df_1.coh2.values
    for ifb, fb in enumerate(df_1.fb):
        for j in range(len(fb)):
            coh_vec = np.append(coh_vec, [df_1.coh2.values[ifb]])
    for iev, ev in enumerate([0, 0.25, 0.5, 1]):
        index = np.abs(coh_vec) == ev
        fix_breaks =\
            np.vstack(np.concatenate([df_1.sound_len/1000,
                                      np.concatenate(df_1.fb.values)-0.3]))
        fix_breaks = fix_breaks[index]
        counts_coh, bins = np.histogram(fix_breaks*1000,
                                        bins=30, range=(-100, 200))
        norm_counts = counts_coh/sum(counts_coh)
        ax.plot(bins[:-1]+(bins[1]-bins[0])/2, norm_counts,
                color=colormap[iev])
    ax.set_ylabel('RT density')
    ax.set_xlabel('Reaction time (ms)')


# function to add letters to panel
def add_text(ax, letter, x=-0.1, y=1.2, fontsize=16):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=fontsize,
            fontweight='bold', va='top', ha='right')


def fig_rats_behav_1(df_data, figsize=(6, 6), margin=.05):
    mat_pright_all = np.zeros((7, 7))
    for subject in df_data.subjid.unique():
        df_sbj = df_data.loc[(df_data.special_trial == 0) &
                             (df_data.subjid == subject)]
        choice = df_sbj['R_response'].values
        coh = df_sbj['coh2'].values
        prior = df_sbj['norm_allpriors'].values
        indx = ~np.isnan(prior)
        mat_pright, _ = com_heatmap(prior[indx], coh[indx], choice[indx],
                                    return_mat=True, annotate=False)
        mat_pright_all += mat_pright
    mat_pright = mat_pright_all / len(df_data.subjid.unique())
    f, ax = plt.subplots(nrows=4, ncols=3, figsize=figsize)  # figsize=(4, 3))
    ax = ax.flatten()
    labs = ['', '',  'c', '', '', 'd', 'e', 'f', 'g']
    for n, ax_1 in enumerate(ax):
        rm_top_right_lines(ax_1)
        add_text(ax=ax_1, letter=labs[n], x=-0.15, y=1.2)
    for i in [0, 1, 3]:
        ax[i].axis('off')
    # TASK PANEL
    ax_task = ax[0]
    pos = ax_task.get_position()
    factor = 1.75
    ax_task.set_position([pos.x0+0.05, pos.y0-0.05, pos.width*factor, pos.height*factor])
    task = plt.imread(TASK_IMG)
    ax_task.imshow(task)
    add_text(ax=ax_task, letter='a', x=0.1, y=1.15)

    # P(RIGHT) MATRIX
    ax_pright = ax[4]
    im_2 = ax_pright.imshow(mat_pright, cmap='PRGn_r')
    pos = ax_pright.get_position()
    ax_pright.set_position([pos.x0-pos.width/1.6, pos.y0+margin/1.5, pos.width*.9,
                            pos.height*.9])
    cbar_ax = f.add_axes([pos.x0+pos.width/2.3, pos.y0+margin/2,
                          pos.width/10, pos.height/2])
    cbar_ax.set_title('p(Right)', fontsize=9)
    f.colorbar(im_2, cax=cbar_ax)
    ax_pright.set_yticks([0, 3, 6])
    ax_pright.set_ylim([-0.5, 6.5])
    ax_pright.set_yticklabels(['L', '', 'R'])
    ax_pright.set_xticks([0, 3, 6])
    ax_pright.set_xlim([-0.5, 6.5])
    ax_pright.set_xticklabels(['Left', '', 'Right'])
    ax_pright.set_xlabel('Prior Evidence')
    ax_pright.set_ylabel('Stimulus Evidence')
    add_text(ax=ax_pright, letter='b', x=-0.2, y=1.15)

    # RTs
    ax_rts = ax[2]
    rm_top_right_lines(ax=ax_rts)
    plot_rt_cohs_with_fb(df=df, ax=ax_rts, subj='LE46')
    ax_rts.set_xlabel('Reaction Time (ms)')
    ax_rts.set_ylabel('Density')
    ax_rts.set_xlim(-101, 201)
    ax_rts.axvline(x=0, linestyle='--', color='k', lw=0.5)
    pos = ax_rts.get_position()
    ax_rts.set_position([pos.x0, pos.y0+margin, pos.width, pos.height])
    add_text(ax=ax_rts, letter='rat LE46', x=0.32, y=1., fontsize=8)

    # TACHOMETRICS
    bin_size = 10
    ax_tach = ax[5]
    labels = ['0', '0.25', '0.5', '1']
    tachometric(df_data, ax=ax_tach, fill_error=True, cmap='gist_yarg',
                labels=labels, rtbins=np.arange(0, 201, bin_size))
    ax_tach.set_xlabel('Reaction Time (ms)')
    ax_tach.set_ylabel('Accuracy')
    ax_tach.set_ylim(0.5, 1.04)
    ax_tach.set_xlim(-101, 201)
    ax_tach.axvline(x=0, linestyle='--', color='k', lw=0.5)
    ax_tach.set_yticks([0.5, 0.75, 1])
    ax_tach.set_yticklabels(['0.5', '0.75', '1'])
    rm_top_right_lines(ax_tach)
    pos = ax_tach.get_position()
    ax_tach.set_position([pos.x0, pos.y0, pos.width, pos.height])
    add_text(ax=ax_tach, letter='rat LE46', x=0.32, y=1., fontsize=8)
    # REGRESSION WEIGHTS
    mt_weights(df, ax=ax[9], plot=True, means_errs=False)
    # MT MATRIX
    mt_matrix_vs_ev_zt(df=df, ax=ax[10], silent_comparison=False,
                       rt_bin=60, collapse_sides=True)
    # SLOWING
    plot_mt_vs_stim(df, ax[11], prior_min=0.8, rt_max=50)

    f.savefig(SV_FOLDER+'fig1.svg', dpi=400, bbox_inches='tight')
    f.savefig(SV_FOLDER+'fig1.png', dpi=400, bbox_inches='tight')
    # plt.show()


def groupby_binom_ci(x, method="beta"):
    # so we can plot groupby with errorbars in binomial vars in 2 lines
    return [abs(x.mean() - ci) for ci in
            proportion_confint(x.sum(), len(x), method=method)]


def tachs_values(df, evidence_bins=np.array([0, 0.15, 0.30, 0.60, 1.05]),
                 rtbins=np.arange(0, 151, 3), rt='sound_len',
                 evidence='avtrapz', hits='hithistory'):
    rtbinsize = rtbins[1]-rtbins[0]
    tmp_df = df
    tmp_df['rtbin'] = pd.cut(
        tmp_df[rt], rtbins, labels=np.arange(rtbins.size-1),
        retbins=False, include_lowest=True, right=True).astype(float)
    xvals = np.zeros((len(rtbins)-1, len(evidence_bins)-1))
    yvals = np.zeros((len(rtbins)-1, len(evidence_bins)-1))
    yerr = np.zeros((len(rtbins)-1, len(evidence_bins)-1))
    n_subjs = len(df.subjid.unique())
    vals_all_rats = np.zeros((len(rtbins)-1, n_subjs))
    for i in range(evidence_bins.size-1):
        for i_s, subj in enumerate(df.subjid.unique()):
            tmp = (tmp_df.loc[(tmp_df[evidence].abs() >= evidence_bins[i]) & (
                   tmp_df[evidence].abs() < evidence_bins[i+1]) &
                   (tmp_df.subjid == subj)]
                   .groupby('rtbin')[hits].agg(['mean',
                                                groupby_binom_ci]).reset_index())
            vals_all_rats[:len(tmp['mean'].values), i_s] = tmp['mean'].values
        xvals[:len(tmp.rtbin.values), i] =\
            tmp.rtbin.values * rtbinsize + 0.5 * rtbinsize
        yvals[:, i] = np.nanmean(vals_all_rats, axis=1)
        yerr[:, i] = np.nanstd(vals_all_rats, axis=1) / n_subjs
    xvals = xvals[:len(tmp['mean'].values), :]
    yvals = yvals[:len(tmp['mean'].values), :]
    return xvals, yvals, yerr


def mt_weights(df, ax, plot=False, means_errs=True, mt=True, t_index_w=False):
    w_coh = []
    w_t_i = []
    w_zt = []
    if ax is None and plot:
        fig, ax = plt.subplots(1)
    for subject in df.subjid.unique():
        df_1 = df.loc[df.subjid == subject]
        if mt:
            var = zscore(np.array(df_1.resp_len))
        else:
            var = zscore(np.array(df_1.sound_len))
        decision = np.array(df_1.R_response)*2 - 1
        coh = np.array(df_1.coh2)
        trial_index = np.array(df_1.origidx)
        com = df_1.CoM_sugg.values
        zt = df_1.allpriors.values
        params = mt_linear_reg(mt=var[~np.isnan(zt)],
                               coh=zscore(coh[~np.isnan(zt)] *
                                          decision[~np.isnan(zt)]),
                               trial_index=zscore(trial_index[~np.isnan(zt)].
                                                  astype(float)),
                               prior=zscore(zt[~np.isnan(zt)] *
                                            decision[~np.isnan(zt)]),
                               plot=False,
                               com=com[~np.isnan(zt)])
        w_coh.append(params[1])
        w_t_i.append(params[2])
        w_zt.append(params[3])
    mean_2 = np.nanmean(w_coh)
    mean_1 = np.nanmean(w_zt)
    std_2 = np.nanstd(w_coh)/np.sqrt(len(w_coh))
    std_1 = np.nanstd(w_zt)/np.sqrt(len(w_zt))
    errors = [std_1, std_2]  # , std_3
    means = [mean_1, mean_2]  # , mean_3
    if t_index_w:
        errors = [std_1, std_2, np.nanstd(w_t_i)/np.sqrt(len(w_t_i))]
        means = [mean_1, mean_2, np.nanmean(w_t_i)]
    if plot:
        if means_errs:
            plot_mt_weights_bars(means=means, errors=errors, ax=ax)
            rm_top_right_lines(ax=ax)
        else:
            plot_mt_weights_violins(w_coh=w_coh, w_t_i=w_t_i, w_zt=w_zt,
                                    ax=ax, mt=mt, t_index_w=t_index_w)
    if means_errs:
        return means, errors
    else:
        return w_coh, w_t_i, w_zt


def mt_weights_rt_bins(df, ax):
    n_subjects = len(df.subjid.unique())
    rtlims = [0, 30, 60, 150]
    nbins = len(rtlims) - 1
    w_coh = np.zeros((n_subjects, nbins))
    w_t_i = np.zeros((n_subjects, nbins))
    w_zt = np.zeros((n_subjects, nbins))
    if ax is None:
        fig, ax = plt.subplots(1)
    for irt, rt_lim in enumerate(rtlims[:-1]):
        for i_s, subject in enumerate(df.subjid.unique()):
            df_1 = df.loc[(df.subjid == subject) & (df.sound_len > rt_lim) &
                          (df.sound_len <= rtlims[irt+1])]
            resp_len = np.array(df_1.resp_len)
            decision = np.array(df_1.R_response)*2 - 1
            coh = np.array(df_1.coh2)
            trial_index = np.array(df_1.origidx)
            com = df_1.CoM_sugg.values
            zt = df_1.allpriors.values
            params = mt_linear_reg(mt=resp_len/max(resp_len),
                                   coh=coh*decision/max(np.abs(coh)),
                                   trial_index=trial_index/max(trial_index),
                                   prior=zt*decision/max(np.abs(zt)), plot=False,
                                   com=com)
            w_coh[i_s, irt] = params[1]
            w_t_i[i_s, irt] = params[2]
            w_zt[i_s, irt] = params[3]
    labels = ['RT < 30 ms', '30 < RT < 60 ms  \n Prior', '60 < RT < 150 ms',
              'RT < 30 ms ', '30 < RT < 60 ms  \n Stimulus', '60 < RT < 150 ms ']
    label_1 = []
    for j in range(len(labels)):
        for i in range(len(w_coh)):
            label_1.append(labels[j])
    ax.axhline(0, color='gray', alpha=0.4)
    arr_weights = np.concatenate((w_zt.flatten(), w_coh.flatten()))
    df_weights = pd.DataFrame({' ': label_1, 'weight': arr_weights})
    sns.violinplot(data=df_weights, x=" ", y="weight", ax=ax,
                   palette=['goldenrod', 'goldenrod', 'goldenrod', 'firebrick',
                            'firebrick', 'firebrick'],
                   linewidth=0.8)
    med_stim = np.nanmean(w_coh, axis=0)
    med_zt = np.nanmean(w_zt, axis=0)
    ax.plot([3, 4, 5], med_stim, color='k')
    ax.plot([0, 1, 2], med_zt, color='k')
    ax.set_ylabel('Impact on MT (weights, a.u)')


def plot_mt_weights_bars(means, errors, ax, f5=False, means_model=None,
                         errors_model=None, width=0.35):
    labels = ['Prior', 'Stimulus']  # , 'Trial index'
    if not f5:
        ax.bar(x=labels, height=means, yerr=errors, capsize=3, color='gray',
               ecolor='blue')
        ax.set_ylabel('Impact on MT (weights, a.u)')
    if f5:
        x = np.arange(len(labels))
        ax.bar(x=x-width/2, height=means, yerr=errors, width=width,
               capsize=3, color='k', label='Data', ecolor='blue')
        ax.bar(x=x+width/2, height=means_model, yerr=errors_model, width=width,
               capsize=3, color='red', label='Model')
        ax.set_ylabel('Impact on MT (weights, a.u)')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend(fontsize=8)


def plot_mt_weights_violins(w_coh, w_t_i, w_zt, ax, mt=True, t_index_w=False):
    if t_index_w:
        labels = ['Prior', 'Stimulus', 'Trial index']  # ]
        arr_weights = np.concatenate((w_zt, w_coh, w_t_i))
        palette = ['darkorange', 'red', 'steelblue']
    else:
        labels = ['Prior', 'Stimulus']  # ]
        arr_weights = np.concatenate((w_zt, w_coh))  #
        palette = ['darkorange', 'red']
    label_1 = []
    for j in range(len(labels)):
        for i in range(len(w_coh)):
            label_1.append(labels[j])
    df_weights = pd.DataFrame({' ': label_1, 'weight': arr_weights})

    sns.violinplot(data=df_weights, x=" ", y="weight", ax=ax,
                   palette=palette, linewidth=0.8)
    if t_index_w:
        arr_weights = np.array((w_zt, w_coh, w_t_i))
    else:
        arr_weights = np.array((w_zt, w_coh))
    for i in range(len(labels)):
        ax.plot(np.repeat(i, len(arr_weights[i])) +
                0.1*np.random.randn(len(arr_weights[i])),
                arr_weights[i], color='k', marker='o', linestyle='',
                markersize=2)
        ax.collections[0].set_edgecolor('k')
    if t_index_w:
        ax.set_xlim(-0.5, 2.5)
        ax.set_xticklabels([labels[0], labels[1], labels[2]], fontsize=9)
    else:
        ax.set_xlim(-0.5, 1.5)
        ax.set_xticklabels([labels[0], labels[1]], fontsize=9)
    if mt:
        ax.set_ylabel('Impact on MT (weights, a.u)')
    else:
        ax.set_ylabel('Impact on RT (weights, a.u)')
    ax.axhline(y=0, linestyle='--', color='k', alpha=.4)


def fig_trajs_2(df, fgsz=(8, 12), accel=False, inset_sz=.06, marginx=0.008,
                marginy=0.05):
    f = plt.figure(figsize=fgsz)
    # FIGURE LAYOUT
    # mt vs zt
    ax_label = f.add_subplot(5, 3, 1)
    add_text(ax_label, 'a', x=-0.1, y=1.2)
    # mt vs stim
    ax_label = f.add_subplot(5, 3, 2)
    add_text(ax_label, 'b', x=-0.1, y=1.2)
    ax_label = f.add_subplot(5, 3, 3)
    ax_label.axis('off')
    # trajs prior
    ax_label = f.add_subplot(5, 3, 4)
    add_text(ax_label, 'c', x=-0.1, y=1.2)
    # trajs stim
    ax_label = f.add_subplot(5, 3, 5)
    add_text(ax_label, 'd', x=-0.1, y=1.2)
    ax_label = f.add_subplot(5, 3, 6)
    ax_label.axis('off')
    # vel prior
    ax_label = f.add_subplot(5, 3, 7)
    add_text(ax_label, 'e', x=-0.1, y=1.2)
    ax_label = f.add_subplot(5, 3, 8)
    add_text(ax_label, 'f', x=-0.1, y=1.2)
    ax_label = f.add_subplot(5, 3, 9)
    ax_label.axis('off')
    ax_label = f.add_subplot(5, 3, 10)
    add_text(ax_label, 'g', x=-0.1, y=1.2)
    # weights linear reg
    ax_label = f.add_subplot(5, 3, 11)
    add_text(ax_label, 'h', x=-0.1, y=1.2)
    # mt mat
    ax_label = f.add_subplot(5, 3, 12)
    add_text(ax_label, 'i', x=-0.1, y=1.2)
    ax_label = f.add_subplot(5, 3, 13)
    add_text(ax_label, 'j', x=-0.1, y=3.0)
    ax_label = f.add_subplot(5, 3, 14)
    add_text(ax_label, 'k', x=-0.1, y=1.2)
    ax_label = f.add_subplot(5, 3, 15)
    add_text(ax_label, 'l', x=-0.1, y=1.2)
    # adjust panels positions
    plt.subplots_adjust(top=0.95, bottom=0.09, left=0.075, right=0.98,
                        hspace=0.5, wspace=0.4)
    ax = f.axes
    pos_ax_0 = ax[0].get_position()
    ax[0].set_position([pos_ax_0.x0, pos_ax_0.y0, pos_ax_0.width*1.6,
                        pos_ax_0.height])
    ax[1].set_position([pos_ax_0.x0 + pos_ax_0.width*2.2, pos_ax_0.y0,
                        pos_ax_0.width*1.6, pos_ax_0.height])
    pos_ax_3 = ax[3].get_position()
    ax[3].set_position([pos_ax_3.x0, pos_ax_3.y0, pos_ax_3.width*1.6,
                        pos_ax_3.height])
    ax[4].set_position([pos_ax_3.x0 + pos_ax_3.width*2.2, pos_ax_3.y0,
                        pos_ax_3.width*1.6, pos_ax_3.height])
    pos_ax_5 = ax[6].get_position()
    ax[6].set_position([pos_ax_5.x0, pos_ax_5.y0, pos_ax_5.width*1.6,
                        pos_ax_5.height])
    ax[7].set_position([pos_ax_5.x0 + pos_ax_5.width*2.2, pos_ax_5.y0,
                        pos_ax_5.width*1.6, pos_ax_5.height])
    ax_cohs = np.array([ax[1], ax[4], ax[7]])
    ax_zt = np.array([ax[0], ax[3], ax[6]])
    ax_inset = add_inset(ax=ax_cohs[2], inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=marginy, right=True)
    ax_inset.yaxis.set_ticks_position('none')
    ax_cohs = np.insert(ax_cohs, 2, ax_inset)
    ax_inset = add_inset(ax=ax_zt[2], inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=marginy, right=True)
    ax_inset.yaxis.set_ticks_position('none')
    ax_zt = np.insert(ax_zt, 2, ax_inset)
    ax_weights = ax[2]
    pos = ax_weights.get_position()
    ax_weights.set_position([pos.x0, pos.y0+pos.height/4, pos.width,
                             pos.height*1/2])
    for i_a, a in enumerate(ax):
        if i_a != 8:
            rm_top_right_lines(a)
    # TRACKING SCREENSHOT
    rat = plt.imread(RAT_noCOM_IMG)
    ax_scrnsht = ax[6]
    img = rat[150:646, 120:-10, :]
    ax_scrnsht.imshow(np.flipud(img)) # rat.shape = (796, 596, 4)
    ax_scrnsht.set_xticks([])
    right_port_y = 50
    center_port_y = 250
    left_port_y = 460
    ax_scrnsht.set_yticks([right_port_y, center_port_y, left_port_y])
    ax_scrnsht.set_yticklabels([-85, 0, 85])
    ax_scrnsht.set_ylim([0, img.shape[0]])
    ax_scrnsht.set_xlabel('x dimension (pixels)')
    ax_scrnsht.set_ylabel('y dimension (pixels)')

    # RAW TRAJECTORIES
    ax_rawtr = ax[7]
    ax_ydim = ax[8]
    ran_max = 100
    for tr in range(ran_max):
        if tr > (ran_max/2):
            trial = df.iloc[tr]
            traj_x = trial['trajectory_x']
            traj_y = trial['trajectory_y']
            ax_rawtr.plot(traj_x, traj_y, color='grey', lw=.5, alpha=0.6)
            time = trial['time_trajs']
            ax_ydim.plot(time, traj_y, color='grey', lw=.5, alpha=0.6)
    ax_rawtr.set_xlim(-80, 20)
    ax_rawtr.set_ylim(-100, 100)
    ax_rawtr.set_xticklabels([])
    ax_rawtr.set_yticklabels([])
    ax_rawtr.set_xticks([])
    ax_rawtr.set_yticks([])
    ax_rawtr.set_xlabel('x dimension (pixels)')
    add_text(ax=ax_rawtr, letter='rat LE46', x=0.7, y=1., fontsize=8)
    ax_ydim.set_xlim(-100, 800)
    ax_ydim.set_ylim(-100, 100)
    ax_ydim.set_yticks([])
    ax_ydim.set_xlabel('Time from movement onset (ms)')
    add_text(ax=ax_ydim, letter='rat LE46', x=0.32, y=1., fontsize=8)
    # adjust panels positions
    pos = ax_rawtr.get_position()
    factor = figsize[1]/figsize[0]
    width = pos.height*factor/2
    ax_rawtr.set_position([pos.x0+width*0.5, pos.y0-margin, width,
                           pos.height])
    pos = ax_ydim.get_position()
    ax_ydim.set_position([pos.x0, pos.y0-margin, pos.width, pos.height])
    pos = ax_scrnsht.get_position()
    ax_scrnsht.set_position([pos.x0+width*0.5, pos.y0-margin, pos.width,
                             pos.height])
    # add colorbar for screenshot
    n_stps = 100
    ax_clbr = plt.axes([pos.x0+width*0.5, pos.y0+pos.height-margin*0.9,
                        pos.width*0.7, pos.height/15])
    ax_clbr.imshow(np.linspace(0, 1, n_stps)[None, :], aspect='auto')
    x_tcks = np.linspace(0, n_stps, 6)
    ax_clbr.set_xticks(x_tcks)
    # pass xticks to strings
    x_tcks_str = ['0', '', '', '', '', str(4*n_stps)]
    x_tcks_str[-1] += ' ms'
    ax_clbr.set_xticklabels(x_tcks_str)
    ax_clbr.tick_params(labelsize=6)
    # ax_clbr.set_title('$N_{max}$', fontsize=6)
    ax_clbr.set_yticks([])
    ax_clbr.xaxis.set_ticks_position("top")
    # ax_clbr.yaxis.tick_right()
    # plot dashed lines
    for i_a in [7, 8]:
        ax[i_a].axhline(y=85, linestyle='--', color='k', lw=.5)
        ax[i_a].axhline(y=-80, linestyle='--', color='k', lw=.5)
        ax[i_a].axhline(0, color='k', lw=.5)
    ax[6].axhline(y=left_port_y, linestyle='--', color='k', lw=.5)
    ax[6].axhline(y=right_port_y, linestyle='--', color='k', lw=.5)
    ax_scrnsht.axhline(center_port_y, color='k', lw=.5)


    df_trajs = df.copy()
    # TRAJECTORIES CONDITIONED ON PRIOR
    plots_trajs_conditioned(df=df_trajs.loc[df_trajs.special_trial == 2],
                            ax=ax_zt, condition='choice_x_prior',
                            prior_limit=1, cmap='copper')
    # TRAJECTORIES CONDITIONED ON COH
    plots_trajs_conditioned(df=df_trajs, ax=ax_cohs,
                            prior_limit=0.1,  # 10% quantile
                            condition='choice_x_coh',
                            cmap='coolwarm')
    # SPLITTING TIME EXAMPLE
    ax_split = ax[12]
    pos = ax_split.get_position()
    ax_split.set_position([pos.x0, pos.y0, pos.width,
                           pos.height*2/5])
    ax_inset = plt.axes([pos.x0, pos.y0+pos.height*3/5, pos.width,
                         pos.height*2/5])
    axes_split = [ax_split, ax_inset]
    plot_trajs_splitting_example(df, ax=axes_split[1], rtbins=np.linspace(0, 15, 2),
                                 xlab=False)
    rm_top_right_lines(axes_split[1])
    rm_top_right_lines(axes_split[0])
    plot_trajs_splitting_example(df, ax=axes_split[0], rtbins=np.linspace(150, 300, 2),
                                 xlab=True)
    # TRAJECTORY SPLITTING PRIOR
    trajs_splitting_prior(df=df, ax=ax[14])
    # TRAJECTORY SPLITTING STIMULUS
    trajs_splitting_stim(df=df, ax=ax[13], connect_points=True)
    f.savefig(SV_FOLDER+'/Fig2.png', dpi=400, bbox_inches='tight')
    f.savefig(SV_FOLDER+'/Fig2.svg', dpi=400, bbox_inches='tight')


def supp_fig_traj_tr_idx(df, fgsz=(15, 5), accel=False, marginx=0.01,
                         marginy=0.05):
    fgsz = fgsz
    inset_sz = 0.08
    f, ax = plt.subplots(nrows=2, ncols=1, figsize=fgsz)
    ax = ax.flatten()
    ax_ti = np.array([ax[0], ax[1]])

    # trajs. conditioned on trial index
    ax_inset = add_inset(ax=ax[0], inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=marginy)
    ax_ti = np.insert(ax_ti, 0, ax_inset)
    ax_inset = add_inset(ax=ax[2], inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=marginy)
    ax_ti = np.insert(ax_ti, 2, ax_inset)
    for a in ax:
        rm_top_right_lines(a)
    plots_trajs_conditioned(df=df, ax=ax_ti, condition='choice_x_prior',
                            prior_limit=1, cmap='copper')
    # splits
    mt_weights(df, ax=ax[3], plot=True, means_errs=False)
    trajs_splitting_stim(df=df, ax=ax[7])
    f.savefig(SV_FOLDER+'/Fig2.png', dpi=400, bbox_inches='tight')
    f.savefig(SV_FOLDER+'/Fig2.svg', dpi=400, bbox_inches='tight')


def tach_1st_2nd_choice(df, ax, model=False, tachometric=False):
    # TODO: average across rats
    choice = df.R_response.values * 2 - 1
    coh = df.coh2.values
    gt = df.rewside.values * 2 - 1
    hit = df.hithistory.values
    sound_len = df.sound_len.values
    subj = df.subjid.values
    if not model:
        com = df.CoM_sugg.values
    if model:
        com = df.com_detected.values
    choice_com = choice
    choice_com[com] = -choice[com]
    hit_com = choice_com == gt
    df_plot_data = pd.DataFrame({'avtrapz': coh, 'hithistory': hit,
                                 'sound_len': sound_len, 'subjid': subj})
    if tachometric:
        xvals, yvals1, _ = tachs_values(df=df_plot_data,
                                        rtbins=np.arange(0, 151, 3))
        colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
        for j in range(4):
            ax.plot(xvals[:, j], yvals1[:, j], color=colormap[j], linewidth=1.5)
        df_plot_data = pd.DataFrame({'avtrapz': coh, 'hithistory': hit_com,
                                     'sound_len': sound_len, 'subjid': subj})
        xvals, yvals2, _ = tachs_values(df=df_plot_data,
                                        rtbins=np.arange(0, 151, 3))
        for j in range(4):
            ax.plot(xvals[:, j], yvals2[:, j], color=colormap[j], linestyle='--',
                    linewidth=1.5)
            ax.fill_between(xvals[:, j], yvals1[:, j], yvals2[:, j],
                            color=COLOR_COM, alpha=0.8)
        ax.set_xlabel('RT (ms)')
        ax.set_ylabel('Accuracy')
        ax.set_ylim(0.3, 1)
        legendelements = [Line2D([0], [0], linestyle='--', color='k', lw=2,
                                 label='initial trajectory'),
                          Line2D([0], [0], color='k', lw=2, label='final response')]
        ax.legend(handles=legendelements)
    else:
        mean_com = []
        mean_nocom = []
        err_com = []
        err_nocom = []
        nsubs = len(df.subjid.unique())
        ev_vals = [0, 0.25, 0.5, 1]
        pvals = [1e-2, 1e-3, 1e-4]
        for i_ev, ev in enumerate(ev_vals):
            mean_x_subj_com = []
            mean_x_subj_nocom = []
            # pv_per_sub = []
            for i_s, subj in enumerate(df.subjid.unique()):
                indx = (coh == ev) & (df.subjid == subj)
                h_nocom = hit_com[indx]
                h_com = hit[indx]
                mean_x_subj_com.append(np.nanmean(h_com))
                mean_x_subj_nocom.append(np.nanmean(h_nocom))
            _, pv = ttest_rel(mean_x_subj_com, mean_x_subj_nocom)
            if pv < pvals[0] and pv > pvals[1]:
                ax.text(ev-0.02, np.nanmean(h_com)+0.05, '*', fontsize=10)
            if pv < pvals[1] and pv > pvals[2]:
                ax.text(ev-0.02, np.nanmean(h_com)+0.05, '**', fontsize=10)
            if pv < pvals[2]:
                ax.text(ev-0.02, np.nanmean(h_com)+0.05, '***', fontsize=10)
            mean_com.append(np.nanmean(mean_x_subj_com))
            mean_nocom.append(np.nanmean(mean_x_subj_nocom))
            err_com.append(np.nanstd(mean_x_subj_com)/np.sqrt(nsubs))
            err_nocom.append(np.nanstd(mean_x_subj_nocom)/np.sqrt(nsubs))
        ax.errorbar(ev_vals, mean_com, yerr=err_com, marker='o', color=COLOR_COM,
                    label='Final trajectory', markersize=5)
        ax.errorbar(ev_vals, mean_nocom, yerr=err_nocom, marker='o',
                    color=COLOR_NO_COM, label='Initial trajectory', markersize=5)
        ax.set_xlabel('Stimulus evidence')
        ax.set_ylabel('Accuracy')
        ax.legend(loc='lower right')
        ax.set_xticks(ev_vals)


def com_statistics(peak_com, time_com, ax):
    ax2, ax1 = ax
    rm_top_right_lines(ax1)
    rm_top_right_lines(ax2)
    peak_com = np.array(peak_com)
    ax1.hist(peak_com/75*100, bins=70, range=(-100, -8/75*100), color=COLOR_COM)
    ax1.hist(peak_com/75*100, bins=10, range=(-8/75*100, -0), color=COLOR_NO_COM)
    ax1.set_yscale('log')
    ax1.axvline(-8/75*100, linestyle=':', color='r')
    ax1.set_xlim(-100, 5)
    ax1.set_xlabel('Deflection point (%)', fontsize=8)
    ax1.set_ylabel('# Trials')
    ax2.set_ylabel('# Trials')
    ax2.hist(time_com, bins=80, range=(0, 500), color=COLOR_COM)
    ax2.set_xlabel('Deflection time (ms)', fontsize=8)


def mt_distros(df, ax, median_lines=False, mtbins=np.linspace(50, 800, 26),
               sim=False):
    subjid = df.subjid
    mt_com_mat = np.empty((len(mtbins)-1, len(subjid.unique())))
    mt_nocom_mat = np.empty((len(mtbins)-1, len(subjid.unique())))
    for i_s, subject in enumerate(subjid.unique()):
        mt_nocom = df.loc[(df.CoM_sugg == 0) & (subjid == subject),
                          'resp_len'].values*1e3
        mt_nocom = mt_nocom[(mt_nocom <= 1000) * (mt_nocom > 50)]
        if sim:
            mt_com = df.loc[(df.com_detected == 1) & (subjid == subject),
                            'resp_len'].values*1e3
        else:
            mt_com = df.loc[(df.CoM_sugg == 1) & (subjid == subject),
                            'resp_len'].values*1e3
        mt_com = mt_com[(mt_com <= 1000) & (mt_com > 50)]
        counts_com, bins = np.histogram(mt_com, bins=mtbins)
        counts_nocom, bins = np.histogram(mt_nocom, bins=mtbins)
        xvals = bins[:-1]+(bins[1]-bins[0])/2
        ax.plot(xvals, counts_com/sum(counts_com), color=COLOR_COM, alpha=0.3,
                linewidth=1)
        ax.plot(xvals, counts_nocom/sum(counts_nocom), color=COLOR_NO_COM, alpha=0.3,
                linewidth=1)
        mt_com_mat[:, i_s] = counts_com/sum(counts_com)
        mt_nocom_mat[:, i_s] = counts_nocom/sum(counts_nocom)
    ax.plot(xvals, np.nanmean(mt_com_mat, axis=1), color=COLOR_COM,
            label='Detected Rev.', linewidth=1.6)
    ax.plot(xvals, np.nanmean(mt_nocom_mat, axis=1), color=COLOR_NO_COM,
            label='No-Rev.', linewidth=1.6)
    if median_lines:
        ax.axvline(np.nanmedian(mt_nocom), color='k')
        ax.axvline(np.nanmedian(mt_com), color='k')
    ax.set_xlim(45, 755)
    ax.legend()
    ax.set_xlabel('MT (ms)')
    ax.set_ylabel('Density')


def fig_CoMs_3(df, peak_com, time_com, inset_sz=.07, marginx=-0.2,
               marginy=0.05, figsize=(8, 10), com_th=8):
    if com_th != 8:
        _, _, _, com = edd2.com_detection(trajectories=traj_y, decision=decision,
                                          time_trajs=time_trajs)
        com = np.array(com)  # new CoM list
        df['CoM_sugg'] = com
    fig, ax = plt.subplots(4, 3, figsize=figsize)
    ax = ax.flatten()
    plt.subplots_adjust(top=0.95, bottom=0.09, left=0.09, right=0.95,
                        hspace=0.5, wspace=0.4)
    pos_ax_0 = ax[0].get_position()
    ax[0].set_position([pos_ax_0.x0, pos_ax_0.y0, pos_ax_0.width*0.8,
                        pos_ax_0.height])
    ax[1].set_position([pos_ax_0.x0 + pos_ax_0.width*1.2, pos_ax_0.y0,
                        pos_ax_0.width*1.4, pos_ax_0.height])
    pos_ax_2 = ax[2].get_position()
    ax[2].set_position([pos_ax_2.x0 + pos_ax_0.width*0.2,
                        pos_ax_2.y0 + pos_ax_2.height/6,
                        pos_ax_2.width*0.8, pos_ax_2.height*4/6])
    labs = ['a', 'b', '', 'c', 'd', 'e', 'f', '', 'g', 'h', '', '']
    for n, axis in enumerate(ax):
        if n == 4:
            axis.text(-0.1, 3, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 1:
            axis.text(-0.1, 1.05, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 6:
            axis.text(-0.1, 1.3, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        else:
            axis.text(-0.1, 1.2, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
    ax_mat = [ax[6], ax[7]]
    rm_top_right_lines(ax=ax[5])
    plot_proportion_corr_com_vs_stim(df, ax[5])
    fig2.e(df, sv_folder=SV_FOLDER, ax=ax[8])
    ax[8].set_ylim(0, 0.075)
    plot_coms_single_session(df=df, ax=ax[1])
    ax_trck = ax[0]
    tracking_image(ax_trck)
    ax_com_stat = ax[4]
    pos = ax_com_stat.get_position()
    ax_com_stat.set_position([pos.x0, pos.y0, pos.width,
                              pos.height*2/5])
    ax_inset = plt.axes([pos.x0, pos.y0+pos.height*3/5, pos.width,
                         pos.height*2/5])
    ax_coms = [ax_com_stat, ax_inset]
    com_statistics(peak_com=peak_com, time_com=time_com, ax=[ax_coms[1],
                                                             ax_coms[0]])
    rm_top_right_lines(ax=ax[2])
    mean_com_traj(df=df, ax=ax[3], condition='choice_x_prior', cmap='copper',
                  prior_limit=1, after_correct_only=True, rt_lim=400,
                  trajectory='trajectory_y',
                  interpolatespace=np.linspace(-700000, 1000000, 1700))
    # plot Pcoms matrices
    n_subjs = len(df.subjid.unique())
    mat_side_0_all = np.zeros((7, 7, n_subjs))
    mat_side_1_all = np.zeros((7, 7, n_subjs))
    for i_s, subj in enumerate(df.subjid.unique()):
        matrix_side_0 =\
            com_heatmap_marginal_pcom_side_mat(df=df.loc[df.subjid == subj],
                                               side=0)
        matrix_side_1 =\
            com_heatmap_marginal_pcom_side_mat(df=df.loc[df.subjid == subj],
                                               side=1)
        mat_side_0_all[:, :, i_s] = matrix_side_0
        mat_side_1_all[:, :, i_s] = matrix_side_1
    matrix_side_0 = np.nanmean(mat_side_0_all, axis=2)
    matrix_side_1 = np.nanmean(mat_side_1_all, axis=2)
    # L-> R
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
    pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[0].set_title(pcomlabel_0)
    im = ax_mat[0].imshow(matrix_side_1, vmin=-3e-2, vmax=vmax, cmap='magma')
    plt.sca(ax_mat[0])
    plt.colorbar(im, fraction=0.04)
    ax_mat[1].set_title(pcomlabel_1)
    im = ax_mat[1].imshow(matrix_side_0, vmin=-3e-2, vmax=vmax, cmap='magma')
    ax_mat[1].yaxis.set_ticks_position('none')
    plt.sca(ax_mat[1])
    cbar = plt.colorbar(im, fraction=0.04)
    cbar.set_label('p(detected CoM)', rotation=270)
    for ax_i in [ax_mat[0], ax_mat[1]]:
        ax_i.set_xlabel('Prior Evidence')
        ax_i.set_yticks([0, 3, 6], ['R', '0', 'L'])
        ax_i.set_xticks([0, 3, 6], ['L', '0', 'R'])
    for ax_i in [ax_mat[0]]:
        ax_i.set_ylabel('Stimulus Evidence')
    fig_COMs_per_rat_inset_3(df=df, ax_inset=ax[2])
    rm_top_right_lines(ax=ax[9])
    mt_distros(df=df, ax=ax[9])
    fig.savefig(SV_FOLDER+'fig3.svg', dpi=400, bbox_inches='tight')
    fig.savefig(SV_FOLDER+'fig3.png', dpi=400, bbox_inches='tight')


def fig_COMs_per_rat_inset_3(df, ax_inset):
    subjects = df.subjid.unique()
    comlist_rats = []
    for subj in subjects:
        df_1 = df.loc[df.subjid == subj]
        mean_coms = np.nanmean(df_1.CoM_sugg.values)
        comlist_rats.append(mean_coms)
    ax_inset.boxplot(comlist_rats)
    ax_inset.plot(1+np.random.randn(len(comlist_rats))*0.2, comlist_rats, 'o',
                  color='grey', alpha=0.4)
    ax_inset.set_xticks([])
    ax_inset.set_ylabel('P(CoM)')
    # ax_inset.set_ylabel('# Rats')


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
    bins_zt = [-1.01]
    for i_p, perc in enumerate([0.75, 0.5, 0.25, 0.25, 0.5, 0.75]):
        if i_p > 2:
            bins_zt.append(df.norm_allpriors.abs().quantile(perc))
        else:
            bins_zt.append(-df.norm_allpriors.abs().quantile(perc))
    bins_zt.append(1.01)
    com_heatmap_kws.update({
        'return_mat': True,
        'predefbins': None
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


def mean_com_traj_simul(df_sim, ax):
    raw_com = df_sim.CoM_sugg.values
    index_com = df_sim.com_detected.values
    trajs_all = df_sim.trajectory_y.values
    dec = df_sim.R_response.values*2-1
    max_ind = max([len(tr) for tr in trajs_all])
    subjects = df_sim.subjid.unique()
    matrix_com_tr = np.empty((len(subjects), max_ind))
    matrix_com_tr[:] = np.nan
    matrix_com_und_tr = np.empty((len(subjects), max_ind))
    matrix_com_und_tr[:] = np.nan
    matrix_nocom_tr = np.empty((len(subjects), max_ind))
    matrix_nocom_tr[:] = np.nan
    for i_s, subject in enumerate(subjects):
        it_subs = np.where(df_sim.subjid.values == subject)[0][0]
        i_com = 0
        i_nocom = 0
        i_und_com = 0
        mat_nocom_erase = np.empty((sum(~(index_com & raw_com)), max_ind))
        mat_nocom_erase[:] = np.nan
        mat_com_erase = np.empty((sum(index_com), max_ind))
        mat_com_erase[:] = np.nan
        mat_com_und_erase = np.empty((sum((~index_com) & (raw_com)), max_ind))
        mat_com_und_erase[:] = np.nan
        for i_t, traj in enumerate(trajs_all[df_sim.subjid == subject]):
            if index_com[i_t+it_subs]:
                mat_com_erase[i_com, :len(traj)] = traj*dec[i_t+it_subs]
                i_com += 1
            if not index_com[i_t+it_subs] and not raw_com[i_t]:
                mat_nocom_erase[i_nocom, :len(traj)] = traj*dec[i_t+it_subs]
                i_nocom += 1
            if raw_com[i_t+it_subs]:
                mat_com_und_erase[i_und_com, :len(traj)] = traj*dec[i_t+it_subs]
                i_und_com += 1
        mean_com_traj = np.nanmean(mat_com_erase, axis=0)
        matrix_com_tr[i_s, :len(mean_com_traj)] = mean_com_traj
        ax.plot(np.arange(len(mean_com_traj)), mean_com_traj, color=COLOR_COM,
                linewidth=1.4, alpha=0.25)
        mean_nocom_tr = np.nanmean(mat_nocom_erase, axis=0)
        matrix_nocom_tr[i_s, :len(mean_nocom_tr)] = mean_nocom_tr
        mean_com_und_traj = np.nanmean(mat_com_und_erase, axis=0)
        matrix_com_und_tr[i_s, :len(mean_com_und_traj)] = mean_com_und_traj
    mean_com_traj = np.nanmean(matrix_com_tr, axis=0)
    mean_nocom_traj = np.nanmean(matrix_nocom_tr, axis=0)
    mean_com_all_traj = np.nanmean(matrix_com_und_tr, axis=0)
    ax.plot(np.arange(len(mean_com_traj)), mean_com_traj, color=COLOR_COM,
            linewidth=2)
    ax.plot(np.arange(len(mean_com_all_traj)), mean_com_all_traj, color=COLOR_COM,
            linewidth=1.4, linestyle='--')
    ax.plot(np.arange(len(mean_nocom_traj)), mean_nocom_traj, color=COLOR_NO_COM,
            linewidth=2)
    legendelements = [Line2D([0], [0], color=COLOR_COM, lw=2,
                             label='Detected Rev.'),
                      Line2D([0], [0], color=COLOR_COM, lw=1.5,  linestyle='--',
                             label='All Rev.'),
                      Line2D([0], [0], color=COLOR_NO_COM, lw=2,
                             label='No-Rev.')]
    ax.legend(handles=legendelements, loc='upper left')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Position (pixels)')
    ax.set_xlim(-25, 400)
    ax.set_ylim(-25, 80)
    ax.axhline(-8, color='r', linestyle=':')
    ax.text(200, -16, "Detection threshold", color='r')


def fig_5(coh, sound_len, hit_model, sound_len_model, zt,
          decision_model, com, com_model, com_model_detected,
          df_sim, means, errors, means_model, errors_model, inset_sz=.06,
          marginx=0.006, marginy=0.07, fgsz=(8, 18)):
    matplotlib.rcParams['font.size'] = 10
    plt.rcParams['legend.title_fontsize'] = 9
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    fig, ax = plt.subplots(ncols=2, nrows=7,
                           gridspec_kw={'top': 0.95, 'bottom': 0.055, 'left': 0.07,
                                        'right': 0.95, 'hspace': 0.5, 'wspace': 0.4},
                           figsize=fgsz)
    ax = ax.flatten()
    labs = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n']
    # set correct size for traj and velocity axis
    pos_ax_0 = ax[0].get_position()
    ax[0].set_position([pos_ax_0.x0-pos_ax_0.x0/8, pos_ax_0.y0, pos_ax_0.width,
                        pos_ax_0.height])
    pos_ax_0 = ax[10].get_position()
    ax[10].set_position([pos_ax_0.x0 + pos_ax_0.width/10, pos_ax_0.y0,
                         pos_ax_0.width/2,
                         pos_ax_0.height])
    ax_inset = plt.axes([pos_ax_0.x0 + pos_ax_0.width*0.8 + pos_ax_0.width/10,
                         pos_ax_0.y0, pos_ax_0.width/2, pos_ax_0.height])
    ax[11].set_position([pos_ax_0.x0 + pos_ax_0.width*1.2 + pos_ax_0.width/10,
                         pos_ax_0.y0, pos_ax_0.width/2, pos_ax_0.height])
    # letters for panels
    for n, ax_1 in enumerate(ax):
        rm_top_right_lines(ax_1)
        ax_1.text(-0.1, 1.4, labs[n], transform=ax_1.transAxes, fontsize=16,
                  fontweight='bold', va='top', ha='right')

    # select RT > 0 (no FB, as in data)
    hit_model = hit_model[sound_len_model >= 0]
    com_model_detected = com_model_detected[sound_len_model >= 0]
    decision_model = decision_model[sound_len_model >= 0]
    com_model = com_model[sound_len_model >= 0]
    subjid = df_sim.subjid.values
    _ = tachometric_data(coh=coh[sound_len_model >= 0], hit=hit_model,
                         sound_len=sound_len_model[sound_len_model >= 0],
                         subjid=subjid,
                         ax=ax[1], label='')
    ax2 = add_inset(ax=ax[13], inset_sz=inset_sz, fgsz=fgsz,
                    marginx=marginx, marginy=0.07, right=True)
    df_plot_pcom = pd.DataFrame({'com': com[sound_len_model >= 0],
                                 'sound_len': sound_len[sound_len_model >= 0],
                                 'rt_model': sound_len_model[sound_len_model >= 0],
                                 'com_model': com_model,
                                 'com_model_detected': com_model_detected,
                                 'subjid': subjid})
    subjects = np.unique(subjid)
    com_data = np.empty((len(subjects), len(BINS_RT)-1))
    com_data[:] = np.nan
    com_model_all = np.empty((len(subjects), len(BINS_RT)-1))
    com_model_all[:] = np.nan
    com_model_det = np.empty((len(subjects), len(BINS_RT)-1))
    com_model_det[:] = np.nan
    for i_s, subject in enumerate(subjects):
        df_plot = df_plot_pcom.loc[subjid == subject]
        xpos_plot, median_pcom_dat, _ =\
            binned_curve(df_plot, 'com', 'sound_len', bins=BINS_RT, xpos=xpos_RT,
                         errorbar_kw={'label': 'Data', 'color': 'k'}, ax=ax[13],
                         legend=False, return_data=True)
        xpos_plot, median_pcom_mod_det, _ =\
            binned_curve(df_plot, 'com_model_detected', 'rt_model', bins=BINS_RT,
                         xpos=xpos_RT, errorbar_kw={'label': 'Model detected',
                                                    'color': 'red'}, ax=ax[13],
                         legend=False, return_data=True)
        xpos_plot, median_pcom_mod_all, _ =\
            binned_curve(df_plot, 'com_model', 'rt_model', bins=BINS_RT,
                         xpos=xpos_RT,
                         errorbar_kw={'label': 'Model all', 'color': 'green'},
                         ax=ax2, legend=False, return_data=True)
        com_data[i_s, :len(median_pcom_dat)] = median_pcom_dat
        com_model_all[i_s, :len(median_pcom_mod_all)] = median_pcom_mod_all
        com_model_det[i_s, :len(median_pcom_mod_det)] = median_pcom_mod_det
    xpos_plot = (BINS_RT[:-1] + BINS_RT[1:]) / 2
    ax[13].errorbar(xpos_plot, np.nanmedian(com_data, axis=0),
                    yerr=np.nanstd(com_data, axis=0)/len(subjects), color='k')
    ax[13].errorbar(xpos_plot, np.nanmedian(com_model_det, axis=0),
                    yerr=np.nanstd(com_model_det, axis=0)/len(subjects), color='r')
    ax2.errorbar(xpos_plot, np.nanmedian(com_model_all, axis=0),
                 yerr=np.nanstd(com_model_all, axis=0)/len(subjects), color='green')
    ax[13].xaxis.tick_top()
    ax[13].xaxis.tick_bottom()
    legendelements = [Line2D([0], [0], color='k', lw=2,
                             label='Data'),
                      Line2D([0], [0], color='r', lw=2,
                             label='Model Detected'),
                      Line2D([0], [0], color='green', lw=2,
                             label='Model All')]
    ax[13].legend(handles=legendelements)
    ax[13].set_xlabel('RT (ms)')
    ax[13].set_ylabel('P(CoM)')
    ax2.set_ylabel('P(CoM)')
    ax2.set_xlabel('RT (ms)')
    zt_model = df_sim.norm_allpriors.values
    coh_model = coh[sound_len_model >= 0]
    decision_01_model = (decision_model+1)/2
    mat_pright = np.zeros((7, 7, len(subjects)))
    for i_s, subject in enumerate(subjects):
        mat_per_subj, _ = com_heatmap(zt_model[subjid == subject],
                                      coh_model[subjid == subject],
                                      decision_01_model[subjid == subject],
                                      return_mat=True, annotate=False)
        mat_pright[:, :, i_s] = mat_per_subj
    mat_pright_avg = np.nanmean(mat_pright, axis=2)
    # P_right
    ax_pright = ax[0]
    im = ax_pright.imshow(np.flipud(mat_pright_avg), vmin=0., vmax=1, cmap='PRGn_r')
    plt.sca(ax_pright)
    cbar = plt.colorbar(im, fraction=0.04)
    cbar.set_label('p(Right)', rotation=270)
    ax_pright.set_yticks([0, 3, 6])
    # ax_pright.set_ylim([-0.5, 6.5])
    ax_pright.set_yticklabels(['L', '', 'R'])
    ax_pright.set_xticks([0, 3, 6])
    # ax_pright.set_xlim([-0.5, 6.5])
    ax_pright.set_xticklabels(['L', '', 'R'])
    ax_pright.set_xlabel('Prior Evidence')
    ax_pright.set_ylabel('Stimulus Evidence')
    # ax[7].set_title('Pright Model')
    df_model = pd.DataFrame({'avtrapz': coh[sound_len_model >= 0],
                             'CoM_sugg':
                                 com_model_detected,
                             'norm_allpriors':
                                 zt_model/max(abs(zt_model)),
                             'R_response': (decision_model+1)/2,
                             'subjid': subjid})
    df_model = df_model.loc[~df_model.norm_allpriors.isna()]
    nbins = 7
    # plot Pcoms matrices
    ax_mat = [ax[10], ax_inset]
    n_subjs = len(df.subjid.unique())
    mat_side_0_all = np.zeros((7, 7, n_subjs))
    mat_side_1_all = np.zeros((7, 7, n_subjs))
    for i_s, subj in enumerate(df_sim.subjid.unique()):
        matrix_side_0 =\
            com_heatmap_marginal_pcom_side_mat(
                df=df_model.loc[df_model.subjid == subj], side=0)
        matrix_side_1 =\
            com_heatmap_marginal_pcom_side_mat(
                df=df_model.loc[df_model.subjid == subj], side=1)
        mat_side_0_all[:, :, i_s] = matrix_side_0
        mat_side_1_all[:, :, i_s] = matrix_side_1
    matrix_side_0 = np.nanmean(mat_side_0_all, axis=2)
    matrix_side_1 = np.nanmean(mat_side_1_all, axis=2)
    # L-> R
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
    pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[0].set_title(pcomlabel_0)
    im = ax_mat[0].imshow(matrix_side_1, vmin=0, vmax=vmax, cmap='magma')
    # plt.sca(ax_mat[0])
    # plt.colorbar(im, fraction=0.04)
    ax_mat[1].set_title(pcomlabel_1)
    im = ax_mat[1].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
    ax_mat[1].yaxis.set_ticks_position('none')

    for ax_i in [ax[10], ax_inset]:
        ax_i.set_xlabel('Prior Evidence')
        ax_i.set_yticklabels(['']*nbins)
        ax_i.set_xticklabels(['']*nbins)
    ax[10].set_ylabel('Stimulus Evidence')
    ax[0].set_ylabel('Stimulus Evidence')
    mt_matrix_vs_ev_zt(df_sim, ax[11], silent_comparison=False, collapse_sides=True)
    ax[10].set_position([pos_ax_0.x0 + pos_ax_0.width/10, pos_ax_0.y0,
                         pos_ax_0.width/2,
                         pos_ax_0.height])
    ax_inset.set_position([pos_ax_0.x0 + pos_ax_0.width*0.6 + pos_ax_0.width/15,
                           pos_ax_0.y0, pos_ax_0.width/2, pos_ax_0.height])
    plt.sca(ax_mat[1])
    cbar = plt.colorbar(im, fraction=0.04)
    cbar.set_label('p(detected CoM)', rotation=270)
    ax[11].set_position([pos_ax_0.x0 + pos_ax_0.width*1.4 + pos_ax_0.width/10,
                         pos_ax_0.y0, pos_ax_0.width/1.5, pos_ax_0.height])
    mt_distros(df=df_sim, ax=ax[12])
    ax_cohs = np.array([ax[5], ax[7], ax[3]])
    ax_zt = np.array([ax[4], ax[6], ax[2]])

    ax_inset = add_inset(ax=ax_cohs[1], inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=marginy, right=True)
    ax_cohs = np.insert(ax_cohs, 3, ax_inset)

    ax_inset = add_inset(ax=ax_zt[1], inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=marginy, right=True)
    ax_zt = np.insert(ax_zt, 3, ax_inset)
    if sum(df_sim.special_trial == 2) > 0:
        traj_cond_coh_simul(df_sim=df_sim[df_sim.special_trial == 2], ax=ax_zt,
                            median=True, prior=True, rt_lim=300)
    else:
        print('No silent trials')
        traj_cond_coh_simul(df_sim=df_sim, ax=ax_zt,
                            median=True, prior=True)
    traj_cond_coh_simul(df_sim=df_sim, ax=ax_cohs, median=True, prior=False,
                        prior_lim=np.quantile(df_sim.norm_allpriors.abs(), 0.1))
    trajs_splitting_stim(df_sim.loc[df_sim.special_trial == 0],
                         ax=ax[8], collapse_sides=True, threshold=500,
                         sim=True,
                         rtbins=np.linspace(0, 150, 16), connect_points=True,
                         draw_line=((0, 90), (90, 0)),
                         trajectory="trajectory_y")
    mean_com_traj_simul(df_sim, ax=ax[9])
    fig.savefig(SV_FOLDER+'fig5.svg', dpi=400, bbox_inches='tight')
    fig.savefig(SV_FOLDER+'fig5.png', dpi=400, bbox_inches='tight')


def traj_cond_coh_simul(df_sim, ax=None, median=True, prior=True,
                        prior_lim=1, rt_lim=200):
    # TODO: save each matrix? or save the mean and std
    df_sim = df_sim[df_sim.sound_len >= 0]
    if median:
        func_final = np.nanmedian
    if not median:
        func_final = np.nanmean
    # nanidx = df_sim.loc[df_sim.allpriors.isna()].index
    # df_sim.loc[nanidx, 'allpriors'] = np.nan
    df_sim['choice_x_coh'] = (df_sim.R_response*2-1) * df_sim.coh2
    bins_coh = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]
    bins_zt = [1.01]
    for i_p, perc in enumerate([0.75, 0.5, 0.25, 0.25, 0.5, 0.75]):
        if i_p < 3:
            bins_zt.append(df.norm_allpriors.abs().quantile(perc))
        else:
            bins_zt.append(-df.norm_allpriors.abs().quantile(perc))
    bins_zt.append(-1.01)
    bins_zt = bins_zt[::-1]
    xvals_zt = [-1, -0.666, -0.333, 0, 0.333, 0.666, 1]
    signed_response = df_sim.R_response.values
    df_sim['normallpriors'] = df_sim['allpriors'] /\
        np.nanmax(df_sim['allpriors'].abs())*(signed_response*2 - 1)
    if ax is None:
        fig, ax = plt.subplots(nrows=2, ncols=2)
        ax = ax.flatten()
    labels_zt = ['inc.', ' ', ' ', '0', ' ', ' ', 'cong.']
    labels_coh = ['-1', ' ', ' ', '0', ' ', ' ', '1']
    if prior:
        bins_ref = bins_zt
        colormap = pl.cm.copper(np.linspace(0, 1, len(bins_zt)-1))
    else:
        bins_ref = bins_coh
        colormap = pl.cm.coolwarm(np.linspace(0, 1, len(bins_coh)))
    subjects = df_sim.subjid
    max_mt = 1000
    mat_trajs_subs = np.empty((len(bins_ref), max_mt,
                               len(subjects.unique())))
    mat_vel_subs = np.empty((len(bins_ref), max_mt,
                             len(subjects.unique())))
    if prior:
        val_traj_subs = np.empty((len(bins_ref)-1, len(subjects.unique())))
        val_vel_subs = np.empty((len(bins_ref)-1, len(subjects.unique())))
    else:
        val_traj_subs = np.empty((len(bins_ref), len(subjects.unique())))
        val_vel_subs = np.empty((len(bins_ref), len(subjects.unique())))
    for i_s, subject in enumerate(subjects.unique()):
        vals_thr_traj = []
        vals_thr_vel = []
        lens = []
        for i_ev, ev in enumerate(bins_ref):
            if not prior:
                index = (df_sim.choice_x_coh.values == ev) *\
                    (df_sim.normallpriors.abs() <= prior_lim) *\
                    (df_sim.special_trial == 0) * (~np.isnan(df_sim.allpriors)) *\
                    (df_sim.sound_len >= 0) * (df_sim.sound_len <= rt_lim) *\
                    (subjects == subject)
            if prior:
                if ev == 1.01:
                    break
                index = (df_sim.normallpriors.values >= bins_zt[i_ev]) *\
                    (df_sim.normallpriors.values < bins_zt[i_ev + 1]) *\
                    (df_sim.sound_len >= 0) * (df_sim.sound_len <= rt_lim) *\
                    (subjects == subject)
                if sum(index) == 0:
                    continue
            lens.append(max([len(t) for t in df_sim.trajectory_y[index].values]))
            traj_all = np.empty((sum(index), max(lens)))
            traj_all[:] = np.nan
            vel_all = np.empty((sum(index), max(lens)))
            vel_all[:] = np.nan
            for tr in range(sum(index)):
                vals_traj = df_sim.traj[index].values[tr] *\
                    (signed_response[index][tr]*2 - 1)
                if sum(vals_traj) == 0:
                    continue
                vals_traj = np.concatenate((vals_traj,
                                            np.repeat(75, max(lens)-len(vals_traj))))
                vals_vel = df_sim.traj_d1[index].values[tr] *\
                    (signed_response[index][tr]*2 - 1)
                vals_vel = np.diff(vals_traj)
                traj_all[tr, :len(vals_traj)] = vals_traj
                vel_all[tr, :len(vals_vel)] = vals_vel
            try:
                index_vel = np.where(np.sum(np.isnan(traj_all), axis=0)
                                     > traj_all.shape[0] - 50)[0][0]
                mean_traj = func_final(traj_all[:, :index_vel], axis=0)
                std_traj = np.nanstd(traj_all[:, :index_vel],
                                     axis=0) / np.sqrt(sum(index))
            except Exception:
                mean_traj = func_final(traj_all, axis=0)
                std_traj = np.nanstd(traj_all, axis=0) / np.sqrt(sum(index))
            val_traj = np.mean(df_sim['resp_len'].values[index])*1e3
            vals_thr_traj.append(val_traj)
            mean_vel = func_final(vel_all, axis=0)
            std_vel = np.nanstd(vel_all, axis=0) / np.sqrt(sum(index))
            val_vel = np.nanmax(mean_vel)  # func_final(np.nanmax(vel_all, axis=1))
            vals_thr_vel.append(val_vel)
            mat_trajs_subs[i_ev, :len(mean_traj), i_s] = mean_traj
            mat_vel_subs[i_ev, :len(mean_vel), i_s] = mean_vel
        val_traj_subs[:len(vals_thr_traj), i_s] = vals_thr_traj
        val_vel_subs[:len(vals_thr_vel), i_s] = vals_thr_vel
    for i_ev, ev in enumerate(bins_ref):
        if prior:
            if ev == 1.01:
                break
        val_traj = np.nanmean(val_traj_subs[i_ev, :])
        val_vel = np.nanmean(val_vel_subs[i_ev, :])
        mean_traj = np.nanmean(mat_trajs_subs[i_ev, :, :], axis=1)
        std_traj = np.std(mat_trajs_subs[i_ev, :, :], axis=1) /\
            np.sqrt(len(subjects.unique()))
        mean_vel = np.nanmean(mat_vel_subs[i_ev, :, :], axis=1)
        std_vel = np.std(mat_vel_subs[i_ev, :, :], axis=1) /\
            np.sqrt(len(subjects.unique()))
        if prior:
            xval = xvals_zt[i_ev]
        else:
            xval = ev
        ax[2].scatter(xval, val_traj, color=colormap[i_ev], marker='o', s=25)
        ax[3].scatter(xval, val_vel, color=colormap[i_ev], marker='o', s=25)
        if not prior:
            label = labels_coh[i_ev]
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
    ax[0].axhline(y=75, linestyle='--', color='k', alpha=0.4)
    ax[0].set_xlim(-5, 460)
    ax[0].set_ylim(-10, 85)
    ax[1].set_ylim(-0.08, 0.68)
    ax[1].set_xlim(-5, 460)
    if prior:
        leg_title = 'Prior'
        ax[2].plot(xvals_zt, np.nanmean(val_traj_subs, axis=1),
                   color='k', linestyle='--', alpha=0.6)
        ax[3].plot(xvals_zt, np.nanmean(val_vel_subs, axis=1),
                   color='k', linestyle='--', alpha=0.6)
        ax[2].set_xlabel('Prior', fontsize=8)
        ax[3].set_xlabel('Prior', fontsize=8)
    if not prior:
        leg_title = 'Stimulus\n evidence'
        ax[2].plot(bins_coh, np.nanmean(val_traj_subs, axis=1),
                   color='k', linestyle='--', alpha=0.6)
        ax[3].plot(bins_coh,  np.nanmean(val_vel_subs, axis=1),
                   color='k', linestyle='--', alpha=0.6)
        ax[2].set_xlabel('Evidence', fontsize=8)
        ax[3].set_xlabel('Evidence', fontsize=8)
    ax[0].legend(title=leg_title, fontsize=7, loc='upper left')
    ax[0].set_ylabel('Position (pixels)', fontsize=8)
    ax[0].set_xlabel('Time from movement onset (ms)', fontsize=8)
    # ax[0].set_title('Mean trajectory', fontsize=10)
    # ax[1].legend(title=leg_title)
    ax[1].set_ylabel('Velocity (pixels/ms)', fontsize=8)
    ax[1].set_xlabel('Time from movement onset (ms)', fontsize=8)
    # ax[1].set_title('Mean velocity', fontsize=8)
    ax[2].set_ylabel('MT (ms)', fontsize=8)
    ax[3].set_ylabel('Peak (pixels/ms)', fontsize=8)


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
    ax.set_ylabel('Position (px)', fontsize=10)
    ax.set_xlabel('Time from movement onset (ms)', fontsize=10)


def fig_humans_6(user_id, sv_folder, nm='300', max_mt=600, jitter=0.003,
                 wanted_precision=8, inset_sz=.06,
                 marginx=0.006, marginy=0.12, fgsz=(8, 14)):
    if user_id == 'Alex':
        folder = 'C:\\Users\\Alexandre\\Desktop\\CRM\\Human\\80_20\\'+nm+'ms\\'
    if user_id == 'AlexCRM':
        folder = 'C:/Users/agarcia/Desktop/CRM/human/'
    if user_id == 'Manuel':
        folder =\
            '/home/molano/Dropbox/project_Barna/psycho_project/80_20/'+nm+'ms/'
    if user_id == 'idibaps_alex':
        folder = '/home/jordi/DATA/Documents/changes_of_mind/humans/'+nm+'ms/'
    subj = ['general_traj']
    steps = [None]
    humans = True
    df_data = ah.traj_analysis(data_folder=folder,
                               subjects=subj, steps=steps, name=nm,
                               sv_folder=sv_folder)
    df_data.avtrapz /= max(abs(df_data.avtrapz))
    fig, ax = plt.subplots(nrows=5, ncols=3, figsize=fgsz)
    ax = ax.flatten()
    plt.subplots_adjust(top=0.95, bottom=0.09, left=0.09, right=0.95,
                        hspace=0.5, wspace=0.6)
    labs = ['a', '',  'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', '', 'k',
            '', 'l']
    for n, ax_1 in enumerate(ax):
        rm_top_right_lines(ax_1)
        if n == 9:
            ax_1.text(-0.1, 3, labs[n], transform=ax_1.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 0:
            ax_1.text(-0.1, 1.15, labs[n], transform=ax_1.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        else:
            ax_1.text(-0.1, 1.2, labs[n], transform=ax_1.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
    for i in [0, 1]:
        ax[i].axis('off')
    # task panel
    pos_ax_0 = ax[0].get_position()
    # setting ax0 a bit bigger
    ax[0].set_position([pos_ax_0.x0 + pos_ax_0.width/5, pos_ax_0.y0-0.02,
                        pos_ax_0.width+pos_ax_0.width*2/3, pos_ax_0.height+0.025])
    ax_task = ax[0]
    pos = ax_task.get_position()
    ax_task.set_position([pos.x0, pos.y0, pos.width, pos.height])
    task = plt.imread(HUMAN_TASK_IMG)
    ax_task.imshow(task, aspect='auto')
    # changing ax x-y plot width
    pos_ax_1 = ax[1].get_position()
    ax[2].set_position([pos_ax_1.x0 + pos_ax_1.width*4/5, pos_ax_1.y0,
                        pos_ax_1.width+pos_ax_1.width/3, pos_ax_1.height])
    # tachs and pright
    ax_tach = ax[3]
    ax_pright = ax[4]
    ax_mat = [ax[10], ax[11]]
    ax_traj = ax[5]
    matrix_figure(df_data=df_data, ax_tach=ax_tach, ax_pright=ax_pright,
                  ax_mat=ax_mat, humans=humans)
    plot_coms(df=df_data, ax=ax_traj, human=humans)
    ax_cohs = ax[6]
    ax_zt = ax[7]
    # trajs. conditioned on coh
    ax_inset = add_inset(ax=ax_cohs, inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=0.04, right=True)
    ax_cohs = np.insert(ax_cohs, 0, ax_inset)
    # trajs. conditioned on zt
    ax_inset = add_inset(ax=ax_zt, inset_sz=inset_sz, fgsz=fgsz,
                         marginx=marginx, marginy=0.04, right=True)
    ax_zt = np.insert(ax_zt, 0, ax_inset)
    axes_trajs = [ax[2], ax_cohs[1], ax_cohs[0], ax_zt[1], ax_zt[0], ax[12],
                  ax[13], ax[14]]
    peak_com = -df_data.com_peak.values
    time_com = df_data.time_com.values
    ax_com_stat = ax[9]
    pos = ax_com_stat.get_position()
    ax_com_stat.set_position([pos.x0, pos.y0, pos.width,
                              pos.height*2/5])
    ax_inset = plt.axes([pos.x0, pos.y0+pos.height*3/5, pos.width,
                         pos.height*2/5])
    ax_coms = [ax_com_stat, ax_inset]
    com_statistics_humans(peak_com=peak_com, time_com=time_com, ax=[ax_coms[0],
                                                                    ax_coms[1]])
    mean_com_traj_human(df_data=df_data, ax=ax[8])
    human_trajs(df_data, sv_folder=sv_folder, ax=axes_trajs, max_mt=max_mt,
                jitter=jitter, wanted_precision=wanted_precision, plotxy=True)
    fig.savefig(SV_FOLDER+'fig6.svg', dpi=400, bbox_inches='tight')
    fig.savefig(SV_FOLDER+'fig6.png', dpi=400, bbox_inches='tight')


def mean_com_traj_human(df_data, ax, max_mt=400):
    # TRAJECTORIES
    rm_top_right_lines(ax=ax)
    index1 = (df_data.subjid != 5) & (df_data.subjid != 6)
    df_data.avtrapz /= max(abs(df_data.avtrapz))
    decision = df_data.R_response.values[index1]
    trajs = df_data.trajectory_y.values[index1]
    times = df_data.times.values[index1]
    com = df_data.CoM_sugg.values[index1]
    # congruent_coh = coh * (decision*2 - 1)
    precision = 16
    mat_mean_trajs_subjs = np.empty((len(df_data.subjid.unique()), max_mt))
    mat_mean_trajs_subjs[:] = np.nan
    for i_s, subj in enumerate(df_data.subjid.unique()):
        index = com & (df_data.subjid.values[index1] == subj)
        all_trajs = np.empty((sum(index), max_mt))
        all_trajs[:] = np.nan
        for tr in range(sum(index)):
            vals = np.array(trajs[index][tr]) * (decision[index][tr]*2 - 1)
            ind_time = [True if t != '' else False for t in times[index][tr]]
            time = np.array(times[index][tr])[np.array(ind_time)].astype(float)
            max_time = max(time)*1e3
            if max_time > max_mt:
                continue
            all_trajs[tr, :len(vals)] = vals
            all_trajs[tr, len(vals):-1] = np.repeat(vals[-1],
                                                    int(max_mt-len(vals)-1))
        mean_traj = np.nanmean(all_trajs, axis=0)
        xvals = np.arange(len(mean_traj))*precision
        yvals = mean_traj
        ax.plot(xvals, yvals, color=COLOR_COM, alpha=0.1)
        mat_mean_trajs_subjs[i_s, :] = yvals
    mean_traj_across_subjs = np.nanmean(mat_mean_trajs_subjs, axis=0)
    ax.plot(xvals, mean_traj_across_subjs, color=COLOR_COM, linewidth=2)
    index = ~com
    all_trajs = np.empty((sum(index), max_mt))
    all_trajs[:] = np.nan
    for tr in range(sum(index)):
        vals = np.array(trajs[index][tr]) * (decision[index][tr]*2 - 1)
        ind_time = [True if t != '' else False for t in times[index][tr]]
        time = np.array(times[index][tr])[np.array(ind_time)].astype(float)
        max_time = max(time)*1e3
        if max_time > max_mt:
            continue
        all_trajs[tr, :len(vals)] = vals
        all_trajs[tr, len(vals):-1] = np.repeat(vals[-1],
                                                int(max_mt-len(vals)-1))
    mean_traj = np.nanmean(all_trajs, axis=0)
    xvals = np.arange(len(mean_traj))*precision
    yvals = mean_traj
    ax.plot(xvals, yvals, color=COLOR_NO_COM, linewidth=2)
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('x-coord. (px)')
    legendelements = [Line2D([0], [0], color=COLOR_COM, lw=2,
                             label='Rev.'),
                      Line2D([0], [0], color=COLOR_NO_COM, lw=2,
                             label='No-Rev.')]
    ax.legend(handles=legendelements, loc='upper left')
    ax.axhline(-100, color='r', linestyle=':')
    ax.set_xlim(-5, 415)
    ax.text(150, -200, 'Detection threshold', color='r', fontsize=8)


def com_statistics_humans(peak_com, time_com, ax):
    ax2, ax1 = ax
    rm_top_right_lines(ax1)
    rm_top_right_lines(ax2)
    ax1.hist(peak_com[peak_com != 0]/600*100, bins=67, range=(-100, -16.667),
             color=COLOR_COM)
    ax1.hist(peak_com[peak_com != 0]/600*100, bins=14, range=(-16.667, 0),
             color=COLOR_NO_COM)
    ax1.set_yscale('log')
    ax1.axvline(-100/6, linestyle=':', color='r')
    ax1.set_xlim(-100, 1)
    ax1.set_xlabel('Deflection point (%)')
    ax1.set_ylabel('# Trials')
    ax2.set_ylabel('# Trials')
    ax2.hist(time_com[time_com != -1]*1e3, bins=30, range=(0, 510),
             color=COLOR_COM)
    ax2.set_xlabel('Deflection time (ms)')


def human_trajs(df_data, ax, sv_folder, max_mt=400, jitter=0.003,
                wanted_precision=8, max_px=800, plotxy=False,
                interpolatespace=np.arange(500)):
    # TRAJECTORIES
    index1 = (df_data.subjid != 5) & (df_data.subjid != 6) &\
             (df_data.sound_len <= 300) &\
             (df_data.sound_len >= 0)
    df_data.avtrapz /= max(abs(df_data.avtrapz))
    coh = df_data.avtrapz.values[index1]
    decision = df_data.R_response.values[index1]
    trajs = df_data.trajectory_y.values[index1]
    times = df_data.times.values[index1]
    sound_len = df_data.sound_len.values[index1]
    prior = df_data['norm_allpriors'][index1] * (decision*2 - 1)
    prior_raw = df_data['norm_allpriors'][index1]
    prior_raw = prior_raw.values
    prior = prior.values
    ev_vals = np.unique(np.round(coh, 2))
    subjects = df_data.subjid.values[index1]
    ground_truth = (df_data.R_response.values*2-1) *\
        (df_data.hithistory.values*2-1)
    ground_truth = ground_truth[index1]
    bins = ev_vals
    congruent_coh = np.round(coh, 2) * (decision*2 - 1)
    colormap = pl.cm.coolwarm(np.linspace(0., 1, len(ev_vals)))
    vals_thr_traj = []
    precision = 1
    labels_stim = ['-1', ' ', ' ', '0', ' ', ' ', '1']
    for i_ev, ev in enumerate(ev_vals):
        index = (congruent_coh == ev) &\
            (np.abs(prior) <= np.quantile(np.abs(prior), 0.25))
        all_trajs = np.empty((sum(index), max_mt))
        all_trajs[:] = np.nan
        for tr in range(sum(index)):
            vals = np.array(trajs[index][tr])*(decision[index][tr]*2-1)
            ind_time = [True if t != '' else False for t in times[index][tr]]
            time = np.array(times[index][tr])[np.array(ind_time)].astype(float)*1e3
            f = interpolate.interp1d(time, vals, bounds_error=False)
            vals_in = f(interpolatespace)
            vals_in = vals_in[~np.isnan(vals_in)]
            max_time = max(time)
            if max_time > max_mt:
                continue
            all_trajs[tr, :len(vals_in)] = vals_in  # - vals[0]
            all_trajs[tr, len(vals_in):-1] = np.repeat(vals[-1],
                                                       int(max_mt - len(vals_in)-1))
        mean_traj = np.nanmean(all_trajs, axis=0)
        std_traj = np.sqrt(np.nanstd(all_trajs, axis=0) / sum(index))
        val_traj = np.nanmean(np.array([float(t[-1]) for t in
                                        times[index]
                                        if t[-1] != '']))*1e3
        vals_thr_traj.append(val_traj)
        ax[2].scatter(ev, val_traj, color=colormap[i_ev], marker='D', s=40)
        xvals = np.arange(len(mean_traj))*precision
        yvals = mean_traj
        ax[1].plot(xvals[yvals <= max_px], mean_traj[yvals <= max_px],
                   color=colormap[i_ev], label='{}'.format(labels_stim[i_ev]))
        ax[1].fill_between(x=xvals[yvals <= max_px],
                           y1=mean_traj[yvals <= max_px]-std_traj[yvals <= max_px],
                           y2=mean_traj[yvals <= max_px]+std_traj[yvals <= max_px],
                           color=colormap[i_ev])
    ax[2].plot(bins, vals_thr_traj, color='k', linestyle='--', alpha=0.6)
    ax[1].set_xlim(-0.1, 470)
    ax[1].set_ylim(-1, 620)
    ax[1].legend(title='Stimulus \n evidence', loc='upper left', fontsize=6)
    ax[1].set_ylabel('x-coord (px)')
    ax[1].set_xlabel('Time from movement onset (ms)')
    ax[2].set_xticks([])
    ax[2].set_xlabel('Stimulus')
    ax[2].set_ylabel('MT (ms)')
    rtbins = np.concatenate(([0], np.quantile(sound_len, [.25, .50, .75, 1])))
    split_ind = []
    colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
    ev_vals = [0, 0.25, 0.5, 1]
    for subj in np.unique(subjects):
        for i in range(rtbins.size-1):
            # fig, ax1 = plt.subplots(1)
            for i_ev, ev in enumerate(ev_vals):
                index = (sound_len < rtbins[i+1]) & (sound_len >= rtbins[i]) &\
                        (np.abs(np.round(coh, 2)) == ev) &\
                        (subjects == subj)  # & (prior <= 0.3)
                all_trajs = all_trajs = np.empty((sum(index), int(max_mt+300)))
                all_trajs[:] = np.nan
                for tr in range(sum(index)):
                    vals = np.array(trajs[index][tr]) * (ground_truth[index][tr])
                    ind_time = [True if t != '' else False
                                for t in times[index][tr]]
                    time = np.array(times[index][tr])[
                        np.array(ind_time)].astype(float)*1e3
                    f = interpolate.interp1d(time, vals, bounds_error=False)
                    vals_in = f(interpolatespace)
                    vals_in = vals_in[~np.isnan(vals_in)]
                    vals_in -= vals_in[0]
                    vals_in = np.concatenate((np.zeros((int(sound_len[index][tr]))),
                                              vals_in))
                    max_time = max(time)
                    if max_time > max_mt:
                        continue
                    all_trajs[tr, :len(vals_in)] = vals_in  # - vals[0]
                    all_trajs[tr, len(vals_in):-1] =\
                        np.repeat(vals[-1], int(max_mt + 300 - len(vals_in)-1))
                if ev == 0:
                    ev_mat = np.repeat(0, sum(index))
                    traj_mat = all_trajs
                else:
                    ev_mat = np.concatenate((ev_mat, np.repeat(ev, sum(index))))
                    traj_mat = np.concatenate((traj_mat, all_trajs))
                # ax1.plot(np.arange(len(np.nanmean(traj_mat, axis=0)))*16,
                #          np.nanmean(traj_mat, axis=0),
                #          color=colormap[i_ev])
                # ax1.set_xlim(0, 650)
                # ax1.set_title('{} < RT < {}'.format(rtbins[i], rtbins[i+1]))
            ind = get_split_ind_corr(traj_mat, ev_mat, startfrom=0,
                                     max_MT=max_mt+300, pval=0.01)
            if ind < 410:
                split_ind.append(ind)
            else:
                # ind = get_split_ind_corr(traj_mat, ev_mat, startfrom=0,
                #                          max_MT=500, pval=0.001)
                # if ind > 410:
                split_ind.append(np.nan)
            # ax1.axvline(ind*16, color='r')
    out_data = np.array(split_ind)
    rtbins = np.array((rtbins[0], rtbins[1], rtbins[2]))
    # to plot trajectories with splitting time: (all subjects together)
    labs = ['Early RT', 'Late RT']
    for i in range(rtbins.size-1):
        ax1 = ax[-3+i]
        if i > 0:
            rtbins = np.array((rtbins[-3], rtbins[-2], rtbins[-1]))
        for i_ev, ev in enumerate(ev_vals):
            index = (sound_len < rtbins[i+1]) & (sound_len >= rtbins[i]) &\
                    (np.abs(np.round(coh, 2)) == ev)
            all_trajs = all_trajs = np.empty((sum(index), int(max_mt+300)))
            all_trajs[:] = np.nan
            for tr in range(sum(index)):
                vals = np.array(trajs[index][tr]) * (ground_truth[index][tr])
                ind_time = [True if t != '' else False
                            for t in times[index][tr]]
                time = np.array(times[index][tr])[
                    np.array(ind_time)].astype(float)*1e3
                f = interpolate.interp1d(time, vals, bounds_error=False)
                vals_in = f(interpolatespace)
                vals_in = vals_in[~np.isnan(vals_in)]
                vals_in -= vals_in[0]
                vals_in = np.concatenate((np.zeros((int(sound_len[index][tr]))),
                                          vals_in))
                max_time = max(time)
                if max_time > max_mt:
                    continue
                all_trajs[tr, :len(vals_in)] = vals_in  # - vals[0]
                all_trajs[tr, len(vals_in):-1] =\
                    np.repeat(vals[-1], int(max_mt + 300 - len(vals_in)-1))
            if ev == 0:
                ev_mat = np.repeat(0, sum(index))
                traj_mat = all_trajs
            else:
                ev_mat = np.concatenate((ev_mat, np.repeat(ev, sum(index))))
                traj_mat = np.concatenate((traj_mat, all_trajs))
            ax1.plot(np.arange(len(np.nanmean(all_trajs, axis=0))),
                     np.nanmean(all_trajs, axis=0),
                     color=colormap[i_ev])
        ax1.set_xlim(-5, 405)
        ax1.set_ylim(-2, 400)
        ax1.set_title(labs[i])
        ind = get_split_ind_corr(traj_mat, ev_mat, startfrom=0,
                                 max_MT=max_mt+300, pval=0.01)
        # ax1.axvline(ind, color='r')
        ax1.set_xlabel('Time (ms)')
        if i == 0:
            ax1.arrow(ind, 45, 0, 65, color='k', width=1, head_width=5,
                      head_length=0.4)
            ax1.text(ind-30, 10, 'Splitting Time', fontsize=8)
            labels = ['0', '0.25', '0.5', '1']
            legendelements = []
            for i_l, lab in enumerate(labels):
                legendelements.append(Line2D([0], [0], color=colormap[i_l], lw=2,
                                      label=lab))
            ax1.legend(handles=legendelements, fontsize=7, loc='upper left')
        else:
            if np.isnan(ind):
                ind = rtbins[i]
            ax1.arrow(ind, 145, 0, -65, color='k', width=1, head_width=5,
                      head_length=0.4)
            ax1.text(ind-60, 160, 'Splitting Time', fontsize=8)
    # now for the prior
    # cong_prior = prior * (decision*2 - 1)
    bins = [-1, -0.5, -0.1, 0.1, 0.5, 1]
    colormap = pl.cm.copper(np.linspace(0, 1, len(bins)-1))
    vals_thr_traj = []
    for i_pr, pr_min in enumerate(bins):
        if pr_min == 1:
            break
        index = (prior >= bins[i_pr])*(prior < bins[i_pr+1])  # * (coh == 0)
        all_trajs = np.empty((sum(index), max_mt))
        all_trajs[:] = np.nan
        for tr in range(sum(index)):
            if prior[index][tr] != 0:
                vals = np.array(trajs[index][tr]) * (decision[index][tr]*2 - 1)
                ind_time = [True if t != '' else False for t in times[index][tr]]
                time = np.array(times[index][tr])[
                    np.array(ind_time)].astype(float)*1e3
                f = interpolate.interp1d(time, vals, bounds_error=False)
                vals_in = f(interpolatespace)
                vals_in = vals_in[~np.isnan(vals_in)]
                max_time = max(time)
                if max_time > max_mt:
                    continue
                all_trajs[tr, :len(vals_in)] = vals_in  # - vals[0]
                all_trajs[tr, len(vals_in):-1] = np.repeat(vals[-1],
                                                           int(max_mt
                                                               - len(vals_in)-1))
            else:
                continue
            if max_time > max_mt:
                continue
        mean_traj = np.nanmean(all_trajs, axis=0)
        std_traj = np.sqrt(np.nanstd(all_trajs, axis=0) / sum(index))
        val_traj = np.nanmean(np.array([float(t[-1]) for t in
                                        times[index]
                                        if t[-1] != '']))*1e3
        vals_thr_traj.append(val_traj)
        ax[4].scatter(i_pr, val_traj, color=colormap[i_pr], marker='D', s=40)
        xvals = np.arange(len(mean_traj))*precision
        yvals = mean_traj
        ax[3].plot(xvals[yvals <= max_px], mean_traj[yvals <= max_px],
                   color=colormap[i_pr])
        ax[3].fill_between(x=xvals[yvals <= max_px],
                           y1=mean_traj[yvals <= max_px]-std_traj[yvals <= max_px],
                           y2=mean_traj[yvals <= max_px]+std_traj[yvals <= max_px],
                           color=colormap[i_pr])
    ax[4].plot(np.arange(5), vals_thr_traj, color='k', linestyle='--', alpha=0.6)
    # ax[3].set_xlim(-0.1, 360)
    ax[1].set_xlim(-0.1, 470)
    ax[3].set_ylim(-1, 620)
    colormap = pl.cm.copper_r(np.linspace(0., 1, 5))
    legendelements = [Line2D([0], [0], color=colormap[0], lw=2,
                             label='cong.'),
                      Line2D([0], [0], color=colormap[1], lw=2,
                             label=''),
                      Line2D([0], [0], color=colormap[2], lw=2,
                             label='0'),
                      Line2D([0], [0], color=colormap[2], lw=2,
                             label=''),
                      Line2D([0], [0], color=colormap[4], lw=2,
                             label='inc.')]
    ax[3].legend(handles=legendelements, title='Prior', loc='upper left',
                 fontsize=7)
    ax[3].set_ylabel('x-coord (px)')
    ax[3].set_xlabel('Time from movement onset (ms)')
    ax[4].set_xlabel('Prior')
    ax[4].set_ylabel('MT (ms)')
    ax[4].set_xticks([])
    if plotxy:
        cont = 0
        for traj in range(800):
            tr_ind = np.random.randint(0, len(df_data['trajectory_y'])-1)
            x_coord = df_data['trajectory_y'][tr_ind]
            y_coord = df_data['traj_y'][tr_ind]
            time_max = df_data['times'][tr_ind][-1]
            if time_max != '':
                if time_max < 0.3 and time_max > 0.1:
                    time = df_data['times'][tr_ind]
                    ind_time = [True if t != '' else False for t in time]
                    time = np.array(time)[np.array(ind_time)]
                    ax[0].plot(x_coord, y_coord, color='k', linewidth=0.5)
                    # ax[5].plot(time*1e3, x_coord, color='k', linewidth=0.5)
                    cont += 1
            if cont == 50:
                break
        ax[0].set_xlabel('x-coord (px)')
        ax[0].set_ylabel('y-coord (px)')
    # ax[5].set_xlabel('Time (ms)')
    # ax[5].set_ylabel('x-coord (px)')
    rtbins = np.concatenate(([0], np.quantile(sound_len, [.25, .50, .75, 1])))
    xvals = []
    for irtb, rtb in enumerate(rtbins[:-1]):
        xvals.append(rtb*0.5 + rtbins[irtb+1]*0.5)
    # xplot = rtbins[:-1] + np.diff(rtbins)/2
    out_data = np.array(out_data).reshape(np.unique(subjects).size,
                                          rtbins.size-1, -1)
    out_data = np.swapaxes(out_data, 0, 1)
    out_data = out_data.astype(float)
    # binsize = np.diff(rtbins)
    ax2 = ax[-1]
    # fig2, ax2 = plt.subplots(1)
    for i in range(len(np.unique(subjects))):
        for j in range(out_data.shape[2]):
            ax2.plot(xvals,
                     out_data[:, i, j],
                     marker='o', mfc=(.6, .6, .6, .3), mec=(.6, .6, .6, 1),
                     mew=1, color=(.6, .6, .6, .3))
    error_kws = dict(ecolor='firebrick', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='firebrick', marker='o', label='mean & SEM')
    ax2.errorbar(xvals,
                 np.nanmedian(out_data.reshape(rtbins.size-1, -1), axis=1),
                 yerr=sem(out_data.reshape(rtbins.size-1, -1),
                          axis=1, nan_policy='omit'), **error_kws)
    ax2.set_xlabel('RT (ms)')
    ax2.set_title('Impact of stimulus', fontsize=9)
    # ax2.set_xticks([107, 128], labels=['Early RT', 'Late RT'], fontsize=9)
    # ax2.set_ylim(190, 410)
    ax2.plot([0, 310], [0, 310], color='k')
    ax2.fill_between([0, 310], [0, 310], [0, 0],
                     color='grey', alpha=0.6)
    ax2.set_ylabel('Splitting time (ms)')
    rm_top_right_lines(ax2)


def linear_fun(x, a, b, c, d):
    return a + b*x[0] + c*x[1] + d*x[2]


def mt_linear_reg(mt, coh, trial_index, com, prior, plot=False):
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
    trial_index = trial_index.astype(float)[~com.astype(bool)]
    xdata = np.array([[coh[~com.astype(bool)]],
                      [trial_index],
                      [prior[~com.astype(bool)]]]).reshape(3, sum(~com))
    ydata = np.array(mt[~com.astype(bool)])
    popt, pcov = curve_fit(f=linear_fun, xdata=xdata, ydata=ydata)
    if plot:
        df = pd.DataFrame({'coh': coh/max(coh), 'prior': prior/max(prior),
                           'MT': resp_len,
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


def run_model(stim, zt, coh, gt, trial_index, subject=None, num_tr=None,
              load_params=True):
    # dt = 5e-3
    if num_tr is not None:
        num_tr = num_tr
    else:
        num_tr = int(len(zt))
    data_augment_factor = 10
    detect_CoMs_th = 8
    if not load_params:
        p_t_aff = 5
        p_t_eff = 4
        p_t_a = 14  # 90 ms (18) PSIAM fit includes p_t_eff
        p_w_zt = 0.5
        p_w_stim = 0.14
        p_e_bound = 2.
        p_com_bound = 0.1
        p_w_a_intercept = 0.056
        p_w_a_slope = -2e-5  # fixed
        p_a_bound = 2.6  # fixed
        p_1st_readout = 40
        p_2nd_readout = 80
        p_leak = 0.5
        p_mt_noise = 35
        p_MT_intercept = 320
        p_MT_slope = 0.07
        conf = [p_w_zt, p_w_stim, p_e_bound, p_com_bound, p_t_aff,
                p_t_eff, p_t_a, p_w_a_intercept, p_w_a_slope, p_a_bound, p_1st_readout,
                p_2nd_readout, p_leak, p_mt_noise, p_MT_intercept, p_MT_slope]
        jitters = len(conf)*[0]
    else:
        conf = np.load(SV_FOLDER + 'parameters_MNLE_BADS' + subject + '.npy')
        jitters = len(conf)*[0]
    print('Number of trials: ' + str(stim.shape[1]))
    p_w_zt = conf[0]+jitters[0]*np.random.rand()
    p_w_stim = conf[1]+jitters[1]*np.random.rand()
    p_e_bound = conf[2]+jitters[2]*np.random.rand()
    p_com_bound = conf[3]+jitters[3]*np.random.rand()
    p_t_aff = int(round(conf[4]+jitters[4]*np.random.rand()))
    p_t_eff = int(round(conf[5]++jitters[5]*np.random.rand()))
    p_t_a = int(round(conf[6]++jitters[6]*np.random.rand()))
    p_w_a_intercept = conf[7]+jitters[7]*np.random.rand()
    p_w_a_slope = conf[8]+jitters[8]*np.random.rand()
    p_a_bound = conf[9]+jitters[9]*np.random.rand()
    p_1st_readout = conf[10]+jitters[10]*np.random.rand()
    p_2nd_readout = conf[11]+jitters[11]*np.random.rand()
    p_leak = conf[12]+jitters[12]*np.random.rand()
    p_mt_noise = conf[13]+jitters[13]*np.random.rand()
    p_MT_intercept = conf[14]+jitters[14]*np.random.rand()
    p_MT_slope = conf[15]+jitters[15]*np.random.rand()
    stim = edd2.data_augmentation(stim=stim.reshape(20, num_tr),
                                  daf=data_augment_factor)
    stim_res = 50/data_augment_factor
    compute_trajectories = True
    all_trajs = True

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
                                 p_MT_slope=p_MT_slope,
                                 p_MT_intercept=p_MT_intercept,
                                 p_w_zt=p_w_zt, p_w_stim=p_w_stim,
                                 p_e_bound=p_e_bound, p_com_bound=p_com_bound,
                                 p_t_aff=p_t_aff, p_t_eff=p_t_eff, p_t_a=p_t_a,
                                 num_tr=num_tr, p_w_a_intercept=p_w_a_intercept,
                                 p_w_a_slope=p_w_a_slope,
                                 p_a_bound=p_a_bound,
                                 p_1st_readout=p_1st_readout,
                                 p_2nd_readout=p_2nd_readout, p_leak=p_leak,
                                 p_mt_noise=p_mt_noise,
                                 compute_trajectories=compute_trajectories,
                                 stim_res=stim_res, all_trajs=all_trajs)
    hit_model = resp_fin == gt
    reaction_time = (first_ind[tr_index]-int(300/stim_res) + p_t_eff)*stim_res
    detected_com = np.abs(x_val_at_updt) > detect_CoMs_th
    return hit_model, reaction_time, detected_com, resp_fin, com_model,\
        pro_vs_re, total_traj, x_val_at_updt


def run_simulation_different_subjs(stim, zt, coh, gt, trial_index, subject_list,
                                   subjid, num_tr=None, load_params=True):
    hit_model = np.empty((0))
    reaction_time = np.empty((0))
    detected_com = np.empty((0))
    resp_fin = np.empty((0))
    com_model = np.empty((0))
    pro_vs_re = np.empty((0))
    total_traj = []
    x_val_at_updt = np.empty((0))
    for subject in subject_list:
        if subject_list[0] is not None:
            index = subjid == subject
        else:
            index = range(num_tr)
        sim_data = DATA_FOLDER + subject + '/sim_data/' + subject + '_simulation.pkl'
        # create folder if it doesn't exist
        os.makedirs(os.path.dirname(sim_data), exist_ok=True)
        if os.path.exists(sim_data):
            data_simulation = np.load(sim_data, allow_pickle=True)
            hit_model_tmp = data_simulation['hit_model_tmp']
            reaction_time_tmp = data_simulation['reaction_time_tmp']
            detected_com_tmp = data_simulation['detected_com_tmp']
            resp_fin_tmp = data_simulation['resp_fin_tmp']
            com_model_tmp = data_simulation['com_model_tmp']
            pro_vs_re_tmp = data_simulation['pro_vs_re_tmp']
            total_traj_tmp = data_simulation['total_traj_tmp']
            x_val_at_updt_tmp = data_simulation['x_val_at_updt_tmp']
        else:
            hit_model_tmp, reaction_time_tmp, detected_com_tmp, resp_fin_tmp,\
                com_model_tmp, pro_vs_re_tmp, total_traj_tmp, x_val_at_updt_tmp =\
                run_model(stim=stim[:, index], zt=zt[index], coh=coh[index],
                          gt=gt[index], trial_index=trial_index[index],
                          subject=subject, load_params=load_params)
            data_simulation = {'hit_model_tmp': hit_model_tmp, 'reaction_time_tmp': reaction_time_tmp,
                               'detected_com_tmp': detected_com_tmp, 'resp_fin_tmp': resp_fin_tmp,
                               'com_model_tmp': com_model_tmp, 'pro_vs_re_tmp': pro_vs_re_tmp,
                               'total_traj_tmp': total_traj_tmp, 'x_val_at_updt_tmp': x_val_at_updt_tmp}
            pd.to_pickle(data_simulation, sim_data)
        hit_model = np.concatenate((hit_model, hit_model_tmp))
        reaction_time = np.concatenate((reaction_time, reaction_time_tmp))
        detected_com = np.concatenate((detected_com, detected_com_tmp))
        resp_fin = np.concatenate((resp_fin, resp_fin_tmp))
        com_model = np.concatenate((com_model, com_model_tmp))
        pro_vs_re = np.concatenate((pro_vs_re, pro_vs_re_tmp))
        total_traj = total_traj + total_traj_tmp
        x_val_at_updt = np.concatenate((x_val_at_updt, x_val_at_updt_tmp))
    return hit_model, reaction_time, detected_com, resp_fin, com_model,\
        pro_vs_re, total_traj, x_val_at_updt


def fig_7(df, df_sim):
    zt = df.allpriors.values
    coh = df.coh2.values
    com = df.CoM_sugg.values
    com_model = df_sim['com_detcted'].values
    sound_len_model = df_sim.sound_len.values
    fig, ax = plt.subplots(nrows=3, ncols=3)
    ax = ax.flatten()
    fig.suptitle('Stim/prior')
    sound_len = df.sound_len.values
    window = [0, 25, 50, 100, 125, 150, 175, 200, 250]
    for i in range(8):
        zt_tmp = zt[(sound_len > window[i]) * (sound_len < window[i+1])]
        coh_tmp = coh[(sound_len > window[i]) * (sound_len < window[i+1])]
        com_tmp = com[(sound_len > window[i]) * (sound_len < window[i+1])]
        edd2.com_heatmap_jordi(zt_tmp, coh_tmp, com_tmp, ax=ax[i],
                               flip=True, annotate=False, xlabel='prior',
                               ylabel='avg stim', cmap='rocket')
        ax[i].set_title('{} < RT < {}'.format(window[i], window[i+1]))
    pos = ax[8].get_position()
    x, y, w, h = pos.x0, pos.y0, pos.width, pos.height
    inset_height = h/2
    inset_width = w/2
    ax[8].set_title('Model')
    ax[8].axis('off')
    ax_inset_1 = plt.axes([x, y, inset_height, inset_width])
    ax_inset_2 = plt.axes([x+inset_width, y, inset_height, inset_width])
    ax_inset_3 = plt.axes([x, y+inset_height, inset_height, inset_width])
    ax_inset_4 = plt.axes([x+inset_width, y+inset_height, inset_height,
                           inset_width])
    ax_inset = [ax_inset_3, ax_inset_4, ax_inset_1, ax_inset_2]
    window = [0, 50, 100, 125, 150]
    for i in range(4):
        zt_tmp = zt[(sound_len_model > window[i]) *
                    (sound_len_model < window[i+1])]
        coh_tmp = coh[(sound_len_model > window[i]) *
                      (sound_len_model < window[i+1])]
        com_model_tmp = com_model[(sound_len_model > window[i]) *
                                  (sound_len_model < window[i+1])]
        edd2.com_heatmap_jordi(zt_tmp, coh_tmp, com_model_tmp, ax=ax_inset[i],
                               flip=True, annotate=False, xlabel='',
                               ylabel='', cmap='rocket')
    ax_inset_1.set_xlabel('Prior evidence')
    ax_inset_1.set_ylabel('Stimulus evidence')
    fig.savefig(SV_FOLDER+'fig7.svg', dpi=400, bbox_inches='tight')
    fig.savefig(SV_FOLDER+'fig7.png', dpi=400, bbox_inches='tight')


def plot_mt_vs_stim(df, ax, prior_min=0.5, rt_max=50):
    subjects = df.loc[df.special_trial == 2, 'subjid'].unique()
    subjid = df.subjid
    zt_cong = df.norm_allpriors.values * (df.R_response*2-1)
    coh_cong = df.coh2.values * (df.R_response*2-1)
    rt = df.sound_len.values
    spec_trial = df.special_trial.values
    mt = df.resp_len.values
    mt_mat = np.empty((len(subjects), len(np.unique(coh_cong))))
    sil = []
    for i_s, subject in enumerate(subjects):
        # silent
        prior_min_quan = np.quantile(zt_cong[(subjid == subject) &
                                             (~np.isnan(zt_cong))], prior_min)
        sil.append(np.nanmean(mt[(zt_cong >= prior_min_quan) & (rt <= rt_max) &
                                 (spec_trial == 2) & (subjid == subject)])*1e3)
        for iev, ev in enumerate(np.unique(coh_cong)):
            index = (subjid == subject) & (zt_cong >= prior_min_quan) &\
                (rt <= rt_max) & (spec_trial == 0) & (coh_cong == ev)
            mt_mat[i_s, iev] = np.nanmean(mt[index])*1e3
    mean_mt_vs_coh = np.nanmean(mt_mat, axis=0)
    sd_mt_vs_coh = np.nanstd(mt_mat, axis=0)/np.sqrt(len(subjects))
    ax.axhline(np.nanmean(sil), color='k', linestyle='--', alpha=0.6)
    coh_unq = np.unique(coh_cong)
    colormap = pl.cm.coolwarm(np.linspace(0, 1, len(coh_unq)))
    for x, y, e, color in zip(coh_unq, mean_mt_vs_coh, sd_mt_vs_coh, colormap):
        ax.plot(x, y, 'o', color=color)
        ax.errorbar(x, y, e, color=color)
    # coh_vals = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]
    ax.set_xticks([-1, 0, 1])
    ax.set_xlabel('Stimulus')
    ax.set_ylabel('MT (ms)')


def mt_matrix_vs_ev_zt(df, ax, silent_comparison=False, rt_bin=None,
                       collapse_sides=False):
    coh_raw = df.coh2.copy()
    norm_allp_raw = df.norm_allpriors.copy()
    df['norm_allpriors'] *= df.R_response.values*2-1
    df['coh2'] *= df.R_response.values*2-1
    if not collapse_sides:
        ax0, ax1 = ax
    if rt_bin is not None:
        if rt_bin > 100:
            df_fil = df.loc[df.sound_len > rt_bin]
        if rt_bin < 100:
            df_fil = df.loc[df.sound_len < rt_bin]
        if not collapse_sides:
            df_0 = df_fil.loc[(df_fil.R_response == 0)]
            df_1 = df_fil.loc[(df_fil.R_response == 1)]
        else:
            df_s = df_fil
    else:
        if not collapse_sides:
            df_0 = df.loc[(df.R_response == 0)]
            df_1 = df.loc[(df.R_response == 1)]
        else:
            df_s = df.copy()
    bins_zt = [1.01]
    for i_p, perc in enumerate([0.75, 0.5, 0.25, 0.25, 0.5, 0.75]):
        if i_p < 3:
            bins_zt.append(df.norm_allpriors.abs().quantile(perc))
        else:
            bins_zt.append(-df.norm_allpriors.abs().quantile(perc))
    bins_zt.append(-1.01)
    # bins_zt = [1.01, 0.65, 0.35, 0.1, -0.1, -0.35, -0.65, -1.01]
    # np.linspace(1.01, -1.01, 8)
    coh_vals = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]
    nsubs = len(df.subjid.unique())
    if not collapse_sides:
        mat_0 = np.zeros((len(bins_zt)-1, 7, nsubs))
        mat_1 = np.zeros((len(bins_zt)-1, 7, nsubs))
        silent_mat_per_rows_0 = np.zeros((len(bins_zt)-1, 7))
        silent_mat_per_rows_1 = np.zeros((len(bins_zt)-1, 7))
    else:
        mat_s = np.zeros((len(bins_zt)-1, 7, nsubs))
        silent_mat_per_rows = np.zeros((len(bins_zt)-1, 7))
    # reference MT computation
    for i_zt, zt in enumerate(bins_zt[:-1]):
        if not collapse_sides:
            mt_sil_per_sub_0 = []
            mt_sil_per_sub_1 = []
        else:
            mt_sil_per_sub = []
        for subj in df.subjid.unique():
            if not collapse_sides:
                mt_silent_0 = df_0.loc[(df_0.special_trial == 2) &
                                       (df_0.norm_allpriors < zt) &
                                       (df_0.subjid == subj) &
                                       (df_0.norm_allpriors > bins_zt[i_zt+1]),
                                       'resp_len']
                mt_silent_1 = df_1.loc[(df_1.special_trial == 2) &
                                       (df_1.norm_allpriors < zt) &
                                       (df_1.subjid == subj) &
                                       (df_1.norm_allpriors > bins_zt[i_zt+1]),
                                       'resp_len']
                mt_sil_per_sub_0.append(np.nanmean(mt_silent_0))
                mt_sil_per_sub_1.append(np.nanmean(mt_silent_1))
            else:
                mt_silent = df_s.loc[(df_s.special_trial == 2) &
                                     (df_s.norm_allpriors < zt) &
                                     (df_s.subjid == subj) &
                                     (df_s.norm_allpriors > bins_zt[i_zt+1]),
                                     'resp_len']
                mt_sil_per_sub.append(np.nanmean(mt_silent))
        if not collapse_sides:
            silent_mat_per_rows_0[i_zt, :] = np.nanmean(mt_sil_per_sub_0)*1e3
            silent_mat_per_rows_1[i_zt, :] = np.nanmean(mt_sil_per_sub_1)*1e3
        else:
            silent_mat_per_rows[i_zt, :] = np.nanmean(mt_sil_per_sub)*1e3
    # MT matrix computation, reference MT can be substracted if desired
    for i_s, subj in enumerate(df.subjid.unique()):
        if not collapse_sides:
            df_sub_0 = df_0.loc[(df_0.subjid == subj)]
            df_sub_1 = df_1.loc[(df_1.subjid == subj)]
        else:
            df_sub = df_s.loc[df_s.subjid == subj]
        for i_ev, ev in enumerate(coh_vals):
            for i_zt, zt in enumerate(bins_zt[:-1]):
                if not collapse_sides:
                    mt_vals_0 = df_sub_0.loc[(df_sub_0.coh2 == ev) &
                                             (df_sub_0.norm_allpriors < zt)
                                             & (df_sub_0.norm_allpriors >=
                                                bins_zt[i_zt+1]),
                                             'resp_len']
                    mt_vals_1 = df_sub_1.loc[(df_sub_1.coh2 == ev) &
                                             (df_sub_1.norm_allpriors < zt)
                                             & (df_sub_1.norm_allpriors >=
                                                bins_zt[i_zt+1]),
                                             'resp_len']
                    mat_0[i_zt, i_ev, i_s] = np.nanmean(mt_vals_0)*1e3
                    mat_1[i_zt, i_ev, i_s] = np.nanmean(mt_vals_1)*1e3
                else:
                    mt_vals = df_sub.loc[(df_sub.coh2 == ev) &
                                         (df_sub.norm_allpriors < zt)
                                         & (df_sub.norm_allpriors >=
                                            bins_zt[i_zt+1]),
                                         'resp_len']
                    mat_s[i_zt, i_ev, i_s] = np.nanmean(mt_vals)*1e3
    if not collapse_sides:
        mat_0 = np.nanmean(mat_0, axis=2)
        mat_1 = np.nanmean(mat_1, axis=2)
    else:
        mat_s = np.nanmean(mat_s, axis=2)
    if silent_comparison:
        if not collapse_sides:
            # We substract reference MT (in silent trials) at each row
            mat_0 -= silent_mat_per_rows_0
            mat_1 -= silent_mat_per_rows_1
        else:
            mat_s -= silent_mat_per_rows
    # else:
    #     if collapse_sides:
    #         mat_s = np.column_stack((mat_s, silent_mat_per_rows[:, 0]))
    df['norm_allpriors'] = norm_allp_raw
    df['coh2'] = coh_raw
    if not collapse_sides:
        # SIDE 0
        im_0 = ax0.imshow(mat_0, cmap='RdGy', vmin=np.nanmin((mat_1, mat_0)),
                          vmax=np.nanmax((mat_1, mat_0)))
        plt.sca(ax0)
        cbar_0 = plt.colorbar(im_0, fraction=0.04)
        cbar_0.remove()
        # cbar_0.set_label(r'$MT \; - MT_{silent}(ms)$')
        ax0.set_xlabel('Evidence')
        ax0.set_ylabel('Prior')
        if rt_bin is not None:
            if rt_bin > 100:
                ax0.set_title('Left, RT > ' + str(rt_bin) + ' ms')
            else:
                ax0.set_title('Left, RT < ' + str(rt_bin) + ' ms')
        else:
            ax0.set_title('Left')
        ax0.set_yticks([0, 3, 6], ['R', '0', 'L'])
        ax0.set_xticks([0, 3, 6], ['L', '0', 'R'])
        # SIDE 1
        ax1.set_title('Right')
        im_1 = ax1.imshow(mat_1, cmap='RdGy', vmin=np.nanmin((mat_1, mat_0)),
                          vmax=np.nanmax((mat_1, mat_0)))
        plt.sca(ax1)
        ax1.set_xlabel('Evidence')
        # ax1.set_ylabel('Prior')
        cbar_1 = plt.colorbar(im_1, fraction=0.04, pad=-0.05)
        if silent_comparison:
            cbar_1.set_label(r'$MT \; - MT_{silent}(ms)$')
        else:
            cbar_1.set_label(r'$MT \;(ms)$')
        ax1.set_yticks([0, 3, 6], ['', '', ''])
        ax1.set_xticks([0, 3, 6], ['L', '0', 'R'])
        ax0pos = ax0.get_position()
        ax1pos = ax1.get_position()
        ax0.set_position([ax0pos.x0, ax1pos.y0, ax1pos.width, ax1pos.height])
        ax1.set_position([ax1pos.x0-ax1pos.width*0.2,
                          ax1pos.y0, ax1pos.width, ax1pos.height])
    else:
        im_s = ax.imshow(np.flip(mat_s).T, cmap='RdGy')
        plt.sca(ax)
        cbar_s = plt.colorbar(im_s, fraction=0.04)
        cbar_s.set_label(r'$MT \;(ms)$')
        ax.set_yticks([0, 3, 6], ['1', '0', '-1'])
        ax.set_xticks([0, 3, 6], ['-1', '0', '1'])
        ax.set_xlabel('Prior Evidence')
        ax.set_ylabel('Stimulus Evidence')


def plot_mt_matrix_different_rtbins(df, small_rt=40, big_rt=120):
    fig, ax = plt.subplots(ncols=2)
    mt_matrix_vs_ev_zt(df, ax, rt_bin=big_rt, silent_comparison=True)
    fig, ax = plt.subplots(ncols=2)
    mt_matrix_vs_ev_zt(df, ax, rt_bin=small_rt, silent_comparison=True)


def supp_com_marginal(df):
    fig, ax = plt.subplots(nrows=len(df.subjid.unique()), ncols=2,
                           figsize=(4, 12))
    ax = ax.flatten()
    for i_ax, subj in enumerate(df.subjid.unique()):
        df_1 = df.loc[df.subjid == subj]
        nbins = 7
        matrix_side_0 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=0)
        matrix_side_1 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=1)
        # L-> R
        vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
        pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
        im = ax[i_ax*2].imshow(matrix_side_1, vmin=0, vmax=vmax)
        plt.sca(ax[i_ax*2])
        plt.colorbar(im, fraction=0.04)
        # R -> L
        pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
        im = ax[i_ax*2+1].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
        ax[i_ax*2+1].yaxis.set_ticks_position('none')
        plt.sca(ax[i_ax*2+1])
        plt.colorbar(im, fraction=0.04)
        if i_ax == 0:
            ax[i_ax].set_title(pcomlabel_1)
            ax[i_ax+1].set_title(pcomlabel_0)
        for ax_i in [ax[i_ax*2], ax[i_ax*2+1]]:
            ax_i.set_yticklabels(['']*nbins)
            ax_i.set_xticklabels(['']*nbins)
        ax[i_ax*2].set_ylabel('stim. {}'.format(subj))
        if i_ax == len(df.subjid.unique()) - 1:
            ax[i_ax*2].set_xlabel('Prior evidence')
            ax[i_ax*2+1].set_xlabel('Prior evidence')
    fig.savefig(SV_FOLDER+'fig_supp_com_marginal.svg', dpi=400,
                bbox_inches='tight')
    fig.savefig(SV_FOLDER+'fig_supp_com_marginal.png', dpi=400,
                bbox_inches='tight')


def norm_allpriors_per_subj(df):
    norm_allpriors = np.empty((0,))
    for subj in df.subjid.unique():
        df_1 = df.loc[df.subjid == subj]
        zt_tmp = df_1.allpriors.values
        norm_allpriors = np.concatenate((norm_allpriors,
                                         zt_tmp/np.nanmax(abs(zt_tmp))))
    return norm_allpriors


def different_com_thresholds(traj_y, time_trajs, decision, sound_len,
                             coh, zt, com_th_list=np.linspace(0.5, 10, 20)):
    fig, ax = plt.subplots(1)
    rm_top_right_lines(ax=ax)
    colormap = pl.cm.Reds(np.linspace(0.2, 1, len(com_th_list)))
    com_d = {}
    fig1_th, ax1 = plt.subplots(4, 2)
    ax1 = ax1.flatten()
    cont = 0
    for i_th, com_th in enumerate(com_th_list):
        print('Com threshold = ' + str(com_th))
        _, _, _, com = edd2.com_detection(trajectories=traj_y, decision=decision,
                                          time_trajs=time_trajs,
                                          com_threshold=com_th)
        df_plot = pd.DataFrame({'sound_len': sound_len, 'com': com})
        binned_curve(df_plot, 'com', 'sound_len', bins=BINS_RT, xpos=xpos_RT,
                     errorbar_kw={'color': colormap[i_th], 'label': str(com_th)},
                     ax=ax)
        com = np.array(com)
        com_d['com_'+str(com_th)] = com
        if com_th == 1 or com_th == 2.5 or com_th == 5 or com_th == 8:
            i_ax = cont
            df_1 = pd.DataFrame({'avtrapz': coh, 'CoM_sugg': com,
                                 'norm_allpriors': zt/max(abs(zt)),
                                 'R_response': (decision+1)/2})
            nbins = 7
            matrix_side_0 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=0)
            matrix_side_1 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=1)
            # L-> R
            vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
            pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
            im = ax1[i_ax*2].imshow(matrix_side_1, vmin=0, vmax=vmax, cmap='magma')
            plt.sca(ax1[i_ax*2])
            plt.colorbar(im, fraction=0.04)
            # R -> L
            pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
            im = ax1[i_ax*2+1].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
            ax1[i_ax*2+1].yaxis.set_ticks_position('none')
            plt.sca(ax1[i_ax*2+1])
            plt.colorbar(im, fraction=0.04)
            if i_ax == 0:
                ax1[i_ax].set_title(pcomlabel_1)
                ax1[i_ax+1].set_title(pcomlabel_0)
            for ax_i in [ax1[i_ax*2], ax1[i_ax*2+1]]:
                ax_i.set_yticklabels(['']*nbins)
                ax_i.set_xticklabels(['']*nbins)
            ax1[i_ax*2].set_ylabel('stim, th = {} px'.format(com_th))
            if i_ax == len(ax1) - 1:
                ax1[i_ax*2].set_xlabel('Prior evidence')
                ax1[i_ax*2+1].set_xlabel('Prior evidence')
            cont += 1
    ax.set_xlabel('RT(ms)')
    ax.set_ylabel('P(CoM)')
    com_dframe = pd.DataFrame(com_d)
    com_dframe.to_csv(SV_FOLDER + 'com_diff_thresholds.csv')


def mt_vs_stim_cong(df, rtbins=np.linspace(0, 80, 9), matrix=False, vigor=True,
                    title=None):
    ev_vals = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1]
    nsubs = len(df.subjid.unique())
    nsubs_sil = len(df.loc[df.special_trial == 2].subjid.unique())
    colormap = pl.cm.coolwarm(np.linspace(0, 1, len(ev_vals)))
    mat_mt_rt = np.empty((len(rtbins)-1, len(ev_vals)+1))
    err_mt_rt = np.empty((len(rtbins)-1, len(ev_vals)+1))
    mat_mt_rt[:] = np.nan
    err_mt_rt[:] = np.nan
    for irt, rtbin in enumerate(rtbins[:-1]):
        mt_mat = np.empty((nsubs, len(ev_vals)))
        mt_sil = []
        for i_sub, subject in enumerate(df.subjid.unique()):
            df_sub = df.loc[(df.subjid == subject) * (df.soundrfail == 0) *
                            (df.sound_len >= rtbin)*(df.sound_len < rtbins[irt+1])]
            # * (df.norm_allpriors.abs() < 0.1)]
            coh_cong = (df_sub.R_response.values*2-1)*(df_sub.coh2.values) *\
                (df_sub.special_trial == 0)
            for i_ev, ev in enumerate(ev_vals):
                index = coh_cong == ev
                mt_mat[i_sub, i_ev] = np.nanmean(df_sub.resp_len.values[index])
            if sum(df_sub.special_trial == 2) > 0:
                mt_sil.append(np.nanmean(
                    df_sub.resp_len.values[df_sub.special_trial == 2]))
        mt_mat *= 1e3
        mt_sil = np.array(mt_sil) * 1e3
        mat_mt_rt[irt, -1] = np.nanmean(1/mt_sil)
        err_mt_rt[irt, -1] = np.nanstd(1/mt_sil)/np.sqrt(nsubs_sil)
        resp_len_mean = np.nanmean(1/mt_mat, axis=0)
        resp_len_err = np.nanstd(1/mt_mat, axis=0)
        mat_mt_rt[irt, :-1] = resp_len_mean  # -np.nanmean(mt_sil)
        err_mt_rt[irt, :-1] = resp_len_err/np.sqrt(nsubs)
    ev_vals = [-1, -0.5, -0.25, 0, 0.25, 0.5, 1, 'silent']
    if not matrix and vigor:
        fig, ax = plt.subplots(1)
        rm_top_right_lines(ax)
        for ev in reversed(range(mat_mt_rt.shape[1])):
            if ev == len(ev_vals)-1:
                color = 'k'
            else:
                color = colormap[ev]
            x = rtbins[:-1]+(rtbins[1]-rtbins[0])/2
            y = mat_mt_rt[:, ev]
            err = err_mt_rt[:, ev]
            ax.errorbar(x, y, err, color=color, marker='o',
                        label=ev_vals[ev])
        ax.legend(title='Stim. evidence')
        ax.set_ylabel('vigor ~ 1/MT (ms^-1)')
        ax.set_xlabel('RT (ms)')
        ax.set_ylim(0.0028, 0.0043)
    if matrix and vigor:
        fig, ax = plt.subplots(1)
        im = ax.imshow(mat_mt_rt, cmap='coolwarm')
        ax.set_xticks(np.arange(8), labels=ev_vals)
        ax.set_yticks(np.arange(8), labels=rtbins[:-1]+(rtbins[1]-rtbins[0])/2)
        ax.set_xlabel('Stim evidence')
        ax.set_ylabel('RT (ms)')
        plt.colorbar(im, label='vigor')
    if matrix and not vigor:
        fig, ax = plt.subplots(1)
        mat_silent = np.zeros((mat_mt_rt[:, :-1].shape))
        for j in range(len(ev_vals)-1):
            mat_silent[:, j] += 1/mat_mt_rt[:, -1]
        im = ax.imshow(1/mat_mt_rt[:, :-1] - mat_silent, cmap='coolwarm',
                       vmin=-50, vmax=75)
        ax.set_xticks(np.arange(len(ev_vals)-1), labels=ev_vals[:-1])
        ax.set_yticks(np.arange(len(rtbins)-1),
                      labels=rtbins[:-1]+(rtbins[1]-rtbins[0])/2)
        ax.set_xlabel('Stim evidence')
        ax.set_ylabel('RT (ms)')
        plt.colorbar(im, label='MT (ms) - MT silent (ms)')
    ax.set_title(title)


def plot_mt_weights_rt_bins(df, rtbins=np.linspace(0, 150, 16)):
    fig, ax = plt.subplots(nrows=2)
    for a in ax:
        rm_top_right_lines(a)
    coh_weights = []
    zt_weights = []
    ti_weights = []
    coh_err = []
    zt_err = []
    ti_err = []
    for irt, rtbin in enumerate(rtbins[:-1]):
        df_rt = df.loc[(df.sound_len >= rtbin) &
                       (df.sound_len < rtbins[irt+1])]
        mean_sub, err_sub = mt_weights(df_rt, ax=None, plot=False,
                                       means_errs=True, mt=True, t_index_w=True)
        coh_weights.append(mean_sub[1])
        zt_weights.append(mean_sub[0])
        ti_weights.append(mean_sub[2])
        coh_err.append(err_sub[1])
        zt_err.append(err_sub[0])
        ti_err.append(err_sub[2])
    error_kws = dict(ecolor='goldenrod', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='goldenrod', marker='o', label='Prior')
    ax[0].errorbar(rtbins[:-1]+(rtbins[1]-rtbins[0])/2, zt_weights, zt_err,
                   **error_kws)
    error_kws = dict(ecolor='firebrick', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='firebrick', marker='o', label='Stimulus')
    ax[0].errorbar(rtbins[:-1]+(rtbins[1]-rtbins[0])/2, coh_weights, coh_err,
                   **error_kws)
    error_kws = dict(ecolor='steelblue', capsize=2, mfc=(1, 1, 1, 0), mec='k',
                     color='steelblue', marker='o', label='Trial index')
    ax[1].errorbar(rtbins[:-1]+(rtbins[1]-rtbins[0])/2, ti_weights, ti_err,
                   **error_kws)
    ax[0].set_ylabel('MT weight')
    ax[0].set_xlabel('RT (ms)')
    ax[0].legend()
    ax[1].set_ylabel('MT weight')
    ax[1].set_xlabel('RT (ms)')
    ax[1].legend()


def supp_com_threshold_matrices(df):
    dfth = pd.read_csv(SV_FOLDER + 'com_diff_thresholds.csv')
    fig, ax = plt.subplots(nrows=3, ncols=10, figsize=(15, 6))
    ax = ax.flatten()
    thlist = np.linspace(1, 10, 10)
    zt = df.allpriors.values
    coh = df.coh2.values
    decision = df.R_response.values*2 - 1
    nbins = 7
    for i_th, threshold in enumerate(thlist):
        com = dfth['com_'+str(threshold)]
        df_1 = pd.DataFrame({'avtrapz': coh, 'CoM_sugg': com,
                             'norm_allpriors': zt/max(abs(zt)),
                             'R_response': (decision+1)/2})
        matrix_side_0 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=0)
        matrix_side_1 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=1)
        # L-> R
        vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
        pcomlabel_1 = 'Left to Right'   # r'$p(CoM_{L \rightarrow R})$'
        im = ax[i_th].imshow(matrix_side_1, vmin=0, vmax=vmax)
        plt.sca(ax[i_th])
        plt.colorbar(im, fraction=0.04)
        # R -> L
        pcomlabel_0 = 'Right to Left'  # r'$p(CoM_{L \rightarrow R})$'
        im = ax[i_th+len(thlist)].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
        ax[i_th+len(thlist)].yaxis.set_ticks_position('none')
        plt.sca(ax[i_th+len(thlist)])
        plt.colorbar(im, fraction=0.04)
        ax[i_th].set_title('stim, th = {} px'.format(threshold))
        ax[i_th+len(thlist)].set_xlabel('Prior evidence')
        if i_th == 0:
            ax[i_th].set_ylabel(pcomlabel_1 + ', avg. stim.')
            ax[i_th+len(thlist)].set_ylabel(pcomlabel_0 + ', avg. stim.')
            ax[i_th + 2*len(thlist)].set_ylabel('Position (px)')
        for ax_i in [ax[i_th], ax[i_th+len(thlist)]]:
            ax_i.set_yticklabels(['']*nbins)
            ax_i.set_xticklabels(['']*nbins)
        cont = 1
        j = 1000
        while cont <= 10:
            if threshold < 10:
                if com[j] and df.trajectory_y.values[j][-1] > 1 and\
                  df.R_response.values[j] == 1 and\
                  not dfth['com_'+str(threshold+0.5)][j] and\
                  df.trajectory_y.values[j][-0] >= -2 and\
                  df.trajectory_y.values[j][-0] <= 10:
                    traj = df.trajectory_y.values[j]
                    time_trajs = df.time_trajs.values[j]
                    traj -= np.nanmean(traj[
                        (time_trajs >= -100)*(time_trajs <= 0)])
                    ax[i_th + 2*len(thlist)].plot(time_trajs,
                                                  traj,
                                                  color='k', alpha=0.7)
                    cont += 1
            if threshold == 10:
                if com[j] and df.trajectory_y.values[j][-1] > 1 and\
                  df.R_response.values[j] == 1 and\
                  df.trajectory_y.values[j][-0] >= -2 and\
                  df.trajectory_y.values[j][-0] <= 10:
                    traj = df.trajectory_y.values[j]
                    time_trajs = df.time_trajs.values[j]
                    traj -= np.nanmean(traj[
                        (time_trajs >= -100)*(time_trajs <= 0)])
                    ax[i_th + 2*len(thlist)].plot(time_trajs,
                                                  traj,
                                                  color='k', alpha=0.7)
                    cont += 1
            j += 1
        ax[i_th + 2*len(thlist)].set_xlabel('Time')
        ax[i_th + 2*len(thlist)].set_ylim(-25, 25)
        ax[i_th + 2*len(thlist)].set_xlim(-100, 500)
        ax[i_th + 2*len(thlist)].axhline(-threshold, color='r', linestyle='--',
                                         alpha=0.5)
        ax[i_th + 2*len(thlist)].axvline(0, color='r', linestyle='--',
                                         alpha=0.5)
    thlist = np.linspace(0.5, 10, 20)
    mean_com = []
    fig2, ax2 = plt.subplots(1)
    for i_th, threshold in enumerate(thlist):
        com = dfth['com_'+str(threshold)]
        mean_com.append(np.nanmean(com))
    ax2.plot(thlist, mean_com, color='k', marker='o')
    ax2.set_xlabel('Threshold (pixels)')
    ax2.set_ylabel('P(CoM)')


def model_vs_data_traj(trajs_model, df_data):
    """
    Plots trajectories of data vs model for close MTs.

    Parameters
    ----------
    trajs_model : array
        Array with the trajectories of the model sorted by trial index.
    df_data : TYPE
        Array with the trajectories of the data sorted by trial index.

    Returns
    -------
    None.

    """
    fig, ax = plt.subplots(5, 5)
    ax = ax.flatten()
    j = 0
    for i, ax_i in enumerate(ax):
        if i % 5 == 0:
            ax_i.set_ylabel('y-coord (px)')
        ax_i.set_xlabel('Time (ms)')
    for t in range(1000):
        ind = np.random.randint(0, len(trajs_model)-1)
        time_traj = df_data.time_trajs.values[ind]
        traj_data = df_data.trajectory_y.values[ind]
        if abs(len(trajs_model[ind]) - time_traj[-1]) < 15 and\
                np.sign(traj_data[-1]) == np.sign(trajs_model[ind][-1]):
            ax[j].plot(np.arange(len(trajs_model[ind])), trajs_model[ind],
                       color='r')
            ax[j].plot(time_traj, traj_data, color='k')
            ax[j].set_xlim(-100, max(time_traj[-1], len(trajs_model[ind])))
            j += 1
        if j == len(ax):
            break


def fig_trajs_model_4(trajs_model, df_data, reaction_time):
    fig, ax = plt.subplots(4, 4)
    ax = ax.flatten()
    ev_vals = [0, 0.25, 0.5, 1]
    norm_zt_vals = [0, 0.1, 0.4, 0.7, 1]
    j = 0
    trajs_model = np.array(trajs_model)
    for i_ev, ev in enumerate(ev_vals):
        for izt, ztbin in enumerate(norm_zt_vals):
            if ztbin == 1:
                break
            indx = (df_data.coh2.values == ev) &\
                (df.norm_allpriors.values > ztbin)\
                & (df.norm_allpriors.values < norm_zt_vals[izt+1])
            pl = True
            while pl:
                ind = np.random.randint(0, sum(indx)-1)
                time_traj = df_data.time_trajs.values[indx][ind]
                traj_data = df_data.trajectory_y.values[indx][ind]
                rt_rat = df_data.sound_len.values[indx][ind]
                if abs(rt_rat - reaction_time[indx][ind]) < 30:
                    ax[j].plot(np.arange(len(trajs_model[indx][ind])),
                               trajs_model[indx][ind], color='r')
                    ax[j].plot(time_traj, traj_data, color='k')
                    ax[j].set_title('ev: {}, {} < zt < {} '
                                    .format(ev, ztbin, norm_zt_vals[izt+1]))
                    ax[j].set_xlim(-10, max(len(trajs_model[indx][ind]),
                                            time_traj[-1]))
                    j += 1
                    pl = False


def mt_vs_ti_data_comparison(df, df_sim):
    df = df[:len(df_sim)]
    coh = np.array(df.coh2)[:len(df_sim)]
    mt_data = df.resp_len.values[:len(df_sim)]
    t_i_data = df.origidx[:len(df_sim)]
    mt_model = df_sim.resp_len
    t_i_model = df_sim.origidx
    plt.figure()
    plt.plot(t_i_data, mt_data*1e3, 'o', markersize=0.6, color='orange',
             label='Data')
    plt.plot(t_i_model, mt_model*1e3, 'o', markersize=0.8, color='blue',
             label='Model')
    plt.ylabel('MT (ms)')
    plt.xlabel('Trial index')
    plt.legend()
    mt_model_signed = np.copy(mt_model)*1e3
    mt_model_signed[df_sim.R_response.values == 0] *= -1
    mt_sign = np.copy(mt_data*1e3)
    mt_sign[df.R_response.values == 0] *= -1
    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(15, 10))
    ax = ax.flatten()
    sns.histplot(mt_model_signed, ax=ax[0])
    sns.histplot(mt_model*1e3, ax=ax[1])
    sns.histplot(mt_data*1e3, color='orange', ax=ax[2])
    sns.histplot(mt_sign, color='orange', ax=ax[3])
    sns.kdeplot(mt_data*1e3, color='orange', ax=ax[4], label='Data')
    sns.kdeplot(mt_model*1e3, color='blue', ax=ax[4], label='Model')
    ax[4].legend()
    ax[1].set_title('Model')
    ax[0].set_title('Model')
    ax[2].set_title('Data')
    ax[3].set_xlabel('MT (ms)')
    ax[4].set_xlabel('MT (ms)')
    for i in range(2):
        ax[i+1].set_xlim(0, 600)
    ax[3].set_xlim(-600, 600)
    ax[0].set_xlim(-600, 600)
    colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
    for iev, ev in enumerate([0, 0.25, 0.5, 1]):
        index = np.abs(coh) == ev
        sns.kdeplot(mt_data[index]*1e3, color=colormap[iev], ax=ax[5])
        index = np.abs(df_sim.coh2) == ev
        sns.kdeplot(mt_model[index]*1e3, color=colormap[iev], ax=ax[5],
                    linestyle='--')
    ax[5].set_xlim(0, 600)
    # plt.show()
    fig, ax = plt.subplots(ncols=3)
    sns.kdeplot(df_sim.sound_len.values, color='blue', label='Model', ax=ax[0])
    sns.kdeplot(df.sound_len.values, color='orange', label='Data', ax=ax[0])
    ax[0].legend()
    ax[0].set_xlabel('RT (ms)')
    sns.histplot(df_sim.sound_len.values, color='blue', label='Model', ax=ax[1])
    sns.histplot(df.sound_len.values, color='orange', label='Data', ax=ax[2])
    ax[1].set_xlabel('RT (ms)')
    ax[1].set_title('Model')
    ax[2].set_xlabel('Data')


def plot_mt_vs_rt_model_comparison(df, df_sim, bins_rt=np.linspace(0, 300, 31)):
    fig, ax = plt.subplots(ncols=2)
    colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
    ax1, ax2 = ax
    for iev, ev in enumerate([0, 0.25, 0.5, 1]):
        binned_curve(df.loc[df.coh2.abs() == ev], 'resp_len', 'sound_len',
                     bins=bins_rt, xpos=np.diff(bins_rt)[0], ax=ax1,
                     errorbar_kw={'label': 'ev: ' + str(ev),
                                  'color': colormap[iev]})
    ax1.set_xlabel('RT (ms)')
    ax1.set_ylabel('MT (s)')
    ax1.set_title('Data')
    ax1.set_ylim(0.23, 0.42)
    colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
    for iev, ev in enumerate([0, 0.25, 0.5, 1]):
        binned_curve(df_sim.loc[df_sim.coh2.abs() == ev], 'resp_len', 'sound_len',
                     bins=bins_rt, xpos=np.diff(bins_rt)[0], ax=ax2,
                     errorbar_kw={'label': 'ev: ' + str(ev),
                                  'color': colormap[iev]})
    ax2.set_xlabel('RT (ms)')
    ax2.set_ylabel('MT (s)')
    ax2.set_title('Model')
    ax2.set_ylim(0.23, 0.42)


def plot_proportion_corr_com_vs_stim(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1)
    rm_top_right_lines(ax)
    com = df.CoM_sugg.values
    gt = np.array(df.rewside)*2-1
    ch = df.R_response.values*2-1
    coh = df.coh2.abs().values
    ch_com = np.copy(ch)
    ch_no_com = np.copy(ch)
    ch_no_com[com] *= -1
    # colormap = pl.cm.gist_gray_r(np.linspace(0.3, 1, 4))
    m_corr = []
    std_corr = []
    m_corr_norm = []
    std_corr_norm = []
    for iev, ev in enumerate(np.unique(coh)):
        index = coh == ev
        m_corr_ev = []
        m_corr_normal = []
        for subj in df.subjid.unique():
            ch_sub = ch_com[index & (df.subjid == subj) & com]
            ch_norm_sub = ch[(~com) & (df.subjid == subj) & index]
            gt_sub = gt[index & (df.subjid == subj) & com]
            gt_norm_sub = gt[(~com) & (df.subjid == subj) & index]
            num_correct = sum(ch_sub == gt_sub)
            mean_corr_norm = np.mean(ch_norm_sub == gt_norm_sub)
            m_corr_ev.append(num_correct/sum(index & (df.subjid == subj) & com))
            m_corr_normal.append(mean_corr_norm)
        m_corr.append(np.nanmean(m_corr_ev))
        m_corr_norm.append(np.nanmean(m_corr_normal))
        std_corr.append(np.nanstd(m_corr_ev))
        std_corr_norm.append(np.nanstd(m_corr_normal))
    ax.errorbar(np.unique(coh), m_corr, std_corr, color='k', marker='o', label='Rev.')
    ax.errorbar(np.unique(coh), m_corr_norm, std_corr_norm, color='r',
                marker='o', label='No-Rev.')
    ax.set_xlabel('Stimulus evidence')
    ax.set_ylabel('Fraction of correcting Rev.')
    ax.set_xticks([0, 0.25, 0.5, 1], ['0', '0.25', '0.5', '1'])
    ax.legend()


def supp_plot_trajs_dep_trial_index(df):
    fig, ax = plt.subplots(nrows=2, ncols=2)
    ax = ax.flatten()
    for a in ax:
        rm_top_right_lines(a)
    ax_ti = [ax[1], ax[0], ax[3], ax[2]]
    plots_trajs_conditioned(df, ax_ti, condition='origidx', cmap='jet',
                            prior_limit=1, rt_lim=300,
                            after_correct_only=True,
                            trajectory="trajectory_y",
                            velocity=("traj_d1", 1),
                            acceleration=('traj_d2', 1), accel=False)


def plot_rt_sim(df_sim):
    fig, ax = plt.subplots(nrows=4, ncols=4)
    ax = ax.flatten()
    colormap = pl.cm.gist_gray_r(np.linspace(0.2, 1, 4))
    for isub, subj in enumerate(df_sim.subjid.unique()):
        ax[isub].set_title(subj)
        for iev, ev in enumerate([0, 0.25, 0.5, 1]):
            sns.kdeplot(df_sim.loc[(df_sim.coh2.abs() == ev) &
                                   (df_sim.subjid == subj), 'sound_len'],
                        color=colormap[iev], ax=ax[isub])
            ax[isub].set_xlabel('RT (ms)')
            ax[isub].set_title(subj)


def sess_t_index_stats(df, subjects):
    subs_spec_trial = df.loc[df.special_trial == 2, 'subjid'].unique()
    subs_no_silent = list(set(subjects)-set(subs_spec_trial))
    ses_st = []
    ntr_sil = []
    ntr_only_sil = []
    for sub_sil in subs_spec_trial:
        ses_st.append(len(df.loc[df.subjid == sub_sil, 'sessid'].unique()))
        ntr_sil.append(len(df.loc[df.subjid == sub_sil]))
        ntr_only_sil.append(len(
            df.loc[(df.special_trial == 2) & (df.subjid == sub_sil)]))
    ses_n_st = []
    ntr_n_sil = []
    for sub_n_sil in subs_no_silent:
        ses_n_st.append(len(df.loc[df.subjid == sub_n_sil, 'sessid'].unique()))
        ntr_n_sil.append(len(df.loc[df.subjid == sub_n_sil]))
    print(', '.join(list(subs_spec_trial)))
    print(', '.join(list(subs_no_silent)))


def mean_traj_per_deflection_time(df, time_com, ax,
                                  bins=np.arange(100, 401, 100)):
    df_1 = df.loc[df.CoM_sugg]
    all_trajs = np.empty((len(df.subjid.unique()), 1700))
    all_trajs[:] = np.nan
    for ind_b, min_b in enumerate(bins[:-1]):
        index = (time_com >= min_b) * (time_com < bins[ind_b+1])
        df_2 = df_1.loc[index]


def mt_diff_rev_nonrev(df):
    mt_x_sub_rev = []
    for subj in df.subjid.unique():
        mt_x_sub_rev.append(
            np.nanmean(df.loc[(df.subjid == subj) & (df.CoM_sugg), 'resp_len']) -
            np.nanmean(df.loc[(~df.CoM_sugg) & (df.subjid == subj), 'resp_len']))
    print('Mean +- SEM of difference in MT rev vs non_rev')
    print(np.nanmean(mt_x_sub_rev)*1e3)
    print('+-')
    print(np.nanstd(mt_x_sub_rev)*1e3/np.sqrt(15))


# ---MAIN
if __name__ == '__main__':
    plt.close('all')
    f1 = False
    f2 = False
    f3 = False
    f4 = False
    f5 = False
    f6 = False
    f7 = False
    com_threshold = 8
    if f1 or f2 or f3 or f5:
        all_rats = True
        if all_rats:
            subjects = ['LE42', 'LE43', 'LE38', 'LE39', 'LE85', 'LE84', 'LE45',
                        'LE40', 'LE46', 'LE86', 'LE47', 'LE37', 'LE41', 'LE36',
                        'LE44']
            # subjects = ['LE37', 'LE36', 'LE39', 'LE46', 'LE47', 'LE85', 'LE43',
            #             'LE40']
            # subjects = ['LE43', 'LE42']
            # with silent: 42, 43, 44, 45, 46, 47
        else:
            subjects = ['LE43']
            # good ones for fitting: 42, 43, 38
        df_all = pd.DataFrame()
        for sbj in subjects:
            df = edd2.get_data_and_matrix(dfpath=DATA_FOLDER + sbj, return_df=True,
                                          sv_folder=SV_FOLDER, after_correct=True,
                                          silent=True, all_trials=True,
                                          srfail=True)
            if all_rats:
                df_all = pd.concat((df_all, df), ignore_index=True)
            else:
                subjects = [None]
        if all_rats:
            df = df_all
            df_all = []
        # XXX: can we remove the code below or move it to the fig5 part?
        zt = np.nansum(df[["dW_lat", "dW_trans"]].values, axis=1)
        df['allpriors'] = zt
        hit = np.array(df['hithistory'])
        stim = np.array([stim for stim in df.res_sound])
        coh = np.array(df.coh2)
        com = df.CoM_sugg.values
        decision = np.array(df.R_response) * 2 - 1
        traj_stamps = df.trajectory_stamps.values
        traj_y = df.trajectory_y.values
        fix_onset = df.fix_onset_dt.values
        fix_breaks = np.vstack(np.concatenate([df.sound_len/1000,
                                               np.concatenate(df.fb.values)-0.3]))
        sound_len = np.array(df.sound_len)
        gt = np.array(df.rewside) * 2 - 1
        trial_index = np.array(df.origidx)
        resp_len = np.array(df.resp_len)
        time_trajs = edd2.get_trajs_time(resp_len=resp_len,
                                         traj_stamps=traj_stamps,
                                         fix_onset=fix_onset, com=com,
                                         sound_len=sound_len)
        if f3 or f5:
            subjid = df.subjid.values
            print('Computing CoMs')
            _, time_com, peak_com, com =\
                edd2.com_detection(trajectories=traj_y, decision=decision,
                                   time_trajs=time_trajs,
                                   com_threshold=com_threshold)
            print('Ended Computing CoMs')
            com = np.array(com)  # new CoM list
            df['CoM_sugg'] = com
        df['norm_allpriors'] = norm_allpriors_per_subj(df)
        df['time_trajs'] = time_trajs

    # fig 1
    if f1:
        print('Plotting Figure 1')
        fig_rats_behav_1(df_data=df)

    # fig 2
    if f2:
        print('Plotting Figure 2')
        fig_trajs_2(df=df.loc[df.soundrfail == 0])

    # fig 3
    if f3:
        print('Plotting Figure 3')
        fig_CoMs_3(df=df, peak_com=peak_com, time_com=time_com)
        supp_com_marginal(df)

    # fig 5 (model)
    if f5:
        with_fb = False
        print('Plotting Figure 5')
        # we can add extra silent to get cleaner fig5 prior traj
        n_sil = 0
        # trials where there was no sound... i.e. silent for simul
        stim[df.soundrfail, :] = 0
        num_tr = int(len(decision))
        decision = np.resize(decision[:int(num_tr)], num_tr + n_sil)
        zt = np.resize(zt[:int(num_tr)], num_tr + n_sil)
        sound_len = np.resize(sound_len[:int(num_tr)], num_tr + n_sil)
        coh = np.resize(coh[:int(num_tr)], num_tr + n_sil)
        com = np.resize(com[:int(num_tr)], num_tr + n_sil)
        gt = np.resize(gt[:int(num_tr)], num_tr + n_sil)
        trial_index = np.resize(trial_index[:int(num_tr)], num_tr + n_sil)
        hit = np.resize(hit[:int(num_tr)], num_tr + n_sil)
        special_trial = np.resize(df.special_trial[:int(num_tr)], num_tr + n_sil)
        subjid = np.resize(np.array(df.subjid)[:int(num_tr)], num_tr + n_sil)
        special_trial[int(num_tr):] = 2
        # special_trial[df.soundrfail.values] = 2
        if stim.shape[0] != 20:
            stim = stim.T
        stim = np.resize(stim[:, :int(num_tr)], (20, num_tr + n_sil))
        stim[:, int(num_tr):] = 0  # for silent simulation
        hit_model, reaction_time, com_model_detected, resp_fin, com_model,\
            _, trajs, x_val_at_updt =\
            run_simulation_different_subjs(stim=stim, zt=zt, coh=coh, gt=gt,
                                           trial_index=trial_index, num_tr=num_tr,
                                           subject_list=subjects, subjid=subjid)
        # basic_statistics(decision=decision, resp_fin=resp_fin)  # dec
        # basic_statistics(com, com_model_detected)  # com
        # basic_statistics(hit, hit_model)  # hit
        MT = [len(t) for t in trajs]
        df_sim = pd.DataFrame({'coh2': coh, 'avtrapz': coh, 'trajectory_y': trajs,
                               'sound_len': reaction_time,
                               'rewside': (gt + 1)/2,
                               'R_response': (resp_fin+1)/2,
                               'resp_len': np.array(MT)*1e-3})
        df_sim['CoM_sugg'] = com_model.astype(bool)
        df_sim['traj_d1'] = [np.diff(t) for t in trajs]
        df_sim['aftererror'] =\
            np.resize(np.array(df.aftererror)[:int(num_tr)], num_tr + n_sil)
        df_sim['subjid'] = subjid
        df_sim['origidx'] = trial_index
        df_sim['special_trial'] = special_trial
        df_sim['traj'] = df_sim['trajectory_y']
        df_sim['com_detected'] = com_model_detected.astype(bool)
        df_sim['peak_com'] = np.array(x_val_at_updt)
        df_sim['hithistory'] = np.array(resp_fin == gt)
        df_sim['soundrfail'] = np.resize(df.soundrfail.values[:int(num_tr)],
                                         num_tr + n_sil)
        df_sim['allpriors'] = zt
        df_sim['norm_allpriors'] = norm_allpriors_per_subj(df_sim)
        # simulation plots
        means, errors = mt_weights(df, means_errs=True, ax=None)
        means_model, errors_model = mt_weights(df_sim, means_errs=True, ax=None)
        if not with_fb:
            df_sim = df_sim[df_sim.sound_len.values >= 0]
        # memory save:
        stim = []
        traj_y = []
        trial_index = []
        special_trial = []
        # df = []
        gt = []
        subjid = []
        traj_stamps = []
        fix_onset = []
        fix_breaks = []
        resp_len = []
        time_trajs = []
        # actual plot
        fig_5(coh=coh, sound_len=sound_len, zt=zt,
              hit_model=hit_model, sound_len_model=reaction_time.astype(int),
              decision_model=resp_fin, com=com, com_model=com_model,
              com_model_detected=com_model_detected,
              means=means, errors=errors, means_model=means_model,
              errors_model=errors_model, df_sim=df_sim)
        fig, ax = plt.subplots(ncols=2, nrows=1)
        ax = ax.flatten()
        ax[0].set_title('Data')
        mt_matrix_vs_ev_zt(df, ax[0], silent_comparison=False, collapse_sides=True)
        ax[1].set_title('Model')
        mt_matrix_vs_ev_zt(df_sim, ax[1], silent_comparison=False,
                           collapse_sides=True)
        # fig.suptitle('DATA (top) vs MODEL (bottom)')
        mt_vs_stim_cong(df_sim, rtbins=np.linspace(0, 80, 9), matrix=False)
        # supp_trajs_prior_cong(df_sim, ax=None)
        # model_vs_data_traj(trajs_model=trajs, df_data=df)
        if f4:
            fig_trajs_model_4(trajs_model=trajs, df_data=df,
                              reaction_time=reaction_time)
    if f6:
        print('Plotting Figure 6')
        # human traj plots
        fig_humans_6(user_id='idibaps_alex', sv_folder=SV_FOLDER, max_mt=600,
                     wanted_precision=12, nm='300')
    if f7:
        fig_7(df, df_sim)
