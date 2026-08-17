from scripts.inspect_database import inspect_database

# === Target Dataset Settings ===
# database_filename = '1_result/45_fxg_3b/seed_0/1_db/db_0.db' 
# database_filename = '1_result/47_3_3boron/seed_0/1_db/db_0.db' 
database_filename = '1_result/43_fxg_0b/seed_0/1_db/db_0.db' 

    # (f'{dir_simul}/42_amorph_seed_3x3', 42),
    # (f'{dir_simul}/43_fxg_0b', 43),
    # (f'{dir_simul}/44_fxg_1b', 44),
    # (f'{dir_simul}/45_fxg_3b', 45),
    # (f'{dir_simul}/61_fxg_5b', 61),

    # (f'{dir_simul}/46_1_1boron', 46),
    # (f'{dir_simul}/47_3_3boron', 47)

    # (f'{dir_simul}/58_pt0b', 58),
    # (f'{dir_simul}/59_pt1b', 59),
    # (f'{dir_simul}/60_pt3b', 60),

# Set your desired iteration range bounds here
iteration_A = 0
iteration_B = 50

# === Database Inspection Execution ===
try:
    inspect_database(database_filename, start_iter=iteration_A, end_iter=iteration_B)
except FileNotFoundError:
    print(f"Error: The file '{database_filename}' was not found. Please check your path.")