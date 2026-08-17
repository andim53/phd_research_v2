import os

# === Directory Definitions ===
dir_simul = '1_result'            # Directory for resulted simulations
dir_out = '0_analy'               # Directory for the analysis

dir_xsf_traj = '0_xsf_traj'       # Stores entire trajectory
dir_xsf = '1_xsf'                 # Stores all structures
dir_im = '2_im'
dir_xsf_min_so_far = '3_min_so_far'

# === Directory Initialization ===
os.makedirs(f'{dir_out}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_xsf_traj}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_xsf}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_im}', exist_ok=True)
os.makedirs(f'{dir_out}/{dir_xsf_min_so_far}', exist_ok=True)

# === Database Paths Configuration ===
db_paths = [
    # (f'{dir_simul}/1_1ML_feOnMgo', 0),
    # (f'{dir_simul}/2_1ML_mgoOnFe', 1),

    # (f'{dir_simul}/0_5x5_mgoOnFe', 0),
    # (f'{dir_simul}/0_5x5_feOnMgo', 1),

    # -- Supercell --
    # (f'{dir_simul}/18_kappa2_iter100_trajNoSave_repSeedDat101', 18),
    # (f'{dir_simul}/19_kappa2_iter100_trajNoSave_repSeedDat0_5x5', 19),
    # (f'{dir_simul}/20_kappa2_iter100_trajNoSave_repSeedDat0_4x4', 20),

    # # -- Lattice --
    # (f'{dir_simul}/22_latt_0', 22),
    # (f'{dir_simul}/23_latt_025', 23),
    # (f'{dir_simul}/24_latt_50', 24),
    # (f'{dir_simul}/25_latt_075', 25),
    # (f'{dir_simul}/26_latt_100', 26),

    # # -- Concentration --
    # (f'{dir_simul}/27_fe_con0', 27),
    # (f'{dir_simul}/28_fe_con5', 28),
    # (f'{dir_simul}/29_fe_con10', 29),
    # (f'{dir_simul}/30_fe_con15', 30),
    # (f'{dir_simul}/31_fe_con20', 31),
    # # (f'{dir_simul}/19_kappa2_iter100_trajNoSave_repSeedDat0_5x5', 19),

    # (f'{dir_simul}/32_latt_0_mgo', 32),
    # (f'{dir_simul}/33_latt_25_mgo', 33),
    # (f'{dir_simul}/34_latt_50_mgo', 34),
    # (f'{dir_simul}/35_latt_75_mgo', 35),
    # (f'{dir_simul}/36_latt_100_mgo', 36),

    # # (f'{dir_simul}/38_test28', 38),    
    # # (f'{dir_simul}/41_mgoOnFe', 39),

    # # (f'{dir_simul}/42_amorph_seed_3x3', 42),
    # (f'{dir_simul}/43_fxg_0b', 43),
    # (f'{dir_simul}/44_fxg_1b', 44),
    # (f'{dir_simul}/45_fxg_3b', 45),
    # (f'{dir_simul}/61_fxg_5b', 61),

    # # (f'{dir_simul}/46_1_1boron', 46),
    # # (f'{dir_simul}/47_3_3boron', 47),

    # (f'{dir_simul}/58_pt0b', 58),
    # (f'{dir_simul}/59_pt1b', 59),
    # (f'{dir_simul}/60_pt3b', 60),

    # (f'{dir_simul}/62_w0b', 62),
    # (f'{dir_simul}/63_w1b', 63),
    # (f'{dir_simul}/64_w3b', 64),
    # (f'{dir_simul}/65_p_w10b', 65),

    # (f'{dir_simul}/66_MgOFe_20B', 66),
    (f'{dir_simul}/67_2ml',67),
    (f'{dir_simul}/68_ratt',68),
]

# === Plot Labels configuration ===
labels = [
    # 'MgO on Fe',
    # 'Fe on MgO',

    # r'0% $a_{\mathrm{MgO}}$ ($a_{\mathrm{Fe}}$)',
    # r'25% $a_{\mathrm{MgO}}$',
    # r'50% $a_{\mathrm{MgO}}$',
    # r'75% $a_{\mathrm{MgO}}$',
    # r'100% $a_{\mathrm{MgO}}$'

    # '2.0 ML Fe/MgO',  # 27_fe_con0 (Baseline)
    # '1.8 ML Fe/MgO',  # 28_fe_con5 (-5 atoms)
    # '1.6 ML Fe/MgO',  # 29_fe_con10 (-10 atoms)
    # '1.4 ML Fe/MgO',  # 30_fe_con15 (-15 atoms)
    # '1.2 ML Fe/MgO',  # 31_fe_con20 (-20 atoms)
    # '1.0 ML Fe/MgO',  # 31_fe_con20 (-20 atoms)
]