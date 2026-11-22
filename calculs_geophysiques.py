# calculs_geophysiques.py
import numpy as np
from scipy.ndimage import gaussian_filter

def calculer_gravimetrie_3d(Rho_model, X_km, Y_km, Z_km, background_density=2700.0):
    G = 6.67430e-11
    dx, dy, dz = (X_km[1]-X_km[0])*1000, (Y_km[1]-Y_km[0])*1000, (Z_km[1]-Z_km[0])*1000
    V_voxel = dx * dy * dz
    XX_m, YY_m, ZZ_m = np.meshgrid(X_km*1000, Y_km*1000, Z_km*1000, indexing='ij')
    
    masse_anomalie = (Rho_model - background_density) * V_voxel
    NX, NY = len(X_km), len(Y_km)
    gravi_map_mGal = np.zeros((NX, NY))
    
    for i in range(NX):
        for j in range(NY):
            x_obs, y_obs = X_km[i]*1000, Y_km[j]*1000
            z_obs = -400.0 # Levé héliporté
            
            dx_grid, dy_grid, dz_grid = XX_m - x_obs, YY_m - y_obs, ZZ_m - z_obs
            r = np.sqrt(dx_grid**2 + dy_grid**2 + dz_grid**2)
            gz_3d = G * masse_anomalie * dz_grid / (r**3)
            gravi_map_mGal[i, j] = np.sum(gz_3d) * 1e5
            
    # Bruit instrumental / topographique
    return gravi_map_mGal + np.random.normal(0, 0.8, gravi_map_mGal.shape)

def simuler_inversion_mt_3d(Res_model, Z_km):
    log_res = np.log10(Res_model)
    log_res_apparent = np.zeros_like(log_res)
    NZ, Z_max = len(Z_km), Z_km[-1]
    
    for k in range(NZ):
        sigma_xy = 0.5 + (Z_km[k] / Z_max) * 3.0 
        log_res_apparent[:, :, k] = gaussian_filter(log_res[:, :, k], sigma=sigma_xy)
        
    log_res_apparent = gaussian_filter(log_res_apparent, sigma=[0, 0, 1.5])
    
    # Bruit électromagnétique augmentant avec la profondeur
    bruit_mt = np.random.normal(0, 1.0, log_res_apparent.shape)
    for k in range(NZ):
        intensite = 0.02 + 0.18 * (Z_km[k] / Z_max)
        log_res_apparent[:, :, k] += bruit_mt[:, :, k] * intensite
        
    return 10**log_res_apparent

def simuler_tomographie_sismique_3d(Vel_model, bruit_expert=False):
    # Smearing vertical
    vel_apparente = gaussian_filter(Vel_model, sigma=[1.5, 1.5, 3.0])
    
    if not bruit_expert:
        # Bruit organique "brut"
        bruit_brut = np.random.normal(0, 120, vel_apparente.shape)
        vel_apparente += gaussian_filter(bruit_brut, sigma=0.5)
        
    return vel_apparente

def simuler_thermique_3d(litho_cube, ZZ_km, dict_lambda, dict_anomalie, flux_basal=90.0, T_surface=15.0):
    Lambda = np.ones_like(litho_cube, dtype=float) * 2.0
    for l_id, cond in dict_lambda.items(): Lambda[litho_cube == l_id] = cond
        
    dz_m = (ZZ_km[0, 0, 1] - ZZ_km[0, 0, 0]) * 1000 
    Res_cum = np.cumsum(dz_m / Lambda, axis=2)
    T_conductif = T_surface + (flux_basal * 1e-3) * Res_cum

    T_anomalie = np.zeros_like(T_conductif)
    for l_id, anom_max in dict_anomalie.items():
        mask = (litho_cube == l_id)
        if np.any(mask): T_anomalie[mask] = anom_max * (ZZ_km[mask] / 5.0)

    T_anomalie_diffusee = gaussian_filter(T_anomalie, sigma=2.0)
    T_final = T_conductif + T_anomalie_diffusee
    
    # Bruit de nappe de surface (uniquement sur Z=0)
    T_final[:, :, 0] += np.random.normal(0, 2.0, (T_final.shape[0], T_final.shape[1]))
    return T_final