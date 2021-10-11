"""
the idea is to get simulations working with few filepaths and parameters
then simply save a multi-pannel figure report.

so the following function can be called to do kind of a grid-search
"""
import os
from sklearn.model_selection import ParameterGrid
from utilsJ.regularimports import *
from utilsJ.Behavior import plotting, ComPipe
from utilsJ.Models import traj
from concurrent.futures import as_completed, ThreadPoolExecutor
from scipy.stats import ttest_ind, sem
from matplotlib import cm
import swifter
import seaborn as sns
from scipy.stats import norm
import warnings


def get_when_t(a, b, startfrom=700, tot_iter=1000, pval=0.001, nan_policy="omit"):
    """a and b are traj matrices.
    returns ms after motor onset when they split
    startfrom: matrix index to start from (should be 0th position in ms
    tot_iter= remaining)"""
    for i in range(tot_iter):
        t2, p2 = ttest_ind(
            a[:, startfrom + i], b[:, startfrom + i], nan_policy=nan_policy
        )
        if p2 < pval:
            return i  # , np.nanmedian(a[:,startfrom+i])
    return np.nan  # , -1


def when_did_split_dat(df, side, rtbin=0, rtbins=np.linspace(0, 150, 7), startfrom=700):
    """gets when they are statistically different by t_test"""
    # get matrices
    if side == 0:
        coh1 = -1
    else:
        coh1 = 1
    dat = df.loc[
        (df.sound_len < rtbins[rtbin + 1])
        & (df.sound_len >= rtbins[rtbin])
        & (df.resp_len)
    ]  # &(df.R_response==side)
    mata = np.vstack(
        dat.loc[dat.coh2 == coh1]
        .apply(lambda x: plotting.interpolapply(x), axis=1) # removed swifter
        .values.tolist()
    )
    matb = np.vstack(
        dat.loc[(dat.coh2 == 0) & (dat.rewside == side)]
        .apply(lambda x: plotting.interpolapply(x), axis=1) # removed swifter
        .values.tolist()
    )
    for a in [mata, matb]:  # discard all nan rows
        a = a[~np.isnan(a).all(axis=1)]

    ind = get_when_t(mata, matb, startfrom=startfrom)
    return ind  # mata, matb,


def shortpad(traj, upto=1000):
    """pads nans to trajectories so it can be stacked in a matrix"""
    missing = upto - traj.size
    return np.pad(traj, ((0, missing)), "constant", constant_values=np.nan)


def when_did_split_simul(df, side, rtbin=0, rtbins=np.linspace(0, 150, 7)):
    """gets when they are statistically different by t_test
    here df is simulated df"""
    # get matrices
    if side == 0:
        coh1 = -1
    else:
        coh1 = 1
    dat = df.loc[
        (df.sound_len < rtbins[rtbin + 1])
        & (df.sound_len >= rtbins[rtbin])
        & (df.resp_len)
    ]  # &(df.R_response==side) this goes out
    mata = np.vstack(
        dat.loc[(dat.traj.apply(len) > 0) & (dat.coh2 == coh1), "traj"]
        .apply(shortpad)
        .values.tolist()
    )
    matb = np.vstack(
        dat.loc[
            (dat.traj.apply(len) > 0) & (dat.coh2 == 0) & (dat.rewside == side), "traj"
        ]
        .apply(shortpad)
        .values.tolist()
    )

    for a in [mata, matb]:  # discard all nan rows
        a = a[~np.isnan(a).all(axis=1)]
    #     for mat in [mata, matb]:
    #         plt.plot(
    #         np.nanmedian(mat, axis=0))
    #     plt.show()
    ind = get_when_t(mata, matb, startfrom=0)
    return ind  # mata, matb,


def whole_splitting(df, rtbins=np.arange(0, 151, 25), simul=False):
    """calculates time it takes for each Side*rtbin coherence 1vs0 to split significantly"""
    _index = [0, 1]  # side
    _columns = np.arange(rtbins.size - 1)  # rtbins
    tdf = pd.DataFrame(np.ones((2, _columns.size)) * -1, index=_index, columns=_columns)
    if simul:
        splitfun = when_did_split_simul
    else:
        splitfun = when_did_split_dat
    # tdf.columns = tdf.columns.set_names(['RTbin', 'side'])
    for b in range(rtbins.size - 1):
        for s, side in enumerate(["L", "R"]):
            split_time = splitfun(df, s, b, rtbins=rtbins)
            tdf.loc[s, b] = split_time

    return tdf


def splitplot(df, out, ax):
    """plots trajectory split time (coh1 vs 0) per RT-bin"""
    tdf = whole_splitting(df)
    tdf2 = whole_splitting(out, simul=True)
    colors = ["green", "purple"]
    for i, (dat, name, marker) in enumerate([[tdf, "data", "o"], [tdf2, "simul", "x"]]):
        for j, side in enumerate(["L", "R"]):
            ax.scatter(
                dat.columns,
                dat.loc[j, :].values,
                marker=marker,
                color=colors[j],
                label=f"{name} {side}",
            )

    ax.set_xlabel("rtbin")
    ax.set_ylabel("time to diverge")
    ax.legend(fancybox=False, frameon=False)

def plot_com_contour(df, out, ax):
    """contour of CoM peak vs prior"""
    sns.kdeplot(out.loc[out.CoM_sugg,'CoM_peakf'].apply(lambda x: x[0]).values,
            out.loc[out.CoM_sugg,'allpriors'].values, ax=ax)

def plot_median_com_traj(df, out, ax):
    """median trajectory for CoM, spliting by huge and moderate bias [only right responses]"""
    ax.plot(
        np.nanmedian(
            np.vstack(
            out.loc[(out.prechoice==0)&(out.R_response==1) & (out.allpriors<-1.25), 'traj'].dropna().apply(lambda x: shortpad(x, upto=700)).values),
            axis=0
        ),
        label = 'huge bias'
    )
    ax.plot(
        np.nanmedian(
            np.vstack(
        out.loc[(out.prechoice==0) &(out.R_response==1)& (out.allpriors.abs()<1.25), 'traj'].dropna().apply(lambda x: shortpad(x, upto=700)).values),
        axis=0),
        label = 'moderate to 0 bias'
    )
    ax.set_xlim([0,300])
    ax.set_xlabel('ms from movement onset')
    ax.set_ylabel('distance in px')
    ax.legend()


def plot0(df, out, ax):
    """RT distributions"""
    df.loc[(df.sound_len < 250)].sound_len.hist(
        bins=np.linspace(0, 250, 101),
        ax=ax,
        label="data",
        density=True,
        alpha=0.5,
        grid=False,
    )
    out.sound_len.hist(
        bins=np.linspace(0, 250, 101),
        ax=ax,
        label="simul all",
        density=True,
        alpha=0.5,
        grid=False,
    )
    ax.set_xlabel("RT (ms)")
    ax.set_title("RT distr")
    ax.legend(frameon=False, fancybox=False)


def pcomRT(df, out, ax):
    """p(CoM) vs RT"""
    plotting.binned_curve(
        df,
        "CoM_sugg",
        "sound_len",
        bins=np.linspace(0, 250, 26),
        xpos=10,
        xoffset=5,
        ax=ax,
        errorbar_kw=dict(label="data", color="tab:blue"),
        legend=False,
        traces="sstr",
        traces_kw=dict(color="grey", alpha=0.3, ls="-"),
    )
    plotting.binned_curve(
        out,
        "CoM_sugg",
        "sound_len",
        bins=np.linspace(0, 250, 26),
        xpos=10,
        xoffset=5,
        ax=ax,
        errorbar_kw=dict(label="simul", color="tab:orange"),
        legend=False,
        traces="sstr",
        traces_kw=dict(color="grey", alpha=0.3, ls=":"),
    )
    plotting.binned_curve(
        out.loc[out.reactive == 0],
        "CoM_sugg",
        "sound_len",
        bins=np.linspace(0, 250, 26),
        xpos=10,
        xoffset=5,
        ax=ax,
        errorbar_kw=dict(label="simul proactive", color="tab:purple"),
        legend=False,
        #traces="sstr",
        #traces_kw=dict(color="grey", alpha=0.3, ls=":"),
    )
    ax.set_ylabel("p(CoM)")
    ax.set_xlabel("RT(ms)")
    ax.set_title("pcom vs rt")
    ax.legend(frameon=False, fancybox=False)


def pcomRT_proactive_only(df, out, ax):
    """deprecated"""
    plotting.binned_curve(
        out.loc[out.reactive == 0],
        "CoM_sugg",
        "sound_len",
        bins=np.linspace(0, 250, 26),
        xpos=10,
        xoffset=5,
        ax=ax,
        errorbar_kw=dict(label="simul", color="tab:orange"),
        legend=False,
        #traces="sstr",
        traces_kw=dict(color="grey", alpha=0.3, ls=":"),
    )
    ax.set_ylabel("p(CoM)")
    ax.set_xlabel("RT(ms)")
    ax.set_title("pcom in proactive")
    ax.legend(frameon=False, fancybox=False)


def plot2(df, out, ax):
    """MT distribution"""
    df.resp_len.hist(
        bins=np.linspace(0, 1, 81),
        ax=ax,
        label="data",
        density=True,
        alpha=0.5,
        grid=False,
    )
    out.resp_len.hist(
        bins=np.linspace(0, 1, 81),
        ax=ax,
        label="simul all",
        density=True,
        alpha=0.5,
        grid=False,
    )
    ax.set_xlabel("MT (secs)")
    ax.set_title("MT distr")
    ax.legend(frameon=False, fancybox=False)


def plot3(df, out, ax):
    """U shape MT vs RT"""
    titles = ["data all", "simul all"]
    datacol = ["resp_len", "resp_len"]
    traces_ls = ["-", ":"]
    for i, dfobj in enumerate([df, out]):  # .loc[out.reactive==0]
        plotting.binned_curve(
            dfobj,
            datacol[i],
            "sound_len",
            ax=ax,
            bins=np.linspace(0, 150, 16),
            # xpos=np.arange(0,150,10), traces='sstr', traces_kw = dict(color='grey', alpha=0.3, ls=traces_ls[i]),
            xpos=10,
            traces="sstr",
            traces_kw=dict(color="grey", alpha=0.3, ls=traces_ls[i]),
            xoffset=5,
            errorbar_kw={"ls": "none", "marker": "o", "label": titles[i]},
        )
        ax.set_xlabel("RT (ms)")
        ax.set_ylabel("MT (s)")
        ax.set_title("MT vs RT")
        ax.legend(frameon=False, fancybox=False)


def plot4(df, out, ax):
    """proportion of proactive trials"""
    counts_t, xpos = np.histogram(out.sound_len, bins=np.linspace(0, 250, 26))
    counts_p, _ = np.histogram(
        out.loc[out.reactive == 0, "sound_len"], bins=np.linspace(0, 250, 26)
    )
    prop_pro = counts_p / counts_t
    ax.plot(xpos[:-1] + 5, prop_pro, marker="o")
    ax.set_ylabel("proportion proactive")
    ax.set_xlabel("RT")
    ax.set_ylim([-0.05, 1.05])


def plot5(df, out, ax):
    """incomplete"""
    ax.set_title("stimuli split trajectories")
    ax.annotate("splitting time per rtbin", (0, 0))


def plot67(df, out, ax, ax2, rtbins=np.linspace(0, 150, 7)):
    """deprecated"""
    markers = ["o", "x"]
    rtbins = np.linspace(0, 150, 7)
    priorbins = np.linspace(-2, 2, 6)
    cmap = cm.get_cmap("viridis_r")
    datres, simulres = pd.DataFrame([]), pd.DataFrame([])
    for i, (dat, store) in enumerate([[df, datres], [out, simulres]]):
        dat["priorbin"] = pd.cut(
            dat.choice_x_allpriors, priorbins, labels=False, include_lowest=True
        )
        for j in range(rtbins.size - 1):
            tmp = (
                dat[(dat.sound_len >= rtbins[j]) & (dat.sound_len < rtbins[j + 1])]
                .groupby("priorbin")["time_to_thr"]
                .agg(m="mean", e=sem)
            )
            store[f"rtbin{j}"] = tmp["m"]

            if j % 2 == 0:  # plot half of it
                kws = {
                    "ls": "none",
                    "marker": markers[i],
                    "color": cmap(j / (rtbins.size - 1)),
                    "capsize": 2,
                }
                if not i:
                    kws = {
                        "ls": "none",
                        "marker": markers[i],
                        "label": f"rtbin={j}",
                        "color": cmap(j / (rtbins.size - 1)),
                        "capsize": 2,
                    }
                ax.errorbar(tmp.index, tmp["m"], yerr=tmp["e"], **kws)
    ax.legend().remove()
    ax.set_ylabel("ms to threshold (30px)")
    ax.set_xlabel("congruence (choice * prior)")
    ax.set_title("prior congruence on MT (o=data, x=simul)")
    diffdf = datres - simulres
    ax2.axhline(0, c="gray", ls=":")
    ax2.set_xlabel("congruence (choice * prior)")
    ax2.set_ylabel("data - simul")
    for i in range(rtbins.size - 1):
        ax2.scatter(
            [-2, -1, 0, 1, 2],
            diffdf[f"rtbin{i}"].values,
            color=cmap(i / (rtbins.size - 1)),
            label=f"rtbin {i}",
        )
    ax2.set_title("prior congruence on MT (data - simul)")
    ax2.legend(frameon=False, fancybox=False)


def plot910(df, out, ax, ax2, rtbins=np.linspace(0, 150, 7)):
    """deprecated"""
    markers = ["o", "x"]
    cmap = cm.get_cmap("viridis_r")
    datres, simulres = pd.DataFrame([]), pd.DataFrame([])
    for i, (dat, store) in enumerate([[df, datres], [out, simulres]]):
        kwargs = dict(ls="none", marker=markers[i], capsize=2)
        for j in range(rtbins.size - 1):
            tmp = (
                dat[(dat.sound_len >= rtbins[j]) & (dat.sound_len < rtbins[j + 1])]
                .groupby("choice_x_coh")["time_to_thr"]
                .agg(m="mean", e=sem)
            )
            store[f"rtbin{j}"] = tmp["m"]
            if j % 2 == 0:
                c = cmap(j / (rtbins.size - 1))
                ax.errorbar(tmp.index, tmp["m"], yerr=tmp["e"], **kwargs, c=c)
    ax.set_xlabel("coh * choice")
    ax.set_ylabel("ms to threshold (30px)")
    ax.set_title("coherence congruence on MT (o=data, x=simul)")
    diffdf = datres - simulres
    ax2.axhline(0, c="gray", ls=":")
    ax2.set_xlabel("coh * choice")
    ax2.set_ylabel("data - simul")
    ax2.set_title("coherence congruence on MT (data - simul)")
    for i in range(rtbins.size - 1):
        ax2.scatter(
            diffdf.index,
            diffdf[f"rtbin{i}"].values,
            color=cmap(i / (rtbins.size - 1)),
            label=f"rtbin {i}",
        )

    ax2.legend(frameon=False, fancybox=False)


def plot1112(df, out, ax, ax2):
    """data and simul CoM Matrix """

    # get max p(com) so colorbars are the same
    subset = df.dropna(subset=["avtrapz", "allpriors", "CoM_sugg"])
    mat_data, _ = plotting.com_heatmap(
        subset.allpriors,
        subset.avtrapz,
        subset.CoM_sugg,
        return_mat=True
    )
    subset = out.dropna(subset=["avtrapz", "allpriors", "CoM_sugg"])
    mat_simul, _ = plotting.com_heatmap(
        subset.allpriors,
        subset.avtrapz,
        subset.CoM_sugg,
        return_mat=True
    )
    maxval = np.max(np.concatenate([
        mat_data.flatten(), mat_simul.flatten()
    ]))

    subset = df.dropna(subset=["avtrapz", "allpriors", "CoM_sugg"])
    plotting.com_heatmap(
        subset.allpriors,
        subset.avtrapz,
        subset.CoM_sugg,
        flip=True,
        ax=ax,
        cmap="magma",
        fmt=".0f",
        vmin=0,
        vmax=maxval
    )
    ax.set_title(f"data p(CoM)")
    subset = out.dropna(subset=["avtrapz", "allpriors", "CoM_sugg"])
    plotting.com_heatmap(
        subset.allpriors,
        subset.avtrapz,
        subset.CoM_sugg,
        flip=True,
        ax=ax2,
        cmap="magma",
        fmt=".0f",
        vmin=0,
        vmax = maxval
    )
    ax2.set_title(f" SIMULATIONS p(CoM)")


def _callsimul(args):
    """unpacks all args so we can use concurrent futures with traj.simul_psiam"""
    return traj.simul_psiam(*args)


def safe_threshold(row, threshold):
    pass  # will this be implemented?


def whole_simul(
    subject, 
    savpath=None,
    dfpath=f"/home/jordi/DATA/Documents/changes_of_mind/data/paper/",#dani_clean.pkl",  # parameter grid
    rtbins=np.linspace(0, 150, 7), # deprecated ~ not yet
    params={
        "t_update": 80, # ms
        "proact_deltaMT": 0.3,
        "reactMT_interc": 110,
        "reactMT_slope": 0.15,
        "com_gamma": 250,
        "glm2Ze_scaling": 0.25,
        "x_e0_noise": 0.001,
        "naive_jerk": True,
        "confirm_thr": 0,
        "proportional_confirm": False,
        "t_update_noise":0,
        "com_deltaMT":0, # 0 = no modulation
        "jerk_lock_ms":0
    },
    batches=10,
    batch_size=1500,
    return_data=False,
    vanishing_bounds=False,
    both_traj=False,
    silent_trials=False,
    sample_silent_only=False,
    trajMT_jerk_extension=0,
    mtnoise=True,
    com_height=5,
    drift_multiplier=1,
    extra_t_0_e = 0, # secs
    use_fixed_bias = False

):  
    """
    subject: 'LEXX' subject to simulate, since several params (psiam and silentMT are loaded from fits)
    savpath: where to save resulting multi-pannel figure
    dfpath: path where the data is stored. If it doe snot end with .pkl attempts appending {subject}_clean.pkl
    rtbins: reaction time bins, semi deprecated
    params: parameters to simulate
        t_update: time it takes from bound hit to exert effect in movement
        pract_deltaMT: coef to reduce expected MT based on accumulated evidence
        reactMT_interc: intercept of reactive MT
        reactMT_slope: slope of reactive MT (* trial_index)
        com_gamma: motor time from updating trajectory to new (reverted) choice
        glm2Ze_scaling: factor to scale down Ze (= Ze * glm2Ze_scaling * bound_height)
        x_e0_noise: variance of the beta distr. centered at scaled Ze
        naive_jerk: whether to use 
            True => boundary conditions = (0,0,0,75,0,0) or 
            False=> those fitted using alex EM procedure (deprecated)
        confirm_thr: use some confirm threshold (ie evidence decision criterion != 0). units fraction of bound_height
        proportional_confirm: whether to make it proportional to Ze/x_0_e
        t_update_noise: scale of the gaussian noise to be added to t_update. (derpecated)
        com_deltaMT: coef to reduce CoM MT based on accumulated evidence
        jerk_lock_ms: ms of trajectory which keep locked @ y=0
    batches: number of simulation batches
    batch_size: amount of trials simulated per batch (too high -> memory errors)
    return_data: deprecated
    vanishing_bounds: whether to disable horizontal bounds after AI hits the bound till ev bounds collapse
    both_traj: whether to return both trajectories in out dataframe (preplanned + final) or not (just final)
    silent_trials: just simulate silent trials
    sample_silent_only: only sample silent trials from data to simulate
    trajMT_jerk_extension: ms of extension of the trajectory to simulate. Since subjects do not break
        lateral photogate with x'=0 and x''=0 it may help getting simulated trajectories that resemble data
    mtnoise: whether to add noise to predicted "expected MT". If float it adds gaussian noise scaled to that value * mae
    com_height: com detection threshold in pxfor simulated data. Real data is already thresholded/detected at 5px
    drift_multiplier: multiplies fited values of drift. It can be an array of shape (4,)
    extra_t_0_e: extends t_0_e for this amound of SECONDS
    """
    # dev note
    if use_fixed_bias:
        raise NotImplementedError(
            'fixed bias usage is not implemented because it might require to fit expectedMT again'
            )
    # append subject to data path
    if not dfpath.endswith('.pkl'): # use default naming
        dfpath = f"{dfpath}{subject}_clean.pkl"

    # if savpath is None:
    #     raise ValueError("provide save path")

    # load real data
    df = pd.read_pickle(dfpath)
    # ensure we just have a single subject
    df = df.loc[df.subjid == subject]
    df["sstr"] = df.coh2.abs() # stimulus str column
    df["priorZt"] = np.nansum(
        df[["dW_lat", "dW_trans"]].values, axis=1
    )  # 'dW_fixedbias' not considered in the evidence offset/pre-planned choice anymore*
    df["prechoice"] = np.ceil(df.priorZt.values / 1000) # pre-planned choice
    df["prechoice"] = df.prechoice.astype(int)
    df["time_to_thr"] = np.nan # initialize variable: time to reach arbitrary threshold in px
    # df.swifter.apply(lambda x: np.argmax(np.abs(plotting.interpolapply(x)[700:])>30), axis=1)
    # split lft and right now!
    df.loc[(df.R_response == 1) & (df.trajectory_y.apply(len) > 10), "time_to_thr"] = (
        df.loc[(df.R_response == 1) & (df.trajectory_y.apply(len) > 10)]
        .dropna(subset=["sound_len"])
        .apply(
            lambda x: np.argmax(plotting.interpolapply(x)[700:] > 30), axis=1 # from 700 because they are aligned
            # to movement onset at 700 position (extreme case [fixation]+[stim]=700)
        )
    )  # axis arg not req. in series
    df.loc[(df.R_response == 0) & (df.trajectory_y.apply(len) > 10), "time_to_thr"] = (
        df.loc[(df.R_response == 0) & (df.trajectory_y.apply(len) > 10)]
        .dropna(subset=["sound_len"])
        .apply(
            lambda x: np.argmax(plotting.interpolapply(x)[700:] < -30), axis=1
        )
    )  # axis arg not req. in series
    df["rtbin"] = pd.cut(df.sound_len, rtbins, labels=False, include_lowest=True)
    df["choice_x_coh"] = (df.R_response * 2 - 1) * df.coh2
    df["allpriors"] = np.nansum(
        df[["dW_trans", "dW_lat"]].values, axis=1
    )  # , 'dW_fixedbias'
    df["choice_x_allpriors"] = (df.R_response * 2 - 1) * df.allpriors

    # load and unpack psiam parameters
    psiam_params = loadmat(
        f"/home/jordi/DATA/Documents/changes_of_mind/data/paper/fits_psiam/{subject} D2Mconstrainedfit_fitonly.mat"
    )["freepar_hat"][0]
    (
        c,
        v_u,
        a_u,
        t_0_u,
        *v,
        a_e,
        z_e,
        t_0_e,
        t_0_e_silent,
        v_trial,
        b,
        d,
        _,
        _,
        _,
    ) = psiam_params
    assert extra_t_0_e<1, f't_0_e is in seconds, it should not be greater than 1 and it is {extra_t_0_e}'
    if extra_t_0_e:
        t_0_e += extra_t_0_e
    
    out = pd.DataFrame([]) # init out dataframe
    
    if sample_silent_only:
        df = df[df.special_trial == 2]
        print(
            f"just sampling from silent trials in subject {subject}\nwhich is around {len(df.loc[df.subjid==subject])}"
        )
    # psiam simulations
    print("psiam_simul began")
    # this runs 7 times so we expect to have n_simul_trials = 7 * nbatches * batch_size
    with ThreadPoolExecutor(max_workers=7) as executor:
        jobs = [
            executor.submit(
                _callsimul,
                [
                    df.loc[df.subjid == subject],
                    f"/home/jordi/DATA/Documents/changes_of_mind/data/paper/fits_psiam/{subject} D2Mconstrainedfit_fitonly.mat",
                    1.3,
                    0.3,
                    1e-4,
                    x, # seed
                    batches,
                    batch_size,
                    params["glm2Ze_scaling"],
                    silent_trials,
                    sample_silent_only,
                    params["x_e0_noise"],
                    params["confirm_thr"],
                    params["proportional_confirm"],
                    params["confirm_ae"],
                    drift_multiplier
                ],
            )
            for x in np.arange(7) * 50  # x is the seed so we do not simulate the same over and over
        ]
        for job in tqdm.tqdm_notebook(as_completed(jobs), total=7):
            out = out.append(job.result(), ignore_index=True)
    # so psiam simulations are already in "out" dataframe

    # initializes a class that will retrieve expected MT
    tr = traj.def_traj(subject, None)
    # initialize some variables
    out["expectedMT"] = np.nan
    out["mu_boundary"] = np.nan
    out["mu_boundary"] = out["mu_boundary"].astype(object) # object because it will contain boundary conditions (vec)

    
    out["priorZt"] = np.nansum(
        out[["dW_lat", "dW_trans"]].values, axis=1
    )  # 'dW_fixedbias',
    out["prechoice"] = np.ceil(out.priorZt.values / 1000)
    out["prechoice"] = out.prechoice.astype(int)

    for col in ["dW_trans", "dW_lat"]:  # invert those factors in left choices to align it to a single dimensino
        out[f"{col}_i"] = out[col] * (out["prechoice"] * 2 - 1)

    try:  ### PROACTIVE RESPONSES
        sdf = out.loc[out.reactive == 0] # create a sliced dataframe of proactive responses to work with
        tr.selectRT(0) # loads subject's MT LinearModel
        # Generate design matrix to multiply with weights 
        fkmat = sdf[["zidx", "dW_trans_i", "dW_lat_i"]].fillna(0).values
        # (cumbersome we could use ".predict" behind scenes instead of doing this raw)
        fkmat = np.insert(fkmat, 0, 1, axis=1) 
        # fkmat = sdf[['zidx', 'dW_trans', 'dW_lat']].fillna(0).values
        # fkmat = np.insert(fkmat, 0, 1,axis=1)
        tr.expected_mt(fkmat, add_intercept=False)
        # store expectedMT in dataframe
        out.loc[sdf.index, "expectedMT"] = tr.mt * 1000 # add expectedMT to those indexes in data frame "out"

        # add noise to the predicted value
        if isinstance(mtnoise, bool):
            mtnoise *= 1
        if mtnoise:  # load mserror
            with open(
                f"/home/jordi/DATA/Documents/changes_of_mind/data/paper/trajectory_fit/MTmse.pkl",
                "rb",
            ) as handle:
                msedict = pickle.load(handle)

            err = mtnoise * msedict[subject] ** 0.5
            out.loc[sdf.index, "expectedMT"] += np.random.normal(
                scale=err, size=out.loc[sdf.index, "expectedMT"].values.size
            ) * 1000 # big bug here, we were using ms already!

            # beware, some noise can make impossible trajectories (ie expectedMT<=0)
            # apply a threshold, expected mT cannot be below 125 ms 
            out.loc[(out.reactive==0)&(out.expectedMT<125), 'expectedMT'] = 125


        if params["naive_jerk"]:
            naive_jerk = np.array([0, 0, 0, 75, 0, 0]).reshape(
                -1, 1
            )  # broadcast final position to port # since it is aligned to final choice, that-s it.
            # It will be aligned later when generating trajectories
            out.loc[sdf.index, f"mu_boundary"] = len(sdf) * [naive_jerk]
        else:
            out.loc[sdf.index, f"mu_boundary"] = tr.return_mu(Fk=fkmat)
            # out.loc[sdf.index, f'priortraj{side}'] = bo.prior_traj(Fk=fkmat,times=bo.mt+0.05,step=10)

        ### REACTIVE ONES
        sdf = out.loc[out.reactive == 1] # create a sliced dataframe of reactive responses to work with
        fkmat = sdf[["zidx", "dW_trans_i", "dW_lat_i"]].fillna(0).values
        fkmat = np.insert(fkmat, 0, 1, axis=1)
        times = (
            sdf.loc[sdf.index, "origidx"].values * params["reactMT_slope"]
            + params["reactMT_interc"]
        )
        out.loc[sdf.index, f"expectedMT"] = times
        if params["naive_jerk"]:
            naive_jerk = np.array([0, 0, 0, 75, 0, 0]).reshape(
                -1, 1
            )  # broadcast final position to port # since it is aligned to final choice, that-s it.
            # It will be aligned later when generating trajectories
            out.loc[sdf.index, f"mu_boundary"] = len(sdf) * [naive_jerk]
        else:
            out.loc[sdf.index, f"mu_boundary"] = tr.return_mu(
                Fk=fkmat
            )  # this one is not used later, right?
            # out.loc[sdf.index, f'priortraj{side}'] = bo.prior_traj(step=10, Fk=fkmat, times=(times+50)/1000)
    except Exception as e:
        raise e

    
    remaining_sensory = (t_0_e - 0.3) * 1000 # that would be t_e delay
    out["remaining_sensory"] = remaining_sensory
    # edit remaining sensory pipe where the stimulus was shorter than it
    out.loc[out.sound_len < remaining_sensory, "remaining_sensory"] = out.loc[
        out.sound_len < remaining_sensory, "sound_len"
    ]
    out["e_after_u"] = 0 # flag for those trials where EA bound is hit after AI
    out.loc[
        (out.e_time * 1000 < out.sound_len + out.remaining_sensory)
        & (out.reactive == 0),
        "e_after_u",
    ] = 1  # control for those which have listened less than the delay # done
    
    out.prechoice = out.prechoice.astype(int)
    out["sstr"] = out.coh2.abs()
    out["t_update"] = np.nan
    
    # effective t_update for most of the trials is params['t_update']
    out.loc[out.reactive == 0, "t_update"] = params[
        "t_update"
    #] + t_0_e # now it happen relative to movement onset!
    ] + t_0_e//0.001 - 300 # new bug


    # UNCOMMENT LINE BELOW IF UPDATE CAN HAPPEN EARLIER WHEN EV-BOUND IS REACHED
    if not vanishing_bounds:
        # adapt t_update in those trials where EA bound is hit after AI bound
        out.loc[out.e_after_u == 1, "t_update"] = (
            out.loc[out.e_after_u == 1, "e_time"]-out.loc[out.e_after_u == 1, "u_time"]
            ) * 1000  + params['t_update']


    if params['t_update_noise']:
        out['t_update'] += np.random.normal(scale=params['t_update_noise'], size=len(out))

    if (out['t_update']<0).sum():
        warnings.warn('replacing t_updates < 0 to 0')
        out.loc[out.t_update<0, 't_update'] = 0

    # add speed up for confirmed choices
    out["resp_len"] = np.nan
    out["resp_len"] = out["expectedMT"]  # this include reactive
    out["base_mt"] = out["expectedMT"]  # this include reactive
    if not silent_trials:
        if params["confirm_thr"] > 0: # if there's confirm_thr scale it relative to delta_ev
            out.loc[
                (out.R_response == out.prechoice) & (out.reactive == 0), "resp_len"
            ] = (
                (
                    1
                    - params["proact_deltaMT"]
                    * out.loc[
                        (out.R_response == out.prechoice) & (out.reactive == 0),
                        "delta_ev",
                    ].abs()
                    / a_e
                )
                * (
                    out.loc[
                        (out.R_response == out.prechoice) & (out.reactive == 0),
                        "resp_len",
                    ]
                    - out.loc[
                        (out.R_response == out.prechoice) & (out.reactive == 0),
                        "t_update",
                    ]
                )
                + out.loc[
                    (out.R_response == out.prechoice) & (out.reactive == 0), "t_update"
                ]
            )  # prechoice==final choice aka confirm
        else: # samething but with x_e instead of delta_ev
            out.loc[
                (out.R_response == out.prechoice) & (out.reactive == 0), "resp_len"
            ] = (
                (
                    1
                    - params["proact_deltaMT"]
                    * out.loc[
                        (out.R_response == out.prechoice) & (out.reactive == 0), "x_e"
                    ].abs()
                    / a_e
                )
                * (
                    out.loc[
                        (out.R_response == out.prechoice) & (out.reactive == 0),
                        "resp_len",
                    ]
                    - out.loc[
                        (out.R_response == out.prechoice) & (out.reactive == 0),
                        "t_update",
                    ]
                )
                + out.loc[
                    (out.R_response == out.prechoice) & (out.reactive == 0), "t_update"
                ]
            )  # prechoice==final choice aka confirm
        
        # changes of mind response length
        out.loc[(out.R_response != out.prechoice) & (out.reactive == 0), "resp_len"] = (
            out.loc[(out.R_response != out.prechoice) & (out.reactive == 0), "t_update"]
            + params["com_gamma"] * (
                1-params['com_deltaMT']
                * out.loc[(out.R_response != out.prechoice) & (out.reactive == 0), 'delta_ev'].abs()
                )
            + params["reactMT_slope"] # why was this shit being added? # else we have a peak around gamma com
            * out.loc[
                (out.R_response != out.prechoice) & (out.reactive == 0), "origidx"
            ]
        )  # tri_ind is new

    out["resp_len"] /= 1000 # transform into seconds so it has same units in df and out
    out["base_mt"] /= 1000 # idem

    # not really elegant, but ensure they are float because we had some object datatype column
    for col in ["zidx", "origidx", "expectedMT", "resp_len", "base_mt"]:
        out[col] = out[col].astype(float)

    out["allpriors"] = np.nansum(out[["dW_trans", "dW_lat"]].values, axis=1)
    out["choice_x_allpriors"] = (out.R_response * 2 - 1) * out.allpriors
    out["traj"] = np.nan
    out.traj = out.traj.astype(object)
    print("psiam done, generating trajectories + derivatives")
    if both_traj:
        out["pretraj"] = np.nan
        out.pretraj = out.pretraj.astype(object)
        out[["pretraj", "traj"]] = out.apply(
            lambda x: traj.simul_traj_single(
                x,
                return_both=True,
                silent_trials=silent_trials,
                trajMT_jerk_extension=trajMT_jerk_extension,
                jerk_lock_ms=params["jerk_lock_ms"]
            ),
            axis=1,
            result_type="expand",
        )
    else:
        out["traj"] = out.apply(
            lambda x: traj.simul_traj_single(
                x,
                silent_trials=silent_trials,
                trajMT_jerk_extension=trajMT_jerk_extension,
                jerk_lock_ms=params["jerk_lock_ms"]
            ),
            axis=1,
        )
    # getting and concatenating gradients
    tmp = out.apply(
        lambda x: plotting.gradient_np_simul(x), axis=1, result_type="expand"
    )
    tmp.columns = ["traj_d1", "traj_d2", "traj_d3"]
    out = pd.concat([out, tmp], axis=1)

    print("getting CoM etc.")
    out["time_to_thr"] = np.nan
    for i, thr in enumerate([30, 30]):
        out.loc[
            (out.R_response == i) & (out.traj.apply(len) > 0), "time_to_thr"
        ] = out.loc[
            (out.R_response == i) & (out.traj.apply(len) > 0), "traj"
        ].apply( #].swifter.apply(
            lambda x: np.argmax(np.abs(x) > thr)
        )
    out["rtbin"] = pd.cut(out.sound_len, rtbins, labels=False, include_lowest=True)
    out["choice_x_coh"] = (out.R_response * 2 - 1) * out.coh2
    out[["Hesitation", "CoM_sugg", "CoM_peakf"]] = out.apply(
        lambda x: ComPipe.chom.did_he_hesitate(
            x, simul=True, positioncol="traj", speedcol="traj_d1", height=com_height
        ),
        axis=1,
        result_type="expand",
    )  # return 1 or more peak frames?

    # not saving data, its 2.9 GB each
    # print('saving data')
    # out.to_pickle(f'{savpath}.pkl')

    # plotting section

    # get data (a) and simul (b) sets to plot. Check each plot function to dig further
    if silent_trials:
        pref_title = "silent_"
        a, b = df.loc[(df.special_trial == 2) & (df.subjid == subject)], out
    else:
        pref_title = ""
        a, b = df.loc[(df.special_trial == 0) & (df.subjid == subject)], out
    fig, ax = plt.subplots(ncols=4, nrows=4, figsize=(24, 20))
    plot0(a, b, ax[0, 0])
    # plot1(a,b, ax[1,0])
    plot2(a, b, ax[1, 0])
    pcomRT(a, b, ax[1, 1])
    _, ymax = ax[1,1].get_ylim()
    if ymax>0.3:
        ax[1,1].set_ylim(-0.05, 0.305)
    # pcomRT_proactive_only(a, b, ax[1, 2])

    # p rev matrix
    b['rev'] = 0
    b.loc[(b.prechoice!=b.R_response)&(b.reactive==0), 'rev'] = 1
    subset = b.dropna(subset=["avtrapz", "allpriors", "CoM_sugg"])
    plotting.com_heatmap(
        subset.allpriors,
        subset.avtrapz,
        subset.rev,
        flip=True,
        ax=ax[1,2],
        cmap="magma",
        fmt=".0f",
        vmin=0
    )
    ax[1,2].set_title('p(rev)')
    
    # from proactive reversals, which are detected as CoM?
    subset = b.loc[(b.rev==1)&(b.reactive==0)].dropna(subset=["avtrapz", "allpriors", "CoM_sugg"])
    plotting.com_heatmap(
        subset.allpriors,
        subset.avtrapz,
        subset.CoM_sugg,
        flip=True,
        ax=ax[1,3],
        cmap="magma",
        fmt=".0f",
        vmin=0
    )
    ax[1,3].set_title('p(com) in proactive reversals')
    plot3(a, b, ax[0, 1])  # ushape
    plot4(a, b, ax[2, 0]) # fraction of proactive responses?
    try:
        splitplot(a,b,ax[3,0])
    except Exception as e:
        print("splitplot typically crashes with silent trials\nbecause in dani's tasks they all have the same coh")
        print(e)
    
    plot_com_contour(a, b, ax[3,1])
    ax[3,1].set_title('CoM peak moment')
    ax[3,1].set_xlabel('time from movement onset (ms)')
    ax[3,1].set_ylabel('absolute prior')
    plot_median_com_traj(a, b, ax[3,2])

    plotting.tachometric(a, ax=ax[0,2], rtbins=np.arange(0,151,5))
    ax[0,2].set_title('tachometric data')
    plotting.tachometric(b, ax=ax[0,3], rtbins=np.arange(0,151,5))
    ax[0,3].set_title('tachometric simul')
    ax[0,2].sharey(ax[0,3])

    plot1112(a, b, ax[2, 2], ax[2, 3])
    for dset, label, col in [[a, 'data', 'tab:blue'], [b, 'simul', 'tab:orange']]:
        plotting.binned_curve(
            dset, 'CoM_sugg', 'origidx', np.linspace(0,600,61), xpos=np.arange(5,600,10),
            ax=ax[2,1], errorbar_kw=dict(color=col,label=label), legend=False
        )
    ax[2,1].legend()
    ax[2,1].set_ylabel('p(CoM)')
    ax[2,1].set_xlabel('trial index')
    # t update distribution
    sns.histplot(
        b.loc[b.reactive==0, 't_update'].values,
        ax=ax[3,3]
    )
    ax[3,3].set_title('effective t_update since movement onset')
    #sns.histplot(
    #    data=b[b.reactive==0], x='origidx', y='expectedMT', ax=ax[2,1]
    #)

    fig.suptitle(pref_title + subject + " " + str(params))
    # suptitle
    fname = f"{pref_title}{subject}-"
    for k, i in params.items():
        fname += f"{k}-{i}-"
    fname = fname[:-1] + ".png"
    if not return_data:
        fig.savefig(f"{savpath}{fname}")
        plt.show()
        return df, out
    else:
        warnings.warn('return data is not implemented so we just return df, and out')
        return df, out # matrices as well
    


def p_rev_pro(rt,a_e=0.5,allpriors=0, glm2Ze_scaling=0.1, confirm_thr=0.1, k_iters=5):
    """calculates probability to revert initial choice given that it was a
    proactive trial. It wil flip it for negative priors, uses 0 drift
    rt: reaction time (ms)
    a_e: semibound (scaled)
    allpriors: sum of priors in left-right space
    glm2Ze_scaling: factor to scale prior estimate
    confirm_thr: threshold to overcome in order to revert
    k: iters for infinite sum
    """
    # start with drift=0, then update if possible
    t = rt/1000
    x_0 = abs(allpriors*glm2Ze_scaling * a_e) + a_e
    rev_thr = a_e - confirm_thr*a_e 
    a = a_e * 2

    iterable = np.c_[np.arange(1,k_iters), -1*np.arange(1,k_iters)].flatten()
    iterable = np.insert(iterable, 0, 0)

    prob_list = []
    for k in iterable:
        first_ = norm(loc=2*k*a+x_0, scale=t)
        first = np.subtract(
            *first_.cdf([rev_thr, 0])
        )
        second_ = norm(loc=2*k*a-x_0, scale=t)
        second = np.subtract(
            *second_.cdf([rev_thr,0])
        )

        prob_list += [first - second]

    p_wo_drift = np.array(prob_list).sum()

    # do drift stuff here if required [oh no cannot with scipy]
    return p_wo_drift

def p_rev_pro2(rt,a_e=0.5,drift=0,allpriors=0, glm2Ze_scaling=0.1, confirm_thr=0.1,
k_iters=5, normalize=False, return_normaliz_factor=False):
    """calculates probability to revert initial choice given that it was a
    proactive trial. It wil flip it for negative priors, uses 0 drift
    rt: reaction time (ms), converted to seconds internally
    a_e: semibound (scaled)
    drift:
    allpriors: sum of priors in left-right space
    glm2Ze_scaling: factor to scale prior estimate
    confirm_thr: threshold to overcome in order to revert
    k: iters for infinite sum
    normalize: (bool= whether to normalize), (float= normalizing factor)
    """
    if return_normaliz_factor:
        assert normalize, "to return normaliz factor requires normalize=True arg"
    norm_factor = 1.0
    # add external normalization so it can be reused
    if isinstance(normalize, float):
        norm_factor = normalize # store value
        normalize=False # set the flag to false so 


    if not allpriors:
        allpriors=1e-6
    t = rt/1000
    if allpriors<0: # prechoice left we will invert all the scheme
        drift *= -1 
    x_0 = abs(allpriors*glm2Ze_scaling * a_e) + a_e # scale prior/x_0 and shift it, 
    # so that lower bound is 0, top is a and middle/threshold is a_e
    rev_thr = a_e - confirm_thr*a_e 
    a = a_e * 2

    iterable = np.c_[np.arange(1,k_iters), -1*np.arange(1,k_iters)].flatten()
    iterable = np.insert(iterable, 0, 0)

    prob_list = []
    if normalize:
        prob_normed = []
    for k in iterable:
        
        first_ = norm(loc=(2*k*a+x_0+drift*t), scale=t)
        first = np.subtract(
            *first_.cdf([rev_thr, 0])
        )
        second_ = norm(loc=(2*k*a-x_0+drift*t), scale=t)
        second = np.subtract(
            *second_.cdf([rev_thr,0])
        )
        if normalize:
            first_n= np.subtract(*first_.cdf([a, 0]))
            second_n = np.subtract(*second_.cdf([a, 0]))
            prob_normed += [ np.exp(2*k*a*drift) * (
                first_n - np.exp(-2*x_0*drift) *second_n)]

        prob_list += [ np.exp(2*k*a*drift) * (
            first - np.exp(-2*x_0*drift) *second)]

    p = np.array(prob_list).sum()
    if not normalize:
        to_return=  p/norm_factor
    else:
        to_return = p/np.array(prob_normed).sum()
    if return_normaliz_factor:
        return [to_return, np.array(prob_normed)]
    else:
        return to_return

    


def threaded_particle_(args):
    """see prob_rev function"""
    k, a, x_0, drift, t, rev_thr= args # unpack vars
    first_ = norm(loc=2*k*a+x_0+drift*t, scale=t)
    first = np.subtract(
        *first_.cdf([rev_thr, 0])
    )
    second_ = norm(loc=2*k*a-x_0+drift*t, scale=t)
    second = np.subtract(
        *second_.cdf([rev_thr,0])
    )
    return np.exp(2*k*a*drift) * (first - np.exp(2*x_0*drift) *second)

def threaded_particle_norm_(args):
    """see prob_rev function"""
    k, a, x_0, drift, t, rev_thr= args # unpack vars
    first_ = norm(loc=2*k*a+x_0+drift*t, scale=t)
    first = np.subtract(
        *first_.cdf([rev_thr, 0])
    )
    second_ = norm(loc=2*k*a-x_0+drift*t, scale=t)
    second = np.subtract(
        *second_.cdf([rev_thr,0])
    )
    first_n= np.subtract(*first_.cdf([a, 0]))
    second_n = np.subtract(*second_.cdf([a, 0]))
    
    p = np.exp(2*k*a*drift) * (
            first - np.exp(2*x_0*drift) *second)
    marginaliz = np.exp(2*k*a*drift) * (
                first_n - np.exp(2*x_0*drift) *second_n)

    return (p, marginaliz)




def prob_rev( # slower than original one
    rt,a_e=0.5,drift=0,allpriors=0, glm2Ze_scaling=0.1, confirm_thr=0.1, k_iters=5, normalize=False, nworkers=7
):
    """same than above but using threads
    calculates probability to revert initial choice given that it was a
    proactive trial. It wil flip it for negative priors, uses 0 drift
    rt: reaction time (ms)
    a_e: semibound (scaled)
    drift:
    allpriors: sum of priors in left-right space
    glm2Ze_scaling: factor to scale prior estimate
    confirm_thr: threshold to overcome in order to revert
    k: iters for infinite sum
    """
    if not allpriors:
        allpriors=1e-6
    t = rt/1000
    if allpriors<0: # prechoice left we will invert all the scheme
        drift *= -1 
    x_0 = abs(allpriors*glm2Ze_scaling * a_e) + a_e
    rev_thr = a_e - confirm_thr*a_e 
    a = a_e * 2

    iterable = np.c_[np.arange(1,k_iters), -1*np.arange(1,k_iters)].flatten()
    iterable = np.insert(iterable, 0, 0)
    
    if normalize:
        threadfun = threaded_particle_norm_
        norm_probs = []
    else:
        threadfun = threaded_particle_

    probs = []
    with ThreadPoolExecutor(max_workers=nworkers) as executor:
        jobs = [
            executor.submit(
                threadfun,
                [
                    k, a, x_0, drift, t, rev_thr
                ],
            )
            for k in iterable
        ]
        if normalize:
            for job in jobs:
                res = job.result()
                probs += [res[0]]
                norm_probs += [res[1]]
        else:
            for job in jobs:
                probs += [job.result()]

    p = np.array(probs).sum()
    if not normalize:
        return p
    else:
        return p/np.array(norm_probs).sum()