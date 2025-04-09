# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 14:12:40 2025

@author: Francisco
"""

# libreria_trincee.py

import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline,interp1d
from plotly.subplots import make_subplots

class Pendio:
    def __init__(self, Z, beta_deg, gamma, gamma_w, Zw, c_, phi_deg, kv=None, kh=None, E=None, nu=None, H=None):
        """
        Inizializza l'oggetto Pendio con i parametri di configurazione.

        Z        : array di profondità [m]
        beta_deg : inclinazione del pendio [gradi]
        gamma    : peso specifico terreno [kN/m^3]
        gamma_w  : peso specifico acqua [kN/m^3]
        Zw       : altezza falda [m]
        c_       : coesione efficace (float o array)
        phi_deg  : angolo di attrito efficace (float o array)
        kv       : permeabilità verticale [m/s]
        kh       : permeabilità orizzontale [m/s]
        E        : modulo elastico tangente [kPa]
        nu       : coefficiente di Poisson [-]
        H        : profondità substrato impermeabile [m]
        """
        self.Z = np.array(Z)
        self.beta = np.radians(beta_deg)
        self.gamma = gamma
        self.gamma_w = gamma_w
        self.Zw = Zw
        self.c_ = np.atleast_1d(c_)
        self.phi_deg = np.atleast_1d(phi_deg)
        self.phi_rad = np.radians(self.phi_deg)

        self.kv = kv
        self.kh = kh
        self.E = E
        self.nu = nu
        self.H = H

    def calcola_componenti(self, dw_override=None):
        """Calcola tau_beta, sigma_beta, u0 (corretto per profondità della falda dw)"""
        Z_safe = np.maximum(self.Z, 1e-3)  # Evita divisioni per zero
        tau_beta = self.gamma * Z_safe * np.cos(self.beta) * np.sin(self.beta)
        sigma_beta = self.gamma * Z_safe * np.cos(self.beta)**2

        # Calcolo u0 basato su profondità della falda
        dw = dw_override if dw_override is not None else (self.Z - self.Zw)
        affondamento = np.maximum(0, self.Z - dw)
        u0 = self.gamma_w * affondamento * np.cos(self.beta)**2

        return tau_beta, sigma_beta, u0

    def calcola_F(self, c_, phi_rad, tau_beta, sigma_beta, u0):
        """Calcola F per un set di parametri dati"""
        numeratore = c_ + (sigma_beta - u0) * np.tan(phi_rad)
        denominatore = np.maximum(tau_beta, 1e-6)  # Evita divisioni per 0
        return numeratore / denominatore

    def grafico_F_c_phi(self):
        """
        Genera un grafico interattivo F(Z) per diversi valori di c_ e phi'.
        """
        tau_beta, sigma_beta, u0 = self.calcola_componenti()

        fig = go.Figure()

        for c_val in self.c_:
            for phi_val in self.phi_rad:
                F = self.calcola_F(c_val, phi_val, tau_beta, sigma_beta, u0)
                fig.add_trace(go.Scatter(
                    x=self.Z,
                    y=F,
                    mode='lines+markers',
                    name=f"c'={c_val} kPa, φ'={np.degrees(phi_val):.1f}°"
                ))

        if self.H:
            fig.add_shape(
                type='line',
                x0=self.H, x1=self.H,
                y0=0, y1=max(F)*1.1,
                line=dict(color='red', width=2, dash='dash'),
                name='Substrato'
            )

        fig.update_layout(
            title="Coefficiente di Sicurezza F(Z)",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            legend_title="Parametri geotecnici",
            template="plotly_white"
        )

        return fig

    def grafico_FvsZ_dw(self, dw_array):
        fig = go.Figure()

        for dw_val in dw_array:
            tau_beta, sigma_beta, u0 = self.calcola_componenti(dw_override=dw_val)
            for c_val in self.c_:
                for phi_val in self.phi_rad:
                    F = self.calcola_F(c_val, phi_val, tau_beta, sigma_beta, u0)
                    fig.add_trace(go.Scatter(
                        x=self.Z,
                        y=F,
                        mode='lines+markers',
                        name=f"dw={dw_val} m"
                    ))

                    if self.H is not None:
                        interp_F = interp1d(self.Z, F, kind='linear', fill_value='extrapolate')
                        F_H = float(interp_F(self.H))
                        fig.add_trace(go.Scatter(
                            x=[self.H],
                            y=[F_H],
                            mode='markers',
                            marker=dict(size=10, color='red', symbol='diamond'),
                            showlegend=False
                        ))

        shapes = []
        if self.H is not None:
            shapes.append({
                'type': 'line',
                'x0': self.H,
                'x1': self.H,
                'y0': 0,
                'y1': 2,
                'line': {
                    'color': 'red',
                    'width': 2,
                    'dash': 'dash'
                }
            })
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='lines',
                line=dict(color='red', width=2, dash='dash'),
                name='Z=H'
            ))

        fig.update_layout(
            title="Coefficiente di Sicurezza F(Z) per diversi livelli della falda (dw)",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            legend_title="Scenari di dw",
            template="plotly_white",
            shapes=shapes
        )
        return fig


class Abachi:
    def __init__(self):
        # Dati per n=1, d=0.5 e d=1
        self.data_n1_d0p5 = {
        "S/H0": np.array([0.5371369055316533, 0.7926827137150185, 1.0186601984502843, 1.1852703614255704, 1.3460088005955606, 1.4619893260449397, 1.6109522794288116, 1.722692697975537, 1.8757769257564794, 2.0495549023651165, 2.2397888509479227, 2.4010282506806657, 2.574602347990507, 2.7316476592908963, 2.938191951777303, 3.2231860858786208, 3.4131579039344038, 3.648492865972078, 3.8837695767815266, 4.106653338785647, 4.2758585939784535, 4.511062490752617, 4.742145113, 4.960761972666194, 5.191771781008002, 5.426873738132768, 5.69494589, 5.897004838347016, 5.979474014709599]),
        "efficienza": np.array([0.9976764750084757, 0.9738890034496378, 0.9430065322927335, 0.9134815477584346, 0.8797107477011155, 0.8515122213018529, 0.8114091632288735, 0.7801049531796045, 0.7400057785218402, 0.694036822, 0.6500464650630493, 0.6158442564094799, 0.5836167643928106, 0.5543183383021633, 0.5221219136072152, 0.4801839418450806, 0.45386118266303654, 0.4256180746571042, 0.40130109943368175, 0.3789355403558686, 0.3633902292496506, 0.3439809200043651, 0.3245677273438645, 0.3120136168071105, 0.2975080901247472, 0.28496951324885367, 0.2724620036946813, 0.26480002547520387, 0.26193309419262456])
        }  # Efficienza per d=0.5
        
        self.data_n1_d1 = {
        "S/H0": np.array([0.9432504884365487, 1.133892778129227, 1.3840911235613402, 1.5448924740578154, 1.729579158,
                          1.931964895479821, 2.164107690210648, 2.4496831715696725, 2.794667915572999, 3.0503395464093357,
                          3.3595067752003542, 3.650723305500896, 3.9597227707546203, 4.256831995, 4.565726608345536,
                          4.945878783854157, 5.355662194137362, 5.747557817256576, 5.990940768986113]),
        "efficienza": np.array([0.8256209872185156, 0.776330662, 0.7129621798075614, 0.6749511563451317, 0.6270686467424167,
                                0.5862699525019487, 0.5398455876442156, 0.49205814404596737, 0.4400863982217067, 0.40781847985264785,
                                0.36994725933796335, 0.3419531170814739, 0.3153891589804173, 0.2902274244452445, 0.2707305053527056,
                                0.24847387607167726, 0.22907202298360474, 0.21530702474861707, 0.2112960781778086])  
        } # Efficienza per d=1

        # Dati per n=1.5, d=0.5, 1.0, 1.5
        self.data_n1p5_d0p5 = {
            "S/H0": np.array([0.503018573, 0.737144393, 0.979967431, 1.208393095, 1.407941557, 1.598839405, 1.786858496, 1.986439223, 2.151317116, 2.40584519, 2.761563572, 3.189548453, 3.487386954, 3.790975801, 4.152369243, 4.412572378, 4.626489533, 4.938693143, 5.271112587, 5.493680356, 5.753815376, 5.930125845, 5.98213349]),
            "efficienza": np.array([0.999885643, 0.985294679, 0.9651852, 0.935433017, 0.902248791, 0.865622484, 0.826929781, 0.787542065, 0.753685771, 0.705310212, 0.645856037, 0.580851799, 0.53865822, 0.501975987, 0.462507967, 0.434118564, 0.416091254, 0.389743869, 0.365454276, 0.350869048, 0.335575901, 0.325838554, 0.326502018])
        }  # Efficienza per d=0.5
        
        self.data_n1p5_d1 = {
            "S/H0": np.array([0.506101676,0.62468642,0.795314659,0.99488463,1.289916074,1.602298934,1.984076705,2.258831369,2.582718505,2.993326875,3.383669219,3.721950144,4.074660708,4.505391702,5.054603474,5.40434207,5.684700094,5.918800819,5.976598245]),
            "efficienza": np.array([0.962663269,0.940547622,0.912202673,0.874882787,0.816837279,0.756026061,0.68621983,0.637834233,0.587356429,0.529942838,0.480121328,0.439975503,0.403268892,0.365834286,0.326273056,0.305421242,0.290807334,0.281041307,0.279634073])  
        } # Efficienza per d=1
        
        self.data_n1p5_d1p5 = {
            "S/H0": np.array([0.504284366, 0.674999935, 0.978936527, 1.270390424, 1.516053789, 1.803346787, 2.078141603, 2.294627055, 2.556908201, 2.831661718, 3.077273459, 3.410289878, 3.689188805, 4.001364596, 4.380130247, 4.704768083, 4.996103245, 5.32904739, 5.645337617, 5.832603857, 5.97408989]),
            "efficienza": np.array([0.645404728, 0.622491222, 0.585615819, 0.548746611, 0.515870351, 0.479003208, 0.445119936, 0.422183715, 0.394261987, 0.368319181, 0.345368505, 0.317411673, 0.294444478, 0.273445879, 0.249436567, 0.232402007, 0.218361642, 0.204300627, 0.19223299, 0.187177274, 0.184129391])  
        } # Efficienza per d=1.5
        
        # Dati per n=2.5, d=0.5, 1.0, 1.5, 2.0
        self.data_n2p5_d0p5 = {
            "S/H0": np.array([0.634717324, 0.82756862, 1.005062892, 1.163477793, 1.294994521, 1.438208275, 1.604753731, 1.724885187, 1.961207522, 2.193558106, 2.406486388, 2.607686468, 3.0021743, 3.210974953, 3.46603373, 3.736418356, 4.002924755, 4.230680079, 4.589578024, 4.84807857, 5.245322312, 5.503698156, 5.796666273, 5.931562418]),
            "efficienza": np.array([0.99414723, 0.980157354, 0.965233877, 0.945767098, 0.925341778, 0.900439665, 0.868384658, 0.843432664, 0.796221403, 0.752603216, 0.714345543, 0.68146501, 0.621989745, 0.591826879, 0.559062735, 0.528132538, 0.498094374, 0.476076197, 0.444436863, 0.42338554, 0.395430727, 0.377980792, 0.361506025, 0.354594221])
        }  # Efficienza per d=0.5
        
        self.data_n2p5_d1 = {
            "S/H0": np.array([0.508824646, 0.741050528, 0.93852826, 1.244533947, 1.473006305, 1.666605812, 1.914438121, 2.305265956, 2.552848862, 2.819604665, 3.198267842, 3.592163341, 3.870179715, 4.213627111, 4.468280607, 4.80384685, 5.073763844, 5.401417759, 5.744428699, 5.906285369]),
            "efficienza": np.array([0.963261094, 0.923244295, 0.886754061, 0.827087587, 0.784361433, 0.748763233, 0.702477259, 0.6375916, 0.5985084, 0.561267462, 0.514363799, 0.471995124, 0.442882247, 0.413010352, 0.391950717, 0.367464276, 0.350039281, 0.331838641, 0.314571602, 0.306817646])  
        }  # Efficienza per d=1
        
        self.data_n2p5_d1p5 = {
            "S/H0": np.array([0.498469909, 0.709923219, 0.938040676, 1.176852058, 1.424247911, 1.717933063, 1.926546664, 2.192990713, 2.428533662, 2.779768683, 3.096162029, 3.478048746, 3.906068886, 4.357140149, 4.711754589, 5.070091376, 5.520757359, 5.7634956, 5.917564644]),
            "efficienza": np.array([0.644528111, 0.617756535, 0.589724374, 0.559518312, 0.525837194, 0.48865445, 0.463893665, 0.435656195, 0.410953604, 0.378397296, 0.352068595, 0.323180181, 0.295291876, 0.268353799, 0.249311006, 0.233877914, 0.218644345, 0.208363931, 0.203294388])  
        }  # Efficienza per d=1.5
        
        self.data_n2p5_d2p0 = {
            "S/H0": np.array([0.498541737, 0.720850087, 0.937618685, 1.171051431, 1.398944424, 1.721372338, 2.032541178, 2.415861467, 2.837915126, 3.270958503, 3.626265785, 4.009137149, 4.436371418, 4.835772251, 5.240667943, 5.495765876, 5.700871366, 5.894987138]),
            "efficienza": np.array([0.482453712, 0.462188576, 0.441911469, 0.420373776, 0.398824112, 0.367105966, 0.340549875, 0.310259913, 0.281350251, 0.25505753, 0.233783207, 0.21645824, 0.197932544, 0.18323649, 0.169848906, 0.162620593, 0.159174035, 0.153110536])  
        }  # Efficienza per d=2.0

        # Dati per n=4.0, d=0.5, 1.0, 1.5, 2.0
        self.data_n2p5_d0p5 = {
            "S/H0": np.array([0.606156838,0.827167872,0.98206114,1.176123743,1.403994541,1.65445171,1.882607959,2.121914668,2.295025557,2.445575349,2.622929607,2.811799813,3.050605495,3.25858635,3.451080455,3.627988695,3.977983045,4.258584367,4.44308731,4.66963368,4.934500464,5.157076032,5.47172962,5.786036304,5.931772814]),
            "efficienza": np.array([0.994970102,0.979936309,0.966041944,0.94057132,0.900918501,0.8509466,0.806108073,0.75870286,0.72774393,0.701089375,0.673598123,0.645233831,0.612486169,0.584167305,0.559413284,0.5400247,0.501238444,0.473092206,0.454622089,0.436251913,0.416171999,0.400493627,0.378731233,0.363270914,0.354613201])
        }  # Efficienza per d=0.5
        
        self.data_n2p5_d1 = {
            "S/H0": np.array([0.499813252,0.687504055,0.846239656,1.011610898,1.210619218,1.45650722,1.664477779,1.854265746,2.06878591,2.262940281,2.472549137,2.711027159,2.958381384,3.181089449,3.477191086,3.82861842,4.064397016,4.366675428,4.673205527,4.981890148,5.312636218,5.605436166,5.862645269,5.971256856]),
            "efficienza": np.array([0.961973751,0.92802909,0.897663111,0.867312905,0.828705489,0.782393416,0.741723012,0.709867628,0.670776013,0.639973154,0.609728105,0.577467389,0.5447067,0.517619227,0.483411196,0.448813605,0.425404714,0.399548533,0.376828898,0.35515653,0.33457875,0.320163645,0.309311449,0.305401044])  
        }  # Efficienza per d=1
        
        self.data_n2p5_d1p5 = {
            "S/H0": np.array([0.504064938,0.644388514,0.85141266,1.040827799,1.270314902,1.526516649,1.796075718,1.998704782,2.239136573,2.432688681,2.686133643,2.923952044,3.206094097,3.537184317,3.936728122,4.289679036,4.598162903,4.890934172,5.190255046,5.498280046,5.806247688,5.945940322]),
            "efficienza": np.array([0.643608238,0.626225318,0.602748074,0.577665753,0.54798903,0.515249372,0.480978246,0.456969482,0.429403068,0.409541311,0.386695487,0.366417883,0.34468242,0.317852582,0.293269757,0.271181541,0.253156207,0.239262107,0.226946795,0.217257539,0.208610292,0.202689478])  
        }  # Efficienza per d=1.5
        
        self.data_n2p5_d2p0 = {
            "S/H0": np.array([0.486384232,0.64417342,0.797567526,1.079967691,1.364637095,1.604868132,1.844927093,2.1272699,2.344980621,2.562720021,2.791404108,3.059988085,3.421757843,3.694708223,4.00732906,4.324545733,4.608354762,4.940796488,5.251033369,5.598814864,5.826896688,5.968571769]),
            "efficienza": np.array([0.482554644,0.469381825,0.455677486,0.42925298,0.401791722,0.377872342,0.35707899,0.331696494,0.315018603,0.297819707,0.282731119,0.266174159,0.244627979,0.229123544,0.216318774,0.200398491,0.188567379,0.177372944,0.167688946,0.159136341,0.154988855,0.153241338])  
        }  # Efficienza per d=2.0

    
    
    def calcola_efficienza(self, S_H0, d_H0, n):
        """
        Calcola l'efficienza in base ai parametri S/H0, D/H0 e n.
        Restituisce il valore dell'efficienza corrispondente.
        """
        if n == 1 and d_H0 == 0.5:
            data = self.data_n1_d0p5
        elif n == 1 and d_H0 == 1.0:
            data = self.data_n1_d1
        # Aggiungere altre condizioni per n=1.5, 2.5, 4.0 se necessario

        # Interpolazione spline
        spline = CubicSpline(data["S/H0"], data["efficienza"])
        efficienza = spline(S_H0)  # Interpoliamo il valore di efficienza per S/H0 dato
        return efficienza

    def plot_abachi(self):
        """
        Traccia tutti i grafici degli abachi per n=1, d=0.5 e d=1.
        """
        fig = make_subplots(rows=2, 
                            cols=2, 
                            subplot_titles=["n=1.0", "n=1.5", "n=2.5", "n=4.0"],
                            vertical_spacing=0.18)  # Riduce lo spazio tra le righe
    
        # Creare un array di interpolazione più fine (100 punti tra 0.5 e 5.8)
        x_interp = np.linspace(0.5, 5.8, 100)
        
        # 1 
        # Tracciare la curva per n=1, d=0.5
        spline_n1_d0p5 = CubicSpline(self.data_n1_d0p5["S/H0"], self.data_n1_d0p5["efficienza"])
        efficienza_n1_d0p5 = spline_n1_d0p5(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n1_d0p5, mode='lines', name='n=1, d=0.5'), row=1, col=1)
        # Tracciare la curva per n=1, d=1.0
        spline_n1_d1 = CubicSpline(self.data_n1_d1["S/H0"], self.data_n1_d1["efficienza"])
        efficienza_n1_d1 = spline_n1_d1(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n1_d1, mode='lines', name='n=1, d=1.0'), row=1, col=1)
            
        #2
        # Tracciare la curva per n=1.5, d=0.5
        spline_n1p5_d0p5 = CubicSpline(self.data_n1p5_d0p5["S/H0"], self.data_n1p5_d0p5["efficienza"])
        x_interp_n1p5_d0p5 = np.linspace(0.5, 5.8, 100)  # Interpolazione tra 0.5 e 5.8
        efficienza_n1p5_d0p5 = spline_n1p5_d0p5(x_interp_n1p5_d0p5)
        fig.add_trace(go.Scatter(x=x_interp_n1p5_d0p5, y=efficienza_n1p5_d0p5, mode='lines', name='n=1.5, d=0.5'), row=1, col=2)
        
        # Tracciare la curva per n=1.5, d=1
        spline_n1p5_d1 = CubicSpline(self.data_n1p5_d1["S/H0"], self.data_n1p5_d1["efficienza"])
        x_interp_n1p5_d1 = np.linspace(0.5, 5.8, 100)  # Interpolazione tra 0.5 e 5.8
        efficienza_n1p5_d1 = spline_n1p5_d1(x_interp_n1p5_d1)
        fig.add_trace(go.Scatter(x=x_interp_n1p5_d1, y=efficienza_n1p5_d1, mode='lines', name='n=1.5, d=1'), row=1, col=2)
        
        # Tracciare la curva per n=1.5, d=1.5
        spline_n1p5_d1p5 = CubicSpline(self.data_n1p5_d1p5["S/H0"], self.data_n1p5_d1p5["efficienza"])
        x_interp_n1p5_d1p5 = np.linspace(0.5, 5.8, 100)  # Interpolazione tra 0.5 e 5.8
        efficienza_n1p5_d1p5 = spline_n1p5_d1p5(x_interp_n1p5_d1p5)
        fig.add_trace(go.Scatter(x=x_interp_n1p5_d1p5, y=efficienza_n1p5_d1p5, mode='lines', name='n=1.5, d=1.5'), row=1, col=2)

    
        # 3
        # Tracciare la curva per n=2.5, d=0.5
        spline_n2p5_d0p5 = CubicSpline(self.data_n2p5_d0p5["S/H0"], self.data_n2p5_d0p5["efficienza"])
        efficienza_n2p5_d0p5 = spline_n2p5_d0p5(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n2p5_d0p5, mode='lines', name='n=2.5, d=0.5'), row=2, col=1)

        # Tracciare la curva per n=2.5, d=1
        spline_n2p5_d1 = CubicSpline(self.data_n2p5_d1["S/H0"], self.data_n2p5_d1["efficienza"])
        efficienza_n2p5_d1 = spline_n2p5_d1(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n2p5_d1, mode='lines', name='n=2.5, d=1'), row=2, col=1)
        
        # Tracciare la curva per n=2.5, d=1.5
        spline_n2p5_d1p5 = CubicSpline(self.data_n2p5_d1p5["S/H0"], self.data_n2p5_d1p5["efficienza"])
        efficienza_n2p5_d1p5 = spline_n2p5_d1p5(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n2p5_d1p5, mode='lines', name='n=2.5, d=1.5'), row=2, col=1)
        
        # Tracciare la curva per n=2.5, d=2.0
        spline_n2p5_d2p0 = CubicSpline(self.data_n2p5_d2p0["S/H0"], self.data_n2p5_d2p0["efficienza"])
        efficienza_n2p5_d2p0 = spline_n2p5_d2p0(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n2p5_d2p0, mode='lines', name='n=2.5, d=2.0'), row=2, col=1)

    
        # 4
        # Tracciare la curva per n=4.0, d=0.5
        spline_n4_d0p5 = CubicSpline(self.data_n2p5_d0p5["S/H0"], self.data_n2p5_d0p5["efficienza"])
        efficienza_n4_d0p5 = spline_n4_d0p5(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n4_d0p5, mode='lines', name='n=4.0, d=0.5'), row=2, col=2)
        
        # Tracciare la curva per n=4.0, d=1.0
        spline_n4_d1 = CubicSpline(self.data_n2p5_d1["S/H0"], self.data_n2p5_d1["efficienza"])
        efficienza_n4_d1 = spline_n4_d1(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n4_d1, mode='lines', name='n=4.0, d=1.0'), row=2, col=2)
        
        # Tracciare la curva per n=4.0, d=1.5
        spline_n4_d1p5 = CubicSpline(self.data_n2p5_d1p5["S/H0"], self.data_n2p5_d1p5["efficienza"])
        efficienza_n4_d1p5 = spline_n4_d1p5(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n4_d1p5, mode='lines', name='n=4.0, d=1.5'), row=2, col=2)
        
        # Tracciare la curva per n=4.0, d=2.0
        spline_n4_d2p0 = CubicSpline(self.data_n2p5_d2p0["S/H0"], self.data_n2p5_d2p0["efficienza"])
        efficienza_n4_d2p0 = spline_n4_d2p0(x_interp)
        fig.add_trace(go.Scatter(x=x_interp, y=efficienza_n4_d2p0, mode='lines', name='n=4.0, d=2.0'), row=2, col=2)

    
        # Layout con dimensioni aumentate
        fig.update_layout(
            title="Abachi Efficienza Idraulica",
            height=700,  # Altezza in pixel
            width=1000,  # Larghezza in pixel
            template="plotly_white",
            showlegend=True,
            title_x=0.5  # Centra il titolo
        )
    
        fig.update_xaxes(title_text="S/H0")
        fig.update_yaxes(title_text="Efficienza")
    
        fig.update_layout(
            margin=dict(t=50, b=50, l=50, r=50),  # Aggiungi margini per evitare che i grafici tocchino il bordo
        )
        
        fig.show()



    def plot_singolo(self,n_value):
        """
        Traccia il grafico per un valore di n (1, 1.5, 2.5, 4.0)
        per i vari valori di d (0.5, 1.0, 1.5, 2.0) separatamente.
        """
        # Creare un array di interpolazione più fine (100 punti tra 0.5 e 5.8)
        x_interp = np.linspace(0.5, 5.8, 100)
    
        # Parametri di n con i rispettivi dati
        parametri = {
            "n=1.0": [
                ("d=0.5", self.data_n1_d0p5, "S/H0", "efficienza"),
                ("d=1.0", self.data_n1_d1, "S/H0", "efficienza")
            ],
            "n=1.5": [
                ("d=0.5", self.data_n1p5_d0p5, "S/H0", "efficienza"),
                ("d=1.0", self.data_n1p5_d1, "S/H0", "efficienza"),
                ("d=1.5", self.data_n1p5_d1p5, "S/H0", "efficienza")
            ],
            "n=2.5": [
                ("d=0.5", self.data_n2p5_d0p5, "S/H0", "efficienza"),
                ("d=1.0", self.data_n2p5_d1, "S/H0", "efficienza"),
                ("d=1.5", self.data_n2p5_d1p5, "S/H0", "efficienza"),
                ("d=2.0", self.data_n2p5_d2p0, "S/H0", "efficienza")
            ],
            "n=4.0": [
                ("d=0.5", self.data_n2p5_d0p5, "S/H0", "efficienza"),
                ("d=1.0", self.data_n2p5_d1, "S/H0", "efficienza"),
                ("d=1.5", self.data_n2p5_d1p5, "S/H0", "efficienza"),
                ("d=2.0", self.data_n2p5_d2p0, "S/H0", "efficienza")
            ]
        }
    
        if n_value not in parametri:
            raise ValueError(f"Valore di n non valido: {n_value}. Scegli tra 'n=1.0', 'n=1.5', 'n=2.5', 'n=4.0'.")
    
        dati = parametri[n_value]
        fig = go.Figure()
    
        # Ciclo sui dati per ogni valore di d in ciascun n
        for d_value, data, x_col, y_col in dati:
            # Interpolazione dei dati
            spline = CubicSpline(data[x_col], data[y_col])
            efficienza = spline(x_interp)
            
            # Aggiungi la traccia al grafico
            fig.add_trace(go.Scatter(x=x_interp, y=efficienza, mode='lines', name=f" {d_value}"))
    
        # Layout del grafico con font Roboto e legenda a destra
        fig.update_layout(
            title=f"Efficienza per {n_value}",
            xaxis_title="S/H0",
            yaxis_title="Efficienza",
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation='h',   # Legenda orizzontale
                x=1,               # Posizione a destra della legenda
                xanchor='right',   # Ancoraggio al bordo destro
                y=1.1,             # Posizionamento sopra il grafico
                yanchor='bottom'   # Ancoraggio in basso della legenda
            ),
            font=dict(
                family="Roboto",   # Font Roboto per tutte le scritte (compresi numeri, etichette, legenda, etc.)
                size=14,           # Dimensione del font
                color="black"      # Colore del testo
            ),
            margin=dict(
                t=100,             # Maggior spazio sopra il grafico per il titolo
                b=50,              # Margine inferiore
                l=50,              # Margine sinistro
                r=50               # Margine destro
            )
        )
    
        # Mostrare il grafico
        fig.show()




