# moteur_geologique.py
import numpy as np
import os
from scipy.interpolate import griddata, interpn

def load_precomputed_model(filepath):
    if not os.path.exists(filepath): raise FileNotFoundError(f"{filepath} introuvable.")
    data = np.load(filepath)
    return data['T'], data['K'], data['Rho'], data['Res'], data['Vel'], data['Gravi'], data['MT_Inv'], data['Sismo_Brut'], data['Sismo_Propre']

def simuler_acquisition_gravi(vraie_carte, X, Y, stations_par_km2):
    surf = (X[-1] - X[0]) * (Y[-1] - Y[0])
    n_stations = int(stations_par_km2 * surf)
    XX, YY = np.meshgrid(X, Y, indexing='ij')
    pts_tous = np.column_stack((XX.ravel(), YY.ravel()))
    
    idx = np.random.choice(len(pts_tous), n_stations, replace=False)
    pts_mesures, val_mes = pts_tous[idx], vraie_carte.ravel()[idx]
    
    carte_interp = griddata(pts_mesures, val_mes, (XX, YY), method='cubic')
    mask_nan = np.isnan(carte_interp)
    if np.any(mask_nan):
        carte_interp[mask_nan] = griddata(pts_mesures, val_mes, (XX, YY), method='nearest')[mask_nan]
    return carte_interp, pts_mesures

def extraire_profil_mt_oblique(MT_Inv, X, Y, Z, xc, yc, azimuth, length, num_points=100):
    theta = np.radians(azimuth)
    s = np.linspace(-length/2, length/2, num_points)
    x_line, y_line = xc + s * np.sin(theta), yc + s * np.cos(theta)
    
    valid = (x_line >= 0) & (x_line <= X[-1]) & (y_line >= 0) & (y_line <= Y[-1])
    s_v, x_v, y_v = s[valid], x_line[valid], y_line[valid]
    
    if len(s_v) == 0: return None, None, None, None
        
    prof_2d = np.zeros((len(Z), len(s_v)))
    for k, z_val in enumerate(Z):
        pts = np.column_stack((x_v, y_v, np.full_like(x_v, z_val)))
        prof_2d[k, :] = interpn((X, Y, Z), MT_Inv, pts, method='linear', bounds_error=False, fill_value=np.nan)
        
    return prof_2d, s_v, x_v, y_v