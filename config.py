# config.py

# Paramètres généraux
INITIAL_BUDGET = 35.0    # Budget de départ en Millions d'Euros (M€)
Z_MAX = 5.0              # Profondeur maximale du modèle en km

# Coûts des opérations (M€)
COST_TICKET_A = 5.0
COST_TICKET_B = 8.0
COST_TICKET_C = 12.0

COST_GRAVI_RECO = 0.5    # 0.25 stations/km2
COST_GRAVI_STD = 2.0     # 1.0 stations/km2
COST_GRAVI_HR = 5.0      # 4.0 stations/km2

COST_MT = 1.5            # Prix pour 1 transect oblique
COST_SEISMIC = 4.0       # Volume tomographique brut
COST_REPROCESSING = 2.0  # Nettoyage du bruit sismique
COST_TEMP = 1.0  # Coût d'une campagne de sondes thermiques de surface (M€)

COST_WELL = 6.0          # Forage standard

# Cibles de rentabilité (Le "Bingo")
TARGET_TEMP = 150.0      # °C
TARGET_PERM = 200.0      # mD (Oblige à trouver l'intersection des failles ou une faille majeure)