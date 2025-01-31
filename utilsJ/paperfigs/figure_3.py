import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.pylab as pl
import os
import sys
sys.path.append("/home/jordi/Repos/custom_utils")  # alex idibaps
sys.path.append('C:/Users/alexg/Onedrive/Documentos/GitHub/custom_utils')  # Alex
# sys.path.append("C:/Users/agarcia/Documents/GitHub/custom_utils")  # Alex CRM
# sys.path.append("/home/garciaduran/custom_utils")  # Cluster Alex
sys.path.append("/home/molano/custom_utils") # Cluster Manuel
import utilsJ.paperfigs.fig2 as fig2
from utilsJ.paperfigs import figures_paper as fp
from utilsJ.Behavior.plotting import tachometric, com_heatmap, trajectory_thr,\
    interpolapply

COLOR_COM = 'coral'
COLOR_NO_COM = 'tab:cyan'


def com_detection(df, data_folder, com_threshold=5, rerun=False, save_dat=False):
    trajectories = df.trajectory_y.values
    decision = np.array(df.R_response.values) * 2 - 1
    time_trajs = df.time_trajs.values
    subjects = df.subjid.unique()
    time_com_all = []
    peak_com_all = []
    comlist_all = []
    for subj in subjects:
        idx_sbj = df.subjid == subj
        trajs = trajectories[idx_sbj]
        dec = decision[idx_sbj]
        t_trajs = time_trajs[idx_sbj]
        com_data = data_folder + subj + '/traj_data/' + subj + '_detected_coms.npz'
        os.makedirs(os.path.dirname(com_data), exist_ok=True)
        if os.path.exists(com_data) and not rerun:
            com_data = np.load(com_data, allow_pickle=True)
            time_com = com_data['time_com'].tolist()
            peak_com = com_data['peak_com'].tolist()
            comlist = com_data['comlist'].tolist()
        else:   
            time_com = []
            peak_com = []
            comlist = []
            for i_t, traj in enumerate(trajs):
                if len(traj) > 1 and max(np.abs(traj)) > 100:
                    comlist.append(False)
                else:
                    if len(traj) > 1 and len(t_trajs[i_t]) > 1 and\
                    sum(np.isnan(traj)) < 1 and sum(t_trajs[i_t] > 1) >= 1:
                        traj -= np.nanmean(traj[
                            (t_trajs[i_t] >= -100)*(t_trajs[i_t] <= 0)])
                        signed_traj = traj*dec[i_t]
                        if abs(traj[t_trajs[i_t] >= 0][0]) < 20:
                            peak = min(signed_traj[t_trajs[i_t] >= 0])
                            if peak < 0:
                                peak_com.append(peak)
                            if peak < -com_threshold:
                                time_com.append(
                                    t_trajs[i_t]
                                    [np.where(signed_traj == peak)[0]][0])
                                comlist.append(True)
                            else:
                                comlist.append(False)
                        else:
                            comlist.append(False)
                    else:
                        comlist.append(False)
            if save_dat:
                data = {'time_com': time_com, 'comlist': comlist,
                        'peak_com': peak_com}
                np.savez(com_data, **data)
        time_com_all += time_com
        peak_com_all += peak_com
        comlist_all += comlist
    return time_com_all, peak_com_all, comlist_all

def plot_proportion_corr_com_vs_stim(df, ax=None):
    if ax is None:
        _, ax = plt.subplots(1)
    fp.rm_top_right_lines(ax)
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
    for ev in np.unique(coh):
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
    ax.errorbar(np.unique(coh), m_corr, std_corr, color='k', marker='o', label='Reversal')
    # ax.errorbar(np.unique(coh), m_corr_norm, std_corr_norm, color='r',
    #             marker='o', label='No-Reversal')
    ax.set_xlabel('Stimulus evidence')
    ax.set_ylabel('Reversal accuracy')
    ax.set_xticks([0, 0.25, 0.5, 1])
    ax.set_xticklabels(['0', '0.25', '0.5', '1'])
    # ax.legend()


def plot_coms_single_session(df, ax):
    fp.rm_top_right_lines(ax)
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


def tracking_image(ax, rat_com_img, margin=.004):
    ax.axhline(y=50, linestyle='--', color='k', lw=.5)
    ax.axhline(y=210, linestyle='--', color='k', lw=.5)
    ax_scrnsht = ax
    pos = ax_scrnsht.get_position()
    ax_scrnsht.set_position([pos.x0-pos.width/10, pos.y0, pos.width,
                             pos.height])
    # add colorbar for screenshot
    n_stps = 100
    ax_clbr = plt.axes([pos.x0+pos.width*1/7, pos.y0+pos.height/1.05+margin,
                        pos.width*0.6, pos.height/15])
    ax_clbr.imshow(np.linspace(0, 1, n_stps)[None, :], aspect='auto')
    ax_clbr.set_xticks([0, n_stps-1])
    ax_clbr.set_xticklabels(['0', '400ms'])
    ax_clbr.tick_params(labelsize=9)
    # ax_clbr.set_title('$N_{max}$', fontsize=6)
    ax_clbr.set_yticks([])
    ax_clbr.xaxis.set_ticks_position("top")
    rat = plt.imread(rat_com_img)
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
        avtrapz_mod = np.round(df_data.avtrapz.values, 2)*5
        df_data['avtrapz_mod'] = avtrapz_mod 
        tachometric(df_data, ax=ax_tach, fill_error=True, rtbins=rtbins,
                    cmap='gist_yarg', evidence='avtrapz_mod')
    else:
        tachometric(df_data, ax=ax_tach, fill_error=True, cmap='gist_yarg')
    ax_tach.axhline(y=0.5, linestyle='--', color='k', lw=0.5)
    ax_tach.set_xlabel('Reaction time (ms)')
    ax_tach.set_ylabel('Accuracy')
    ax_tach.set_ylim(0.3, 1.04)
    ax_tach.spines['right'].set_visible(False)
    ax_tach.spines['top'].set_visible(False)
    colormap = pl.cm.gist_gray_r(np.linspace(0.4, 1, 4))
    legendelements = [Line2D([0], [0], color=colormap[3], lw=1.5,
                             label='1'),
                      Line2D([0], [0], color=colormap[2], lw=1.5,
                             label='0.5'),
                      Line2D([0], [0], color=colormap[1], lw=1.5,
                             label='0.25'),
                      Line2D([0], [0], color=colormap[0], lw=1.5,
                             label='0')]
    ax_tach.legend(handles=legendelements, fontsize=8, labelspacing=0.01,
                   title='Stimulus')
    # plot Pcoms matrices
    nbins = 7
    matrix_side_0 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=0)
    matrix_side_1 = com_heatmap_paper_marginal_pcom_side(df=df_data, side=1)
    # L-> R
    vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
    pcomlabel_1 = 'Left to right'   # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[0].set_title(pcomlabel_1, fontsize=11.5)
    im = ax_mat[0].imshow(matrix_side_1, vmin=0, vmax=vmax, cmap='magma')
    plt.sca(ax_mat[0])

    pcomlabel_0 = 'Right to reft'  # r'$p(CoM_{L \rightarrow R})$'
    ax_mat[1].set_title(pcomlabel_0, fontsize=11.5)
    im = ax_mat[1].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
    ax_mat[1].yaxis.set_ticks_position('none')
    plt.sca(ax_mat[1])
    cbar = plt.colorbar(im, fraction=0.04)
    cbar.set_label('p (reversal)', rotation=270, labelpad=14)
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
    cbar_right = plt.colorbar(im_2, fraction=0.03, location='top')
    for t in cbar_right.ax.get_yticklabels():
        t.set_fontsize(7.5)
    cbar_right.ax.set_title('p( right)', fontsize=10)
    cbar_right.ax.tick_params(rotation=45)
    # R -> L
    for ax_i in [ax_pright, ax_mat[0], ax_mat[1]]:
        ax_i.set_xlabel('Prior evidence')
        ax_i.set_xticks([0, 3, 6])
        ax_i.set_xticklabels(['L', '', 'R'])
    for ax_i in [ax_pright, ax_mat[0]]:
        ax_i.set_yticks([0, 3, 6])
        ax_i.set_yticklabels(['R', '', 'L'])
        ax_i.set_ylabel('Stimulus evidence')  # , labelpad=-17)
    ax_mat[1].set_yticklabels(['']*nbins)


def com_statistics(peak_com, time_com, ax, mean_mt):
    ax2, ax1 = ax
    fp.rm_top_right_lines(ax1)
    fp.rm_top_right_lines(ax2)
    peak_com = np.array(peak_com)
    ax1.hist(peak_com/75*100, bins=70, range=(-100, -8/75*100), color=COLOR_COM)
    ax1.hist(peak_com/75*100, bins=10, range=(-8/75*100, -0), color=COLOR_NO_COM)
    ax1.set_yscale('log')
    ax1.axvline(-8/75*100, linestyle=':', color='r')
    ax1.set_xlim(-100, 5)
    ax1.set_xlabel('Deflection point (%)')
    ax1.set_ylabel('# Trials')
    ax1.set_yticks([1e2, 1e4])
    ax1.axhline(y=1e2, color='k', linestyle='--', alpha=0.5)
    ax1.axhline(y=1e4, color='k', linestyle='--', alpha=0.5)
    ax2.set_ylabel('# Trials')
    ax2.hist(time_com, bins=80, range=(0, 500), color=COLOR_COM)
    # ax2.set_xlabel('Deflection time (ms)')
    # ax3 = ax2.twiny()
    # ax3.set_xlim(ax2.get_xlim())
    # ax3.set_xticks([0, mean_mt*0.5, mean_mt, mean_mt*1.5],
    #                [0, 50, 100, 150])
    # ax3.spines['right'].set_visible(False)
    # ax3.set_xlabel('Proportion (%)')


def mean_com_traj_aligned_deflection(
        df, ax, data_folder,
        prior_limit=1, rt_lim=300, trajectory='trajectory_y',
        interpolatespace=np.linspace(-700000, 1000000, 1701),
        com_th=8, time_align=True, spat_align=True, redo=True):
    # plots mean com trajectory and mean non-CoM trajectory
    fp.rm_top_right_lines(ax)
    nanidx = df.loc[df[['dW_trans', 'dW_lat']].isna().sum(axis=1) == 2].index
    df['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df.loc[nanidx, 'allpriors'] = np.nan
    df['norm_allpriors'] = fp.norm_allpriors_per_subj(df)
    df['choice_x_prior'] = (df.R_response*2-1) * df.norm_allpriors
    df['choice_x_coh'] = (df.R_response*2-1) * df.coh2
    all_trajs = np.empty((len(df.subjid.unique()), len(interpolatespace)))
    all_trajs[:] = np.nan
    ac_cond = (df.aftererror*1) >= 0
    kw = {"trajectory": trajectory, "align": "action"}
    common_cond = (df.norm_allpriors.abs() <= prior_limit) &\
        ac_cond & (df.special_trial == 0) & (df.sound_len < rt_lim)
    ax.axhline(-8, color='r', linestyle=':')
    ax.axvline(0, color='k', linestyle=':')
    for i_s, subj in enumerate(df.subjid.unique()):
        if subj == 'LE86':
            continue
        indx_trajs = common_cond & (df.CoM_sugg == True) & (df.subjid == subj)
        com_data = data_folder + subj + '/traj_data/' + subj + '_traj_coms.npz'
        os.makedirs(os.path.dirname(com_data), exist_ok=True)
        if os.path.exists(com_data) and not redo:
            com_data = np.load(com_data, allow_pickle=True)
            mat_com = com_data['mat_com'].item()
        else:
            time_com_sub, peak_com_sub, com =\
                com_detection(df=df.loc[indx_trajs],
                              data_folder=data_folder,
                              com_threshold=com_th, rerun=True, save_dat=False)
            mat_com = np.vstack(df.loc[indx_trajs][com]
                                .apply(lambda x: interpolapply(x, **kw),
                                       axis=1).values.tolist())
        mat_trajs = mat_com
        # median_traj = np.nanmedian(mat_trajs, axis=0)
        # offset = np.nanmean(median_traj[(interpolatespace > -100000) &
        #                                 (interpolatespace < 0)])
        decision = df.loc[indx_trajs, 'R_response'][com].values*2-1
        for itr, traj in enumerate(mat_trajs):
            if time_align:
                mat_trajs[itr] = np.roll(traj*decision[itr],
                                         -int(time_com_sub[itr]))
            if spat_align:
                mat_trajs[itr] -= peak_com_sub[itr]
        mean_traj = np.nanmean(mat_trajs, axis=0)
        all_trajs[i_s, :] = mean_traj
        # all_trajs[i_s, :] += -offset
        ax.plot((interpolatespace)/1000, all_trajs[i_s, :], color=COLOR_COM, linewidth=0.8,
                alpha=0.3)
    mean_traj = np.nanmedian(all_trajs, axis=0)
    # mean_traj += -np.nanmean(mean_traj[(interpolatespace > -100000) &
    #                                    (interpolatespace < 0)])
    ax.plot((interpolatespace)/1000, mean_traj, color=COLOR_COM, linewidth=1.8)
    # if time_align:
    #     # ax.set_xlabel('Time (ms)')
        
    #     # ax.text(100, -20, "Detection threshold", color='r')
    # else:
    #     ax.set_xlabel('Time (ms)')
    # if spat_align:
    #     ax.set_ylabel('distance from peak (pixels)')
    # else:
    #     ax.set_ylabel('y-coord')
    ax.set_ylim(-30, 40)
    ax.set_xticks([0, 150])
    # ax.set_title('reversal', fontsize=9.5)
    ax.text(-150, 45, 'deflection', fontsize=9.5)
    ax.set_xlim(-100, 200)


def mean_com_vel(df, ax, data_folder, condition='choice_x_prior', prior_limit=1,
                  after_correct_only=True, rt_lim=300,
                  trajectory=("traj_d1", 1),
                  interpolatespace=np.linspace(-700000, 1000000, 1700),
                  cong=False):
    # plots mean com trajectory and mean non-CoM trajectory
    fp.rm_top_right_lines(ax)
    nanidx = df.loc[df[['dW_trans', 'dW_lat']].isna().sum(axis=1) == 2].index
    df['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df.loc[nanidx, 'allpriors'] = np.nan
    df['norm_allpriors'] = fp.norm_allpriors_per_subj(df)
    df['choice_x_prior'] = (df.R_response*2-1) * df.norm_allpriors
    df['choice_x_coh'] = (df.R_response*2-1) * df.coh2
    bins = np.array([-1.1, 1.1])
    # xlab = 'prior towards response'
    bintype = 'edges'
    all_trajs = np.empty((len(df.subjid.unique()), 1700))
    all_trajs[:] = np.nan
    all_trajs_nocom = np.empty((len(df.subjid.unique()), 1700))
    all_trajs_nocom[:] = np.nan
    if after_correct_only:
        ac_cond = df.aftererror == False
    else:
        ac_cond = (df.aftererror*1) >= 0

    common_cond = (df.norm_allpriors.abs() <= prior_limit) &\
        ac_cond & (df.special_trial == 0) & (df.sound_len < rt_lim)
    for i_s, subj in enumerate(df.subjid.unique()):
        if subj == 'LE86':
            continue
        if cong:
            com_data = data_folder + subj + '/traj_data/' + subj + '_vels_coms_cong.npz'
        if not cong:
            com_data = data_folder + subj + '/traj_data/' + subj + '_vels_coms_inc.npz'
        os.makedirs(os.path.dirname(com_data), exist_ok=True)
        if os.path.exists(com_data):
            com_data = np.load(com_data, allow_pickle=True)
            mat_com = com_data['mat_com'].item()
            mat_nocom = com_data['mat_nocom'].item()
        else:
            if cong:
                indx_trajs = common_cond & (df.CoM_sugg == True) & (df.subjid == subj) \
                & (np.sign(df.choice_x_coh.values) * np.sign(df.choice_x_prior.values) == 1)
            if not cong:
                indx_trajs = common_cond & (df.CoM_sugg == True) & (df.subjid == subj) \
                & (np.sign(df.choice_x_coh.values) * np.sign(df.choice_x_prior.values) == -1)
            _, _, _, mat_com, _, _ =\
                trajectory_thr(df.loc[indx_trajs], condition, bins,
                            collapse_sides=True, thr=30, ax=None, ax_traj=None,
                            return_trash=True, error_kwargs=dict(marker='o'),
                            cmap=None, bintype=bintype,
                            trajectory=trajectory, plotmt=False,
                            color_tr=COLOR_COM, alpha_low=True)
            if cong:
                indx_trajs = common_cond & (df.CoM_sugg == False) & (df.subjid == subj) \
                & (np.sign(df.choice_x_coh.values) * np.sign(df.choice_x_prior.values) == 1)
            if not cong:
                indx_trajs = common_cond & (df.CoM_sugg == False) & (df.subjid == subj) \
                & (np.sign(df.choice_x_coh.values) * np.sign(df.choice_x_prior.values) == -1)
            _, _, _, mat_nocom, _, _ =\
                trajectory_thr(df.loc[indx_trajs], condition, bins,
                            collapse_sides=True, thr=30, ax=None, ax_traj=None,
                            return_trash=True, error_kwargs=dict(marker='o'),
                            cmap=None, bintype=bintype,
                            trajectory=trajectory, plotmt=False, plot_traj=False,
                            alpha_low=True)
            mat_com_vals = -mat_com[0]
            mat_com = {0: mat_com_vals}
            data = {'mat_com': mat_com, 'mat_nocom': mat_nocom}
            np.savez(com_data, **data)
        median_traj = np.nanmedian(mat_com[0], axis=0)
        all_trajs[i_s, :] = median_traj
        all_trajs[i_s, :] += -np.nanmean(median_traj[(interpolatespace > -100000) &
                                                     (interpolatespace < 0)])
        all_trajs_nocom[i_s, :] = np.nanmedian(mat_nocom[0], axis=0)
        # ax.plot((interpolatespace)/1000, all_trajs[i_s, :], color=COLOR_COM, linewidth=0.8,
        #         alpha=0.5)
        # ax.plot((interpolatespace)/1000, all_trajs_nocom[i_s, :], color=COLOR_NO_COM,
        #         linewidth=0.8, alpha=0.5)
    mean_traj = np.nanmedian(all_trajs, axis=0)
    mean_traj += -np.nanmean(mean_traj[(interpolatespace > -100000) &
                                       (interpolatespace < 0)])
    mean_traj_nocom = np.nanmedian(all_trajs_nocom, axis=0)
    mean_traj_nocom += -np.nanmean(mean_traj_nocom[(interpolatespace > -100000) &
                                                   (interpolatespace < 0)])
    if not cong:
        ax.axhline(y=np.nanmax(mean_traj_nocom), color=COLOR_NO_COM, linestyle='--', alpha=0.8)
        ax.axhline(y=-np.nanmax(mean_traj_nocom), color=COLOR_NO_COM, linestyle='--', alpha=0.8)
    if cong:
        linestyle = '--'
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    if not cong:
        linestyle = '-'
        x_val = np.where(np.abs(mean_traj[800:-1]) == np.nanmin(np.abs(mean_traj[800:-1])))[0]
        ax.axvline(x=(interpolatespace[x_val+800])/1000,
                   color='k', linestyle='--', alpha=0.5)
        ax.plot((interpolatespace)/1000, mean_traj, color=COLOR_COM, linewidth=2,
                linestyle=linestyle)
    ax.plot((interpolatespace)/1000, mean_traj_nocom, color=COLOR_NO_COM, linewidth=2,
            linestyle=linestyle)
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Velocity')
    # ax.axhline(y=np.nanmin(mean_traj), color='k', linestyle='--', alpha=0.5)
    ax.set_xlim(-100, 500)
    ax.set_ylim(-0.45, 0.45)
    legendelements = [Line2D([0], [0], color=COLOR_COM, lw=2,
                              label='Detected reversal'),
                      Line2D([0], [0], color=COLOR_NO_COM, lw=2,
                              label='No-reversal'),
                      Line2D([0], [0], color='k', lw=2,
                             label='Inc.'),
                      Line2D([0], [0], color='k', lw=2, linestyle='--',
                             label='Cong.')]
    ax.legend(handles=legendelements, loc='upper right')


def mean_com_traj(df, ax, data_folder, condition='choice_x_prior', prior_limit=1,
                  after_correct_only=True, rt_lim=300,
                  trajectory='trajectory_y',
                  interpolatespace=np.linspace(-700000, 1000000, 1700)):
    # plots mean com trajectory and mean non-CoM trajectory
    fp.rm_top_right_lines(ax)
    nanidx = df.loc[df[['dW_trans', 'dW_lat']].isna().sum(axis=1) == 2].index
    df['allpriors'] = np.nansum(df[['dW_trans', 'dW_lat']].values, axis=1)
    df.loc[nanidx, 'allpriors'] = np.nan
    df['norm_allpriors'] = fp.norm_allpriors_per_subj(df)
    df['choice_x_prior'] = (df.R_response*2-1) * df.norm_allpriors
    df['choice_x_coh'] = (df.R_response*2-1) * df.coh2
    bins = np.array([-1.1, 1.1])
    # xlab = 'prior towards response'
    bintype = 'edges'
    all_trajs = np.empty((len(df.subjid.unique()), 1700))
    all_trajs[:] = np.nan
    all_trajs_nocom = np.empty((len(df.subjid.unique()), 1700))
    all_trajs_nocom[:] = np.nan
    if after_correct_only:
        ac_cond = df.aftererror == False
    else:
        ac_cond = (df.aftererror*1) >= 0

    common_cond = (df.norm_allpriors.abs() <= prior_limit) &\
        ac_cond & (df.special_trial == 0) & (df.sound_len < rt_lim)
    for i_s, subj in enumerate(df.subjid.unique()):
        if subj == 'LE86':
            continue
        com_data = data_folder + subj + '/traj_data/' + subj + '_traj_coms.npz'
        os.makedirs(os.path.dirname(com_data), exist_ok=True)
        if os.path.exists(com_data):
            com_data = np.load(com_data, allow_pickle=True)
            mat_com = com_data['mat_com'].item()
            mat_nocom = com_data['mat_nocom'].item()
        else:
            indx_trajs = common_cond & (df.CoM_sugg == True) & (df.subjid == subj)
            _, _, _, mat_com, _, _ =\
                trajectory_thr(df.loc[indx_trajs], condition, bins,
                            collapse_sides=True, thr=30, ax=None, ax_traj=ax,
                            return_trash=True, error_kwargs=dict(marker='o'),
                            cmap=None, bintype=bintype,
                            trajectory=trajectory, plotmt=False,
                            color_tr=COLOR_COM, alpha_low=True)
            indx_trajs = common_cond & (df.CoM_sugg == False) & (df.subjid == subj)
            _, _, _, mat_nocom, _, _ =\
                trajectory_thr(df.loc[indx_trajs], condition, bins,
                            collapse_sides=True, thr=30, ax=None, ax_traj=ax,
                            return_trash=True, error_kwargs=dict(marker='o'),
                            cmap=None, bintype=bintype,
                            trajectory=trajectory, plotmt=False, plot_traj=False,
                            alpha_low=True)
            data = {'mat_com': mat_com, 'mat_nocom': mat_nocom}
            np.savez(com_data, **data)
        median_traj = np.nanmedian(mat_com[0], axis=0)
        all_trajs[i_s, :] = median_traj
        all_trajs[i_s, :] += -np.nanmean(median_traj[(interpolatespace > -100000) &
                                                     (interpolatespace < 0)])
        all_trajs_nocom[i_s, :] = np.nanmedian(mat_nocom[0], axis=0)
        ax.plot((interpolatespace)/1000, all_trajs[i_s, :], color=COLOR_COM, linewidth=0.8,
                alpha=0.5)
        ax.plot((interpolatespace)/1000, all_trajs_nocom[i_s, :], color=COLOR_NO_COM,
                linewidth=0.8, alpha=0.5)
    mean_traj = np.nanmedian(all_trajs, axis=0)
    mean_traj += -np.nanmean(mean_traj[(interpolatespace > -100000) &
                                       (interpolatespace < 0)])
    mean_traj_nocom = np.nanmedian(all_trajs_nocom, axis=0)
    mean_traj_nocom += -np.nanmean(mean_traj_nocom[(interpolatespace > -100000) &
                                                   (interpolatespace < 0)])
    ax.plot((interpolatespace)/1000, mean_traj, color=COLOR_COM, linewidth=2)
    ax.plot((interpolatespace)/1000, mean_traj_nocom, color=COLOR_NO_COM, linewidth=2)
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('y-coord (pixels)')
    ax.set_ylim(-30, 105)
    ax.set_xlim(-100, 500)
    ax.set_yticks([-25, 0, 25, 50, 75])
    legendelements = [Line2D([0], [0], color=COLOR_COM, lw=2,
                             label='Detected reversal'),
                      Line2D([0], [0], color=COLOR_NO_COM, lw=2,
                             label='No-reversal')]
    # ax.legend(handles=legendelements, loc='upper left')
    ax.axhline(-8, color='r', linestyle=':')
    ax.text(20, -20, "Detection threshold", color='r')


def com_heatmap_marginal_pcom_side_mat(
    df,  # data source, must contain 'avtrapz' and allpriors
    pcomlabel=None, side=0,
    n_points_marginal=None,
    nbins=7,  # nbins for the square matrix
    com_heatmap_kws={},  # avoid binning & return_mat already handled by the functn
    priors_col='norm_allpriors', stim_col='avtrapz',
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

def fig_COMs_per_rat_inset_3(df, ax_inset):
    subjects = df.subjid.unique()
    comlist_rats = []
    for subj in subjects:
        df_1 = df.loc[df.subjid == subj]
        mean_coms = np.nanmean(df_1.CoM_sugg.values)
        comlist_rats.append(mean_coms)
    ax_inset.boxplot(comlist_rats)
    ax_inset.plot(1+np.random.randn(len(comlist_rats))*0.06, comlist_rats, 'o',
                  color='grey', alpha=0.5)
    ax_inset.set_xlim(0.7, 1.3)
    ax_inset.set_xticks([])
    ax_inset.set_title('p(reversal)', fontsize=10.5)
    # ax_inset.set_ylabel('# Rats')


def mt_distros(df, ax, median_lines=False, mtbins=np.linspace(50, 800, 26),
               sim=False, xlmax=755):
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
            label='Detected reversal', linewidth=1.6)
    ax.plot(xvals, np.nanmean(mt_nocom_mat, axis=1), color=COLOR_NO_COM,
            label='No-reversal', linewidth=1.6)
    if median_lines:
        ax.axvline(np.nanmedian(mt_nocom), color='k')
        ax.axvline(np.nanmedian(mt_com), color='k')
    ax.set_xlim(45, xlmax)
    if not sim:
        ax.legend(loc='center left', bbox_to_anchor=(-0.1, 1.3))
    if sim:
        ax.legend(loc='center left', bbox_to_anchor=(0.1, 1.1))
    ax.set_xlabel('MT (ms)')
    ax.set_ylabel('Density')


def fig_3_CoMs(df, rat_com_img, sv_folder, data_folder, figsize=(11, 5.5),
               com_th=8, inset_sz=.06, marginx=0.9, marginy=0.08):
    fig, ax = plt.subplots(2, 5, figsize=figsize)
    ax = ax.flatten()
    # ax[10].axis('off')
    # ax[11].axis('off')
    plt.subplots_adjust(top=0.95, bottom=0.09, left=0.06, right=0.99,
                        hspace=0.6, wspace=0.5)
    pos_ax_0 = ax[0].get_position()
    ax[0].set_position([pos_ax_0.x0, pos_ax_0.y0, pos_ax_0.width*0.8,
                        pos_ax_0.height])
    ax[1].set_position([pos_ax_0.x0 + pos_ax_0.width*1.2, pos_ax_0.y0,
                        pos_ax_0.width*1.4, pos_ax_0.height])
    pos_ax_2 = ax[2].get_position()
    ax[2].set_position([pos_ax_2.x0 - pos_ax_2.width/11,
                        pos_ax_2.y0 + pos_ax_2.height/6,
                        pos_ax_2.width*0.5, pos_ax_2.height*0.5])
    pos_ax_3 = ax[3].get_position()
    ax[3].set_position([pos_ax_3.x0 - pos_ax_3.width/1.6,
                        pos_ax_3.y0,
                        pos_ax_3.width*1.45, pos_ax_3.height])
    labs = ['a', 'b', '', 'c', 'd', 'e', 'f', 'g', '', 'h', '', '']
    for n, axis in enumerate(ax):
        if n == 7:
            axis.text(-0.12, 1.3, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 4:
            axis.text(-0.17, 2.8, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 0:
            axis.text(-0.12, 1.35, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 1 or n == 2:
            axis.text(-0.12, 1.12, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        elif n == 3:
            axis.text(-0.16, 1.12, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
        else:
            axis.text(-0.12, 1.17, labs[n], transform=axis.transAxes, fontsize=16,
                      fontweight='bold', va='top', ha='right')
    time_com, peak_com, com = com_detection(df=df,
                                            data_folder=data_folder,
                                            com_threshold=com_th)
    com = np.array(com)
    df['CoM_sugg'] = com
    # TRACKING IMAGE PANEL
    ax_trck = ax[0]
    tracking_image(ax_trck, rat_com_img=rat_com_img)
    # TRAJECTORIES PANEL
    plot_coms_single_session(df=df, ax=ax[1])
    # REVERSAL PERCENTAGES PANEL
    fp.rm_top_right_lines(ax=ax[2])
    fig_COMs_per_rat_inset_3(df=df, ax_inset=ax[2])
    # MEAN REVERSAL TRAJECTORY PANEL
    mean_com_traj(df=df, ax=ax[3], data_folder=data_folder, condition='choice_x_prior',
                  prior_limit=1, after_correct_only=True, rt_lim=400,
                  trajectory='trajectory_y',
                  interpolatespace=np.linspace(-700000, 1000000, 1700))
    ax_inset = fp.add_inset(ax=ax[3], inset_sz=0.05, fgsz=(2, 1),
                            marginx=0.105, marginy=0.25, right=True)
    mean_com_traj_aligned_deflection(df=df, ax=ax_inset, data_folder=data_folder,
                                     time_align=True, spat_align=False)
    # REVERSAL STATISTICS PANELS
    ax_com_stat = ax[4]
    pos = ax_com_stat.get_position()
    ax_com_stat.set_position([pos.x0-pos.width/8, pos.y0, pos.width*1.1,
                              pos.height*2/5])
    ax_inset = plt.axes([pos.x0-pos.width/8, pos.y0+pos.height*3.2/5, pos.width*1.1,
                         pos.height*2/5])
    ax_coms = [ax_com_stat, ax_inset]
    pos_ax_9 = ax[9].get_position()
    ax[9].set_position([pos_ax_9.x0-pos.width/8, pos_ax_9.y0,
                        pos_ax_9.width*1.1, pos_ax_9.height])
    mean_mt = np.nanmedian(df.loc[~com, ['resp_len']].values)*1e3
    com_statistics(peak_com=peak_com, time_com=time_com, ax=[ax_coms[1],
                                                              ax_coms[0]],
                    mean_mt=mean_mt)
    # PROPORTION CORRECT COM VS STIM PANEL
    fp.rm_top_right_lines(ax=ax[6])
    plot_proportion_corr_com_vs_stim(df, ax[6])
    # PCOM MATRICES
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
    pcomlabel_1 = 'Right to left'  # r'$p(CoM_{L \rightarrow R})$'
    pcomlabel_0 = 'Left to right'   # r'$p(CoM_{L \rightarrow R})$'
    ax_mat = [ax[7], ax[8]]
    ax_mat[0].set_title(pcomlabel_0, fontsize=10)
    im = ax_mat[0].imshow(np.flipud(matrix_side_1), vmin=0, vmax=vmax, cmap='magma')
    ax_mat[1].set_title(pcomlabel_1, fontsize=10)
    im = ax_mat[1].imshow(np.flipud(matrix_side_0), vmin=0, vmax=vmax, cmap='magma')
    ax_mat[1].yaxis.set_ticks_position('none')
    margin = 0.01
    for ax_i in [ax_mat[0], ax_mat[1]]:
        ax_i.set_xlabel('Prior evidence')
        ax_i.set_xticks([0, 3, 6])
        ax_i.set_xticklabels(['L', '0', 'R'])
        ax_i.set_ylim([-.5, 6.5])
    ax_mat[0].set_yticks([0, 3, 6])
    ax_mat[0].set_yticklabels(['L', '0', 'R'])
    ax_mat[1].set_yticks([])
    pos = ax_mat[0].get_position()
    ax_mat[0].set_position([pos.x0-margin, pos.y0, pos.width,
                                pos.height])
    pos = ax_mat[1].get_position()
    ax_mat[1].set_position([pos.x0-6*margin, pos.y0, pos.width,
                                pos.height])
    pright_cbar_ax = fig.add_axes([pos.x0+pos.width/1.65, pos.y0,
                                   pos.width/12, pos.height/2])
    cbar = fig.colorbar(im, cax=pright_cbar_ax)
    cbar.ax.set_title('     p(rev.)', fontsize=10)
    ax_mat[0].set_ylabel('Stimuluse evidence')
    # COM PROB VERSUS REACTION TIME PANEL
    fig2.e(df, sv_folder=sv_folder, ax=ax[9])
    ax[9].set_ylim(0, 0.075)
    ax[9].set_ylabel('p(reversal)')
    # MT DISTRIBUTIONS PANEL
    fp.rm_top_right_lines(ax=ax[5])
    mt_distros(df=df, ax=ax[5])
    fig.savefig(sv_folder+'fig3.svg', dpi=400, bbox_inches='tight')
    fig.savefig(sv_folder+'fig3.png', dpi=400, bbox_inches='tight')


def supp_com_marginal(df, sv_folder):
    fig, ax = plt.subplots(nrows=5, ncols=6,
                           figsize=(13, 10),
                           gridspec_kw={'top': 0.92, 'bottom': 0.08,
                                        'left': 0.08, 'right': 0.92,
                                        'hspace': 0.4, 'wspace': 0.4})
    ax = ax.flatten()
    for i_ax, subj in enumerate(df.subjid.unique()):
        ax[i_ax*2].text(1.25, 1.25, subj, transform=ax[i_ax*2].transAxes, fontsize=16,
                        va='top', ha='right')
        df_1 = df.loc[df.subjid == subj]
        nbins = 7
        matrix_side_0 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=0)
        matrix_side_1 = com_heatmap_marginal_pcom_side_mat(df=df_1, side=1)
        ax_mat = [ax[i_ax*2], ax[i_ax*2+1]]
        pos_com_0 = ax_mat[0].get_position()
        ax_mat[0].set_position([pos_com_0.x0 + pos_com_0.width*0.3, pos_com_0.y0,
                                pos_com_0.width, pos_com_0.height])
        ax_mat[1].set_position([pos_com_0.x0 + pos_com_0.width*1.4, pos_com_0.y0,
                                pos_com_0.width, pos_com_0.height])
        # L-> R
        vmax = max(np.max(matrix_side_0), np.max(matrix_side_1))
        im = ax[i_ax*2].imshow(matrix_side_1, vmin=0, vmax=vmax, cmap='magma')
        # plt.sca(ax[i_ax*2])
        # plt.colorbar(im, fraction=0.04)
        # R -> L
        im = ax[i_ax*2+1].imshow(matrix_side_0, vmin=0, vmax=vmax, cmap='magma')
        ax[i_ax*2+1].yaxis.set_ticks_position('none')
        plt.sca(ax[i_ax*2+1])
        if (i_ax+1) % 3 == 0:    
            plt.colorbar(im, fraction=0.04, label='p(reversal)')
        else:
            plt.colorbar(im, fraction=0.04)
        for ax_i in [ax[i_ax*2], ax[i_ax*2+1]]:
            ax_i.set_yticklabels(['']*nbins)
            ax_i.set_xticklabels(['']*nbins)
        if i_ax % 3 == 0:
            ax[i_ax*2].set_ylabel('Stimulus evidence')
        if i_ax >= 12:
            ax[i_ax*2].set_xlabel('Prior evidence')
            ax[i_ax*2+1].set_xlabel('Prior evidence')
    fig.savefig(sv_folder+'fig_supp_com_marginal.svg', dpi=400,
                bbox_inches='tight')
    fig.savefig(sv_folder+'fig_supp_com_marginal.png', dpi=400,
                bbox_inches='tight')
