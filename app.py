# app.py
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from config import *
from moteur_geologique import load_precomputed_model, simuler_acquisition_gravi, extraire_profil_mt_oblique

st.set_page_config(page_title="Géo-Invest (M2)", layout="wide")

# ==========================================
# 1. GESTION DES ÉTATS ET INITIALISATION
# ==========================================
if 'phase' not in st.session_state:
    st.session_state.phase = 'ENCHERES'
    st.session_state.budget = INITIAL_BUDGET
    st.session_state.expenses = []
    st.session_state.active_zone = None
    st.session_state.game_over = False

# ==========================================
# 2. PHASE D'ENCHÈRES (DATA ROOM OFFICIELLE)
# ==========================================
# if st.session_state.phase == 'ENCHERES':
#     st.markdown(
#         f"""
#         <div style='text-align: center; background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #4CAF50;'>
#             <h1>⚖️ Agence Nationale de l'Énergie</h1>
#             <h3>Appel d'Offres : Concessions Géothermiques Hautes Températures</h3>
#             <h4 style='color: #4CAF50;'>Capital d'investissement disponible : {INITIAL_BUDGET} M€</h4>
#         </div>
#         """, unsafe_allow_html=True
#     )
    
#     st.write("📁 **ACCÈS À LA DATA ROOM PRÉLIMINAIRE**")
#     st.write("Veuillez consulter les dossiers géologiques de surface avant d'engager le capital de votre société. **Une seule concession peut être acquise.**")
#     st.markdown("---")
    
#     col1, col2 = st.columns(2)
#     col3, col4 = st.columns(2)
    
#     zones = [
#         (col1, "Bloc A : Le Grand Graben", "🟢 Risque Tectonique : Faible", "🌡️ Gradient : ~40 °C/km", 
#          "Bassin sédimentaire majeur. Subsidence importante et géométrie tabulaire.", 
#          COST_TICKET_A, 'zone_A.npz', "Aquifère profond, forage standard sans surprise."),
         
#         (col2, "Bloc B : Faille Conjuguée", "🟠 Risque Tectonique : Modéré", "🌡️ Gradient : ~45 °C/km", 
#          "Zone de transition tectonique. Indices de cisaillement structural complexe.", 
#          COST_TICKET_B, 'zone_B.npz', "Faille en relais, fort potentiel de perméabilité de fracture."),
         
#         (col3, "Bloc C : Socle Aride", "🔴 Risque Tectonique : Élevé", "🌡️ Gradient : ~65 °C/km", 
#          "Affleurement granitique pur massif. Source hydrothermale signalée.", 
#          COST_TICKET_C, 'zone_C.npz', "Système volcanique ou faille de socle (coûts de forage incertains)."),
         
#         # --- LE NOUVEAU BLOC ---
#         (col4, "Bloc D : L'Écaille Orogénique", "🟣 Risque Tectonique : Extrême", "🌡️ Gradient : ~50 °C/km", 
#          "Zone de piémont (contreforts de chaîne). La géologie de surface montre un socle très ancien et fracturé.", 
#          10.0, 'zone_D.npz', "Piège structural profond sous couverture (Sub-thrust play).")
#     ]
    
#     for col, titre, risque, gradient, desc, prix, fichier, potentiel in zones:
#         with col:
#             with st.container(border=True):
#                 st.subheader(titre)
#                 st.markdown(f"**{risque}**<br>**{gradient}**", unsafe_allow_html=True)
#                 st.caption(desc)
                
#                 try:
#                     data = np.load(fichier)
#                     geol_surf = data['Rho'][:, :, 0]
#                     fig_apercu = px.imshow(geol_surf.T, origin='lower', color_continuous_scale='Earth')
#                     fig_apercu.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=180, coloraxis_showscale=False,
#                                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
#                     fig_apercu.update_xaxes(visible=False); fig_apercu.update_yaxes(visible=False)
#                     st.plotly_chart(fig_apercu, use_container_width=True)
#                 except FileNotFoundError:
#                     st.error("🛰️ Imagerie indisponible. (Générez les .npz)")
                
#                 st.markdown("---")
#                 st.write(f"💡 **Cible visée :** {potentiel}")
#                 st.markdown(f"<h3 style='text-align: center; color: #ff4b4b;'>{prix} M€</h3>", unsafe_allow_html=True)
                
#                 if st.button("Acquérir les droits d'exploration", key=f"btn_{fichier}", type="primary", use_container_width=True):
#                     st.session_state.active_zone = fichier
#                     st.session_state.budget -= prix
#                     st.session_state.expenses.append({"Action": f"Droits {titre.split(':')[0]}", "Coût (M€)": prix})
#                     st.session_state.phase = 'EXPLORATION'
#                     st.session_state.initialized = False
#                     st.rerun()

# ==========================================
# 2. PHASE D'ENCHÈRES (SAISIE DU MONTANT)
# ==========================================
if st.session_state.phase == 'ENCHERES':
    st.markdown(
        f"""
        <div style='text-align: center; background-color: #1e1e1e; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #4CAF50;'>
            <h1>⚖️ Agence Nationale de l'Énergie</h1>
            <h3>Attribution des Concessions Géothermiques</h3>
            <h4 style='color: #4CAF50;'>Capital d'investissement de votre société : {INITIAL_BUDGET} M€</h4>
        </div>
        """, unsafe_allow_html=True
    )
    
    st.write("📁 **ACCÈS À LA DATA ROOM PRÉLIMINAIRE**")
    st.write("Saisissez le montant de l'offre validée par le Ministère pour acquérir votre bloc.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    # (Colonne, Titre, Risque, Gradient, Desc, Mise à prix min, Fichier, Atout)
    zones = [
        (col1, "Bloc A : Le Grand Graben", "🟢 Risque : Faible", "🌡️ Grad. : ~40 °C/km", 
         "Bassin sédimentaire majeur. Géométrie tabulaire.", 5.0, 'zone_A.npz', "Aquifère profond standard."),
         
        (col2, "Bloc B : Faille Décentrée", "🟠 Risque : Modéré", "🌡️ Grad. : ~45 °C/km", 
         "Zone de transition tectonique complexe.", 8.0, 'zone_B.npz', "Faille en relais, forte perméabilité."),
         
        (col3, "Bloc C : Socle Aride", "🔴 Risque : Élevé", "🌡️ Grad. : ~65 °C/km", 
         "Affleurement granitique pur. Fumerolles de surface.", 12.0, 'zone_C.npz', "Système volcanique très chaud."),
         
        (col4, "Bloc D : L'Écaille Orogénique", "🟣 Risque : Extrême", "🌡️ Grad. : ~50 °C/km", 
         "Zone de piémont. Socle très ancien et fracturé.", 10.0, 'zone_D.npz', "Piège structural sous couverture.")
    ]
    
    for col, titre, risque, gradient, desc, prix_min, fichier, potentiel in zones:
        with col:
            with st.container(border=True):
                st.subheader(titre)
                st.markdown(f"**{risque}**<br>**{gradient}**", unsafe_allow_html=True)
                st.caption(desc)
                
                try:
                    data = np.load(fichier)
                    geol_surf = data['Rho'][:, :, 0]
                    fig_apercu = px.imshow(geol_surf.T, origin='lower', color_continuous_scale='Earth')
                    fig_apercu.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=150, coloraxis_showscale=False,
                                             plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    fig_apercu.update_xaxes(visible=False); fig_apercu.update_yaxes(visible=False)
                    st.plotly_chart(fig_apercu, use_container_width=True)
                except:
                    st.warning("Aperçu indisponible.")
                
                st.markdown("---")
                st.write(f"💡 *Cible : {potentiel}*")
                st.write(f"💼 **Mise à prix minimum : {prix_min} M€**")
                
                # Saisie simple de la somme finale payée
                offre = st.number_input("Montant de l'acquisition (M€) :", min_value=prix_min, max_value=st.session_state.budget, value=prix_min, step=0.5, key=f"offre_{fichier}")
                
                if st.button("Valider l'acquisition du Bloc", key=f"btn_{fichier}", type="primary", use_container_width=True):
                    st.session_state.active_zone = fichier
                    st.session_state.budget -= offre
                    st.session_state.expenses.append({"Action": f"Concession {titre.split(':')[0]}", "Coût (M€)": offre})
                    st.session_state.phase = 'EXPLORATION'
                    st.session_state.initialized = False
                    st.rerun()

                    
# ==========================================
# 3. PHASE D'EXPLORATION
# ==========================================
elif st.session_state.phase == 'EXPLORATION':
    NX, NY, NZ = 50, 50, 25
    x_coords, y_coords, z_coords = np.linspace(0, 10, NX), np.linspace(0, 10, NY), np.linspace(0, 5, NZ)
    
    if not st.session_state.get('initialized', False):
        models = load_precomputed_model(st.session_state.active_zone)
        # On charge bien les 9 matrices !
        st.session_state.T_model, st.session_state.K_model, st.session_state.Rho_model, st.session_state.Res_model, st.session_state.Vel_model, st.session_state.Gravi_map, st.session_state.MT_Inv, st.session_state.Sismo_Brut, st.session_state.Sismo_Propre = models
        
        st.session_state.mt_profiles = []
        st.session_state.wells = []
        st.session_state.gravi_acquisitions = {}
        st.session_state.has_temp = False
        st.session_state.has_seismic = False
        st.session_state.has_reprocessed = False
        st.session_state.game_over = False
        st.session_state.initialized = True

    # --- SIDEBAR (Tableau de Bord & Forage) ---
    with st.sidebar:
        st.title("📊 Géo-Invest")
        st.metric("💰 Budget Restant", f"{st.session_state.budget:.1f} M€")
        st.progress(max(0.0, st.session_state.budget / INITIAL_BUDGET))
        
        st.markdown("---")
        st.subheader("🏗️ Derrick de Forage")
        wx = st.slider("Cible X (km)", 0.0, 10.0, 5.0, step=0.1)
        wy = st.slider("Cible Y (km)", 0.0, 10.0, 5.0, step=0.1)
        wz = st.slider("Profondeur Z (km)", 1.0, 5.0, 3.0, step=0.5)
        
        # Bouton désactivé si la partie est terminée
        if st.button(f"🚀 Lancer le Forage ({COST_WELL} M€)", use_container_width=True, disabled=st.session_state.game_over):
            st.session_state.budget -= COST_WELL
            st.session_state.expenses.append({"Action": f"Forage Z={wz}km", "Coût (M€)": COST_WELL})
            idx_x, idx_y = int((wx/10)*(NX-1)), int((wy/10)*(NY-1))
            idx_z = int((wz/5)*(NZ-1))
            
            prof_T = st.session_state.T_model[idx_x, idx_y, :idx_z+1]
            prof_K = st.session_state.K_model[idx_x, idx_y, :idx_z+1]
            success = (prof_T[-1] >= TARGET_TEMP) and (prof_K[-1] >= TARGET_PERM)
            
            st.session_state.wells.append({'x': wx, 'y': wy, 'z': wz, 'profile_T': prof_T, 'profile_K': prof_K, 'success': success, 'max_T': prof_T[-1], 'max_K': prof_K[-1]})
            
            if success or st.session_state.budget <= 0: 
                st.session_state.game_over = True
            st.rerun()

        st.markdown("---")
        if st.session_state.expenses: st.dataframe(pd.DataFrame(st.session_state.expenses), hide_index=True)
        if st.button("🔄 Abandonner Concession"): 
            st.session_state.clear()
            st.rerun()

    # --- ÉCRAN DE FIN DE JEU (Bandeau persistant) ---
    if st.session_state.game_over:
        if st.session_state.wells[-1]['success']: 
            st.success("🏆 **PROJET GÉOTHERMIQUE VALIDÉ !** Réservoir commercial atteint. Vous pouvez analyser vos données ci-dessous.")
        else: 
            st.error("📉 **LIQUIDATION.** Budget épuisé ou échec. Vous pouvez examiner l'interface pour comprendre vos erreurs.")
        st.markdown("---")

    # --- ONGLETS PRINCIPAUX ---
    tab_map, tab_mt, tab_seis, tab_petro, tab_wells = st.tabs(["🗺️ Cartes", "📡 MT", "📳 Sismique", "🧪 Petro", "🏗️ Puits"])

    # 1. ONGLET CARTES DE SURFACE
    with tab_map:
        sub_geol, sub_gravi, sub_temp = st.tabs(["🗺️ Géologie (Z=0)", "🪨 Gravimétrie", "🌡️ Température de Surface"])
        
        with sub_geol:
            st.info("Carte géologique déduite des affleurements (Densité de la roche en surface).")
            fig_geol = px.imshow(st.session_state.Rho_model[:, :, 0].T, origin='lower', x=x_coords, y=y_coords, color_continuous_scale='Earth')
            for mt in st.session_state.mt_profiles: fig_geol.add_trace(go.Scatter(x=mt['x_val'], y=mt['y_val'], mode='lines', line=dict(color='orange', dash='dash')))
            if st.session_state.wells:
                wx, wy = [w['x'] for w in st.session_state.wells], [w['y'] for w in st.session_state.wells]
                fig_geol.add_trace(go.Scatter(x=wx, y=wy, mode='markers', marker=dict(size=14, color='red', symbol='x-dot')))
            fig_geol.update_xaxes(showspikes=True, spikemode="across"); fig_geol.update_yaxes(showspikes=True, spikemode="across")
            st.plotly_chart(fig_geol, use_container_width=True)

        with sub_gravi:
            offres_gravi = {"Reconnaissance": {"cout": COST_GRAVI_RECO, "densite": 0.25}, "Standard": {"cout": COST_GRAVI_STD, "densite": 1.0}, "Haute Résolution": {"cout": COST_GRAVI_HR, "densite": 4.0}}
            non_acquises = [nom for nom in offres_gravi.keys() if nom not in st.session_state.gravi_acquisitions]
            
            if non_acquises:
                with st.expander("🚁 Lancer une nouvelle campagne gravimétrique", expanded=(len(st.session_state.gravi_acquisitions) == 0)):
                    c_sel, c_btn = st.columns([2, 1])
                    with c_sel: choix_nom = st.selectbox("Densité :", non_acquises, format_func=lambda x: f"{x} - {offres_gravi[x]['cout']} M€")
                    with c_btn:
                        if st.button("Acquérir", use_container_width=True, disabled=st.session_state.game_over):
                            cout, dens = offres_gravi[choix_nom]['cout'], offres_gravi[choix_nom]['densite']
                            st.session_state.budget -= cout
                            st.session_state.expenses.append({"Action": f"Gravi {choix_nom}", "Coût (M€)": cout})
                            carte_calc, pts_calc = simuler_acquisition_gravi(st.session_state.Gravi_map, x_coords, y_coords, dens)
                            st.session_state.gravi_acquisitions[choix_nom] = (carte_calc, pts_calc)
                            st.rerun()
            
            if st.session_state.gravi_acquisitions:
                noms_acquis = list(st.session_state.gravi_acquisitions.keys())
                carte_a_afficher = noms_acquis[0]
                if len(noms_acquis) > 1: carte_a_afficher = st.radio("🔄 **Comparer les acquisitions :**", noms_acquis, horizontal=True)
                
                carte_ech, pts_ech = st.session_state.gravi_acquisitions[carte_a_afficher]
                fig_map = px.imshow(carte_ech.T, origin='lower', x=x_coords, y=y_coords, color_continuous_scale='Viridis', title=f"Bouguer ({carte_a_afficher})")
                fig_map.add_trace(go.Scatter(x=pts_ech[:,0], y=pts_ech[:,1], mode='markers', marker=dict(size=3, color='black', opacity=0.5), name='Capteurs'))
                for mt in st.session_state.mt_profiles: fig_map.add_trace(go.Scatter(x=mt['x_val'], y=mt['y_val'], mode='lines', line=dict(color='orange', dash='dash')))
                if st.session_state.wells:
                    wx, wy = [w['x'] for w in st.session_state.wells], [w['y'] for w in st.session_state.wells]
                    fig_map.add_trace(go.Scatter(x=wx, y=wy, mode='markers', marker=dict(size=14, color='red', symbol='x-dot')))
                fig_map.update_xaxes(showspikes=True, spikemode="across"); fig_map.update_yaxes(showspikes=True, spikemode="across")
                st.plotly_chart(fig_map, use_container_width=True)

        with sub_temp:
            if not st.session_state.has_temp:
                if st.button(f"🌡️ Lancer campagne thermique ({COST_TEMP} M€)", disabled=st.session_state.game_over):
                    st.session_state.budget -= COST_TEMP
                    st.session_state.expenses.append({"Action": "Thermie de surface", "Coût": COST_TEMP})
                    st.session_state.has_temp = True
                    st.rerun()
            else:
                fig_temp = px.imshow(st.session_state.T_model[:, :, 0].T, origin='lower', x=x_coords, y=y_coords, color_continuous_scale='Inferno', title="Température de surface (Z=0)")
                for mt in st.session_state.mt_profiles: fig_temp.add_trace(go.Scatter(x=mt['x_val'], y=mt['y_val'], mode='lines', line=dict(color='orange', dash='dash')))
                if st.session_state.wells:
                    wx, wy = [w['x'] for w in st.session_state.wells], [w['y'] for w in st.session_state.wells]
                    fig_temp.add_trace(go.Scatter(x=wx, y=wy, mode='markers', marker=dict(size=14, color='cyan', symbol='x-dot')))
                fig_temp.update_xaxes(showspikes=True, spikemode="across"); fig_temp.update_yaxes(showspikes=True, spikemode="across")
                st.plotly_chart(fig_temp, use_container_width=True)

    # 2. ONGLET MT
    with tab_mt:
        c1, c2, c3 = st.columns(3)
        with c1: xc = st.slider("Centre X", 0.0, 10.0, 5.0, step=0.1)
        with c2: yc = st.slider("Centre Y", 0.0, 10.0, 5.0, step=0.1)
        with c3: az = st.slider("Azimut", 0, 359, 110)
        
        if st.button(f"🛒 Tirer Profil MT ({COST_MT} M€)", disabled=st.session_state.game_over):
            st.session_state.budget -= COST_MT
            prof_2d, s_val, x_val, y_val = extraire_profil_mt_oblique(st.session_state.MT_Inv, x_coords, y_coords, z_coords, xc, yc, az, 10.0)
            if prof_2d is not None:
                st.session_state.mt_profiles.append({'xc': xc, 'yc': yc, 'azimuth': az, 'prof_2d': prof_2d, 's_val': s_val, 'x_val': x_val, 'y_val': y_val})
                st.session_state.expenses.append({"Action": f"MT Az.{az}°", "Coût": COST_MT})
            st.rerun()

        if st.session_state.mt_profiles:
            idx = st.selectbox("Voir profil :", range(len(st.session_state.mt_profiles)), format_func=lambda i: f"MT {i+1} (Azimut {st.session_state.mt_profiles[i]['azimuth']}°)")
            mt = st.session_state.mt_profiles[idx]
            fig_mt = px.imshow(np.log10(mt['prof_2d']), origin='upper', x=mt['s_val'], y=z_coords, color_continuous_scale='Turbo_r', labels={'color':'Log(Ohm.m)'}, title="Coupe Magnétotellurique")
            fig_mt.update_yaxes(title="Profondeur (km)"); fig_mt.update_xaxes(title="Distance au centre (km)", showspikes=True, spikemode="across")
            st.plotly_chart(fig_mt, use_container_width=True)

    # 3. ONGLET SISMIQUE
    with tab_seis:
        if not st.session_state.has_seismic:
            if st.button(f"🚁 Acheter Tomographie Vs ({COST_SEISMIC} M€)", disabled=st.session_state.game_over):
                st.session_state.has_seismic = True
                st.session_state.budget -= COST_SEISMIC
                st.session_state.expenses.append({"Action": "Sismique 3D", "Coût": COST_SEISMIC})
                st.rerun()
        else:
            if not st.session_state.has_reprocessed:
                if st.button(f"🔄 Retraitement Expert ({COST_REPROCESSING} M€)", disabled=st.session_state.game_over):
                    st.session_state.has_reprocessed = True
                    st.session_state.budget -= COST_REPROCESSING
                    st.session_state.expenses.append({"Action": "Reprocessing", "Coût": COST_REPROCESSING})
                    st.rerun()

            z_slice = st.slider("Profondeur Z (km)", 0.0, Z_MAX, 1.5, step=0.1)
            idx_z = int((z_slice / Z_MAX) * (NZ - 1))
            slice_data = st.session_state.Sismo_Propre[:, :, idx_z] if st.session_state.has_reprocessed else st.session_state.Sismo_Brut[:, :, idx_z]
            fig_vel = px.imshow(slice_data.T, origin='lower', x=x_coords, y=y_coords, color_continuous_scale='RdBu_r', title="Vitesse de Cisaillement (Vs)")
            fig_vel.update_xaxes(showspikes=True, spikemode="across"); fig_vel.update_yaxes(showspikes=True, spikemode="across")
            st.plotly_chart(fig_vel, use_container_width=True)

    # 4. ONGLET PETROPHYSIQUE
    with tab_petro:
        if not st.session_state.has_seismic: st.warning("Acquérez d'abord la sismique pour la croiser avec la MT.")
        else:
            z_p = st.slider("Profondeur Z (km) pour Cross-Plot", 0.0, Z_MAX, 2.5, step=0.1)
            idx_zp = int((z_p / Z_MAX) * (NZ - 1))
            vs_flat = (st.session_state.Sismo_Propre[:,:,idx_zp] if st.session_state.has_reprocessed else st.session_state.Sismo_Brut[:,:,idx_zp]).ravel()
            mt_flat = np.log10(st.session_state.MT_Inv[:,:,idx_zp]).ravel()
            
            st.caption(f"📊 *Indice : À cette profondeur, Vs varie de {vs_flat.min():.0f} à {vs_flat.max():.0f} m/s, et Log(MT) de {mt_flat.min():.1f} à {mt_flat.max():.1f}*")
            
            c_vs, c_mt = st.columns(2)
            with c_vs: max_vs = st.number_input("Seuil Max Vs", value=int(vs_flat.min() + 200), step=50)
            with c_mt: max_mt = st.number_input("Seuil Max Log(MT)", value=round(mt_flat.min() + 0.3, 1), step=0.1)
            
            mask = (vs_flat <= max_vs) & (mt_flat <= max_mt)
            
            cp1, cp2 = st.columns(2)
            with cp1:
                df = pd.DataFrame({'Vs': vs_flat, 'MT': mt_flat, 'Cible': mask.astype(str)})
                fig_sc = px.scatter(df, x='Vs', y='MT', color='Cible', color_discrete_map={'True':'red', 'False':'lightgrey'}, opacity=0.5)
                fig_sc.add_vline(x=max_vs, line_dash="dash", line_color="black")
                fig_sc.add_hline(y=max_mt, line_dash="dash", line_color="black")
                fig_sc.update_layout(height=450)
                st.plotly_chart(fig_sc, use_container_width=True)
            with cp2:
                # Ajout crucial du zmin/zmax pour éviter le bug Plotly de l'image rose !
                fig_sm = px.imshow(mask.reshape((NX,NY)).T, origin='lower', x=x_coords, y=y_coords, color_continuous_scale=['#f0f0f0', 'red'], zmin=0, zmax=1)
                fig_sm.update_layout(height=450)
                fig_sm.update_xaxes(showspikes=True, spikemode="across"); fig_sm.update_yaxes(showspikes=True, spikemode="across")
                st.plotly_chart(fig_sm, use_container_width=True)

    # 5. ONGLET PUITS
    with tab_wells:
        if st.session_state.wells:
            fig_w = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("Température (°C)", "Perméabilité (mD)"))
            for i, w in enumerate(st.session_state.wells):
                c = 'green' if w['success'] else 'red'
                z_arr = np.linspace(0, w['z'], len(w['profile_T']))
                fig_w.add_trace(go.Scatter(x=w['profile_T'], y=z_arr, line=dict(color=c, width=3), name=f"Puits {i+1}"), row=1, col=1)
                fig_w.add_trace(go.Scatter(x=w['profile_K'], y=z_arr, line=dict(color=c, width=3, dash='dot'), showlegend=False), row=1, col=2)
            
            fig_w.update_yaxes(autorange="reversed", title="Profondeur (km)", row=1, col=1)
            
            # Objectif T°
            fig_w.add_vline(x=TARGET_TEMP, line_dash="solid", line_color="orange", line_width=2, annotation_text="Objectif T°", row=1, col=1)
            fig_w.add_vrect(x0=TARGET_TEMP, x1=max(TARGET_TEMP + 100, 300), fillcolor="green", opacity=0.1, line_width=0, row=1, col=1)
            fig_w.add_vrect(x0=0, x1=TARGET_TEMP, fillcolor="red", opacity=0.05, line_width=0, row=1, col=1)
            
            # Objectif Perméabilité
            fig_w.add_vline(x=TARGET_PERM, line_dash="solid", line_color="blue", line_width=2, annotation_text="Objectif K", row=1, col=2)
            fig_w.add_vrect(x0=TARGET_PERM, x1=max(TARGET_PERM + 300, 1000), fillcolor="green", opacity=0.1, line_width=0, row=1, col=2)
            fig_w.add_vrect(x0=0, x1=TARGET_PERM, fillcolor="red", opacity=0.05, line_width=0, row=1, col=2)
            
            st.plotly_chart(fig_w, use_container_width=True)