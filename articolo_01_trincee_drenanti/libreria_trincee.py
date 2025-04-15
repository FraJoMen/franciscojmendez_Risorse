# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 14:12:40 2025

@author: Francisco
"""

# libreria_trincee.py

import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import CubicSpline
from plotly.subplots import make_subplots

#%% 
class Pendio:
    def __init__(self, Z, beta_deg, gamma, gamma_w):
        """
        Inizializza il pendio con i parametri geometrici e fisici fissi.
        
        Parametri:
        - Z: array di profondità [m]
        - beta_deg: inclinazione del pendio [gradi]
        - gamma: peso specifico del terreno [kN/m³]
        - gamma_w: peso specifico dell’acqua [kN/m³]
        """
        self.Z = np.array(Z)
        self.beta = np.radians(beta_deg)
        self.gamma = gamma
        self.gamma_w = gamma_w

    def calcola_componenti(self, dw):
        """
        Calcola tau_beta, sigma_beta, u0 per una falda a profondità dw.
        """
        Z = np.maximum(self.Z, 1e-3)
        tau = self.gamma * Z * np.cos(self.beta) * np.sin(self.beta)
        sigma = self.gamma * Z * np.cos(self.beta)**2
        affondamento = np.maximum(0, Z - dw)
        u0 = self.gamma_w * affondamento * np.cos(self.beta)**2
        return tau, sigma, u0

    def calcola_F(self, c_list, phi_list, dw_list):
        """
        Calcola F(Z) per ogni combinazione di c', φ', dw.
        Ritorna un dizionario: chiavi (c, φ, dw), valori array F(Z).
        """
        risultati = {}
        for dw in dw_list:
            tau, sigma, u0 = self.calcola_componenti(dw)
            for c in c_list:
                for phi in phi_list:
                    phi_rad = np.radians(phi)
                    num = c + (sigma - u0) * np.tan(phi_rad)
                    F = num / np.maximum(tau, 1e-6)
                    risultati[(c, phi, dw)] = F
        return risultati

    def plot_F_vs_Z_dw(self, F_dict, c, phi):
        """
        Plot F(Z) al variare di dw per una coppia fissa (c, φ)
        """
        fig = go.Figure()
        for (c_val, phi_val, dw), F in F_dict.items():
            if c_val == c and phi_val == phi:
                fig.add_trace(go.Scatter(
                    x=self.Z,
                    y=F,
                    mode='lines+markers',
                    name=f'dw={dw} m'
                ))
        fig.update_layout(
            title=f"F(Z) per c'={c} kPa, φ={phi}°",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            template="plotly_white"
        )
        fig.show()

    def plot_F_vs_Z_c_phi(self, F_dict, dw):
        """
        Plot F(Z) al variare di c', φ' per una falda fissa (dw)
        """
        fig = go.Figure()
        for (c_val, phi_val, dw_val), F in F_dict.items():
            if dw_val == dw:
                fig.add_trace(go.Scatter(
                    x=self.Z,
                    y=F,
                    mode='lines+markers',
                    name=f"c'={c_val}, φ={phi_val}°"
                ))
        fig.update_layout(
            title=f"F(Z) per dw={dw} m",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            template="plotly_white"
        )
        fig.show()




#%%

class AbachiEfficienza:
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
        
    def plot_singolo(self, n_value, export_html=False, filename="grafico.html"):
        x_interp = np.linspace(0.5, 5.8, 100)
    
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
            raise ValueError(f"Valore di n non valido: {n_value}. Scegli tra {list(parametri.keys())}")
    
        fig = go.Figure()
    
        for d_value, data, x_col, y_col in parametri[n_value]:
            spline = CubicSpline(data[x_col], data[y_col])
            efficienza = spline(x_interp)
            fig.add_trace(go.Scatter(x=x_interp, y=efficienza, mode='lines', name=f"{d_value}"))
    
        fig.update_layout(
            title=f"Abaco {n_value}",
            xaxis_title="S/H0",
            yaxis_title="Efficienza",
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation='h',
                x=1,
                xanchor='right',
                y=1.1,
                yanchor='bottom'
            ),
            font=dict(family="Roboto", size=14, color="black"),
            margin=dict(t=140, b=50, l=50, r=50),
            hovermode='closest'  # ✅ basta questo per interrogare singoli punti
        )

    
        fig.update_xaxes(
            showspikes=True,
            spikecolor="grey",
            spikethickness=1,
            linecolor="black",
            linewidth=1
        )
    
        fig.update_yaxes(
            showspikes=True,
            spikecolor="grey",
            spikethickness=1,
            linecolor="black",
            linewidth=1
        )
    
        if export_html:
            fig.write_html(
                filename,
                include_plotlyjs="cdn",
                config={
                    "responsive": True,
                    "displaylogo": False,
                    "displayModeBar": True,
                    "modeBarButtonsToAdd": ["hoverClosestCartesian"]
                }
            )
            fig.show()
        else:
            fig.show()



#%%
class AbachiTemporali:
    def __init__(self):
        """
        Dati degli abachi temporali (T50 e T90) per n = 1 e n = 2.5.
        Le curve sono fornite per diversi valori di D/H0.
        """

        # === n = 1.0 ===
        self.data_T50_n1_d0p5 = {
            "S/H0": np.array([0.502437236, 0.511793276, 0.531862982, 0.583978966, 0.646998051, 0.736801301,
                              0.911745566, 1.049949747, 1.215127527, 1.407089472, 1.604566112, 1.818207969,
                              2.385053489, 2.749065536, 3.113235446, 3.386433917, 3.702550196, 4.104312654,
                              4.452538356, 4.843555576, 5.170322375, 5.513128099, 5.845283303]),
            "T": np.array([0.001377717, 0.002033229, 0.003001163, 0.004554195, 0.006546911, 0.009415737,
                           0.015959247, 0.021757212, 0.028106889, 0.036325806, 0.044875685, 0.053967905,
                           0.07211513, 0.07799788, 0.080629502, 0.080995708, 0.079961449, 0.080496096,
                           0.080233188, 0.081489205, 0.081932084, 0.083148177, 0.082854518])
        }

        self.data_T50_n1_d1p0 = {
            "S/H0": np.array([0.508015078, 0.517686845, 0.564319705, 0.627244073, 0.711690489, 0.80694529,
                              0.982142137, 1.205708342, 1.445692345, 1.648494246, 1.910284452, 2.129472578,
                              2.380927991, 2.611050792, 2.959118631, 3.237610789, 3.612652229, 3.960846359,
                              4.255503733, 4.550097963, 4.828653267, 5.042863432, 5.310705071, 5.621464517,
                              5.916121892]),
            "T": np.array([0.001293288, 0.001743537, 0.002743031, 0.004051751, 0.00582669, 0.008156263,
                           0.012859289, 0.019392988, 0.026483098, 0.033016593, 0.040463375, 0.046094689,
                           0.05067048, 0.054189814, 0.056512188, 0.057810514, 0.057128123, 0.057459022,
                           0.05722049, 0.058023377, 0.05829209, 0.05956776, 0.059832991, 0.059063717,
                           0.058818523])
        }

        self.data_T90_n1_d0p5 = {
            "S/H0": np.array([0.504121113, 0.529579224, 0.613994068, 0.70382889, 0.799178408, 0.915955258,
                              1.064841531, 1.240701405, 1.379379176, 1.560848463, 1.790529246, 2.009622654,
                              2.239556018, 2.491011431, 2.710483711, 2.956708582, 3.192314506, 3.433340408,
                              3.647550573, 3.856467051, 4.12963395, 4.429585012, 4.729536074, 4.981275642,
                              5.318756106, 5.575947224, 5.913459262]),
            "T": np.array([0.018320797, 0.026801384, 0.038892469, 0.055431204, 0.075515562, 0.102913646,
                           0.141602216, 0.184623001, 0.219756123, 0.266540349, 0.323543174, 0.378711209,
                           0.427607263, 0.470055572, 0.49360162, 0.523270121, 0.539772784, 0.546860464,
                           0.558828017, 0.560767888, 0.568434217, 0.576461402, 0.584601942, 0.59238353,
                           0.595708878, 0.587527562, 0.58550458])
        }

        self.data_T90_n1_d1p0 = {
            "S/H0": np.array([0.509477946, 0.545776013, 0.619571909, 0.688231982, 0.783549928, 0.884477288,
                              0.985436221, 1.15581297, 1.363719122, 1.582528376, 1.801495493, 2.041953086,
                              2.336136871, 2.694665794, 2.946279071, 3.321099501, 3.610336898, 3.819253376,
                              4.156702268, 4.408473408, 4.686997139, 4.938736707, 5.142264779, 5.474419983,
                              5.774434191, 5.919100249]),
            "T": np.array([0.018322425, 0.02585573, 0.036509071, 0.048384121, 0.066514151, 0.085061194,
                           0.10780027, 0.145717999, 0.195320408, 0.248019, 0.301007318, 0.358893356,
                           0.40934967, 0.459016656, 0.482266781, 0.507731134, 0.514809602, 0.516596671,
                           0.524217779, 0.526411564, 0.533655619, 0.540759064, 0.547519044, 0.54558534,
                           0.543368705, 0.539768423])
        }
        
        # === n = 2.5 ===
        self.data_T50_n2p5_d0p5 = {
            "S/H0": np.array([0.50428235, 0.56837503, 0.64333464, 0.72380691, 0.8260764, 0.9337635,
                              1.04696328, 1.1548088, 1.28445153, 1.42492951, 1.56017995, 1.73892978,
                              1.91238872, 2.12418287, 2.32517346, 2.70583266, 2.94528519, 3.1738708,
                              3.40800076, 3.68572515, 4.00701228, 4.38827344, 4.60608717, 4.85666008,
                              5.09088509, 5.47765891, 5.82641434]),
            "T": np.array([0.002021, 0.002917, 0.004248, 0.006078, 0.008698, 0.012561,
                           0.017821, 0.024613, 0.034004, 0.047833, 0.063206, 0.085841,
                           0.111486, 0.137321, 0.164647, 0.206972, 0.227101, 0.246933,
                           0.261425, 0.276947, 0.296213, 0.314284, 0.329693, 0.339904,
                           0.350346, 0.365174, 0.367073])
        }

        self.data_T50_n2p5_d1p0 = {
            "S/H0": np.array([0.50082901, 0.52696666, 0.56352768, 0.63294294, 0.71867443, 0.8371651,
                              0.9939593, 1.15623449, 1.34056035, 1.57389826, 1.79655934, 2.02479644,
                              2.26412225, 2.5415615, 2.80832392, 3.06425109, 3.32565925, 3.57075118,
                              3.87584881, 4.13183935, 4.63298518, 4.91080462, 5.16685852, 5.41743144,
                              5.69534592, 5.9514315]),
            "T": np.array([0.005346, 0.007309, 0.011426, 0.01709, 0.025799, 0.038275,
                           0.054336, 0.076458, 0.100205, 0.132603, 0.164822, 0.197701,
                           0.224811, 0.258077, 0.278279, 0.294707, 0.309356, 0.32177,
                           0.329055, 0.342315, 0.363847, 0.375268, 0.383485, 0.395362,
                           0.397, 0.402087])
        }

        self.data_T50_n2p5_d1p5 = {
            "S/H0": np.array([0.52069362, 0.787361, 1.01591492, 1.32072742, 1.60922369, 1.91951717,
                              2.26256983, 2.61110348, 2.99778226, 3.33548067, 3.62964801, 3.94561257,
                              4.21801438, 4.52311202, 4.86090547, 5.24229335, 5.48206271, 5.9070767]),
            "T": np.array([0.198573, 0.219927, 0.241276, 0.267374, 0.293591, 0.322483,
                           0.348121, 0.372489, 0.398789, 0.419088, 0.432348, 0.446172,
                           0.456051, 0.466376, 0.477167, 0.488524, 0.49027, 0.497802])
        }

        self.data_T50_n2p5_d2p0 = {
            "S/H0": np.array([0.51429386, 0.67761456, 0.92264312, 1.09138144, 1.33641, 1.55960968,
                              1.79918894, 2.02790128, 2.33280882, 2.63787477, 2.8720681, 3.23707639,
                              3.48761762, 3.81993009, 4.16859047, 4.4682388, 4.71342577, 5.0076248,
                              5.32365272, 5.56342208, 5.91756344]),
            "T": np.array([0.259512, 0.272015, 0.288026, 0.304633, 0.322564, 0.3445,
                           0.364748, 0.382693, 0.412884, 0.426016, 0.44304, 0.45754,
                           0.475939, 0.491276, 0.507231, 0.518673, 0.525235, 0.537039,
                           0.544407, 0.546352, 0.559129])
        }

        self.data_T90_n2p5_d0p5 = {
            "S/H0": np.array([0.51964286, 0.5625, 0.63214286, 0.7125, 0.825, 0.96428571,
                              1.11428571, 1.275, 1.47857143, 1.70357143, 1.90178571, 2.12678571,
                              2.3625, 2.59821429, 2.89821429, 3.16607143, 3.46071429, 3.71785714,
                              3.94821429, 4.2, 4.52142857, 4.78928571, 5.1375, 5.49642857,
                              5.72678571, 5.94107143]),
            "T": np.array([0.002868, 0.00437, 0.006056, 0.008067, 0.011096, 0.014789,
                           0.019097, 0.023516, 0.02897, 0.034857, 0.039978, 0.045502,
                           0.049779, 0.054027, 0.058678, 0.062207, 0.065968, 0.068283,
                           0.070099, 0.072555, 0.074557, 0.075965, 0.078084, 0.079636,
                           0.07983, 0.080012])
        }

        self.data_T90_n2p5_d1p0 = {
            "S/H0": np.array([0.51964286, 0.55714286, 0.59464286, 0.63214286, 0.69107143,
                              0.77142857, 0.87857143, 0.98035714, 1.15714286, 1.32321429,
                              1.47321429, 1.69821429, 1.99821429, 2.26607143, 2.55, 2.94107143,
                              3.23571429, 3.48214286, 3.7875, 4.17857143, 4.58035714, 5.025,
                              5.28214286, 5.53928571, 5.7375]),
            "T": np.array([0.002868, 0.004511, 0.005681, 0.006931, 0.008801, 0.011723,
                           0.015012, 0.018474, 0.025427, 0.030819, 0.036759, 0.044938,
                           0.055417, 0.064624, 0.071867, 0.080012, 0.085525, 0.087816,
                           0.092399, 0.096539, 0.101681, 0.105458, 0.107438, 0.10859,
                           0.108818])
        }

        self.data_T90_n2p5_d1p5 = {
            "S/H0": np.array([0.51428571, 0.71785714, 0.9, 1.06607143, 1.275, 1.47857143,
                              1.65, 1.86964286, 2.05714286, 2.28214286, 2.49107143, 2.72678571,
                              3.00535714, 3.21428571, 3.47678571, 3.72321429, 3.94285714,
                              4.20535714, 4.41964286, 4.70357143, 4.9125, 5.22321429, 5.52321429,
                              5.84464286, 5.96785714]),
            "T": np.array([0.104612, 0.115318, 0.126085, 0.134591, 0.146035, 0.155948,
                           0.163854, 0.175007, 0.181013, 0.193344, 0.201619, 0.206995,
                           0.214306, 0.219958, 0.227688, 0.228283, 0.230638, 0.236855,
                           0.239285, 0.241919, 0.244387, 0.245193, 0.247933, 0.246811,
                           0.249103])
        }

        self.data_T90_n2p5_d2p0 = {
            "S/H0": np.array([0.525, 0.69107143, 0.87321429, 0.98571429, 1.15714286,
                              1.28571429, 1.4625, 1.63928571, 1.81607143, 2.11071429,
                              2.34642857, 2.53392857, 2.775, 2.94642857, 3.13928571,
                              3.36964286, 3.66964286, 3.91071429, 4.14642857, 4.44642857,
                              4.91785714, 5.44285714, 5.7375]),
            "T": np.array([0.18978, 0.197814, 0.206222, 0.209773, 0.218665, 0.224241,
                           0.230076, 0.237946, 0.248046, 0.25685, 0.265801, 0.272749,
                           0.280038, 0.282783, 0.28562, 0.2909, 0.296497, 0.302012,
                           0.30518, 0.306151, 0.312608, 0.316856, 0.315332])
        }
        

    def add_griglia_secondaria_y(self, fig, row, col, y_min=1e-3, y_max=1e1,
                                 color="rgba(200,200,200,0.2)", width=0.5):
        import numpy as np
    
        # Esponenti log base 10 tra y_min e y_max (senza sforare!)
        e_min = int(np.floor(np.log10(y_min)))
        e_max = int(np.floor(np.log10(y_max))) 
    
        esponenti = np.arange(e_min, e_max)
    
        for e in esponenti:
            for m in range(2, 10):  # Minor ticks: 2·10^e ... 9·10^e
                y = m * np.power(10.0, e)
                if y_min <= y <= y_max:
                    fig.add_shape(
                        type="line",
                        x0=0, x1=1,
                        y0=y, y1=y,
                        line=dict(color=color, width=width),
                        xref="x domain",
                        yref="y",
                        row=row,
                        col=col
                    )

        
    def plot_abachi(self):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["T50 – n=1.0", "T90 – n=1.0", "T50 – n=2.5", "T90 – n=2.5"],
            vertical_spacing=0.15
        )
    
        x_interp = np.linspace(0.5, 6.0, 250)
    
        configurazioni = [
            ("T50", "n1", 1, 1),
            ("T90", "n1", 1, 2),
            ("T50", "n2p5", 2, 1),
            ("T90", "n2p5", 2, 2)
        ]
    
        for tipo, n_label, r, c in configurazioni:
            for d in ["0p5", "1p0", "1p5", "2p0"]:
                attr = f"data_{tipo}_{n_label}_d{d}"
                if hasattr(self, attr):
                    data = getattr(self, attr)
                    x = data["S/H0"]
                    y = data["T"]
                    spline_log = CubicSpline(x, np.log10(y), extrapolate=False)
                    y_vals = 10 ** spline_log(x_interp)
                    fig.add_trace(
                        go.Scatter(
                            x=x_interp,
                            y=y_vals,
                            mode='lines',
                            #name=f"{tipo}, n={n_label.replace('p', '.')}, d={d.replace('p', '.')}",
                            name=f"{tipo}, n={n_label[1:].replace('p', '.')}, d={d.replace('p', '.')}",
                            hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"
                        ),
                        row=r,
                        col=c
                    )
    
            # ✅ Griglia log secondaria con limiti fissi per ogni subplot
            if (r, c) == (2, 2):  # T90 – n=2.5
                y_min_plot = 1e-2
                y_max_plot = 1e+1
            else:
                y_min_plot = 1e-3
                y_max_plot = 1e+0
    
            self.add_griglia_secondaria_y(fig, r, c, y_min=y_min_plot, y_max=y_max_plot)
    
        fig.update_layout(
            title="Abachi Temporali",
            height=750,
            width=1000,
            template="plotly_white",
            showlegend=True,
            title_x=0.5,
            margin=dict(t=50, b=50, l=50, r=50)
        )
    
        tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
        ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]
    
        for r in [1, 2]:
            for c in [1, 2]:
                fig.update_xaxes(
                    title_text="S/H₀",
                    tickformat=".2f",
                    row=r,
                    col=c
                )
                fig.update_yaxes(
                    type="log",
                    title_text="T50" if c == 1 else "T90",
                    tickmode="array",
                    tickvals=tickvals,
                    ticktext=ticktext,
                    ticks="outside",
                    ticklen=8,
                    showgrid=True,
                    gridcolor="lightgray",
                    range=(
                        [-3, -1] if (r == 1 and c == 1) else
                        [-2,  0] if (r == 1 and c == 2) else
                        [-3,  0] if (r == 2 and c == 1) else
                        [-3,  0] if (r == 2 and c == 2) else None
                    ),
                    row=r,
                    col=c
                )
       
        fig.show()

    def add_griglia_subplot(self, fig, y_min=1e-3, y_max=1e1,
                                 color="rgba(200,200,200,0.2)", width=0.5):
        e_min = int(np.floor(np.log10(y_min)))
        e_max = int(np.floor(np.log10(y_max)))
        for e in np.arange(e_min, e_max):
            for m in range(2, 10):
                y = m * np.power(10.0, e)
                if y_min <= y <= y_max:
                    fig.add_shape(
                        type="line",
                        x0=0, x1=1,
                        y0=y, y1=y,
                        line=dict(color=color, width=width),
                        xref="x domain",
                        yref="y"
                    )


    def get_y_limits(self, tipo, n_label):
        if tipo == "T50" and n_label == "n1":
            return 1e-3, 1e-1  # log10 → [–3, -1]
        elif tipo == "T90" and n_label == "n1":
            return 1e-2, 1e0  # log10 → [–2, 0]
        else:  # Tutti gli altri
            return 1e-3, 1e0  # log10 → [–3, 0]
        
    def plot_singolo(self, tipo, n_label, d_list=["0p5", "1p0", "1p5", "2p0"], export_html=False, filename="grafico.html"):
        fig = go.Figure()
        x_interp = np.linspace(0.5, 6.0, 250)
    
        for d in d_list:
            attr = f"data_{tipo}_{n_label}_d{d}"
            if hasattr(self, attr):
                data = getattr(self, attr)
                x = data["S/H0"]
                y = data["T"]
                spline_log = CubicSpline(x, np.log10(y), extrapolate=False)
                y_vals = 10 ** spline_log(x_interp)
    
                fig.add_trace(go.Scatter(
                    x=x_interp,
                    y=y_vals,
                    mode="lines",
                    name=f"d={d.replace('p', '.')}",
                    hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"
                ))
    
        y_min_plot, y_max_plot = self.get_y_limits(tipo, n_label)
        self.add_griglia_subplot(fig, y_min=y_min_plot, y_max=y_max_plot)
    
        tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
        ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]
    
        fig.update_layout(
            title=f"Abaco n={n_label[1:].replace('p', '.')}",
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation='h',
                x=1,
                xanchor='right',
                y=1.1,
                yanchor='bottom'
            ),
            font=dict(family="Roboto", size=14, color="black"),
            margin=dict(t=140, b=50, l=50, r=50),
            hovermode="closest"
        )
    
        fig.update_xaxes(
            title_text="S/H₀",
            tickformat=".2f",
            showspikes=True,
            spikecolor="grey",
            spikethickness=1,
            linecolor="black",
            linewidth=1
        )
    
        fig.update_yaxes(
            type="log",
            title_text=tipo,
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            ticks="outside",
            ticklen=8,
            showgrid=True,
            gridcolor="#EAF2F6",
            range=[np.log10(y_min_plot), np.log10(y_max_plot)],
            showspikes=True,
            spikecolor="grey",
            spikethickness=1,
            linecolor="black",
            linewidth=1
        )
    
        if export_html:
            fig.write_html(
                filename,
                include_plotlyjs="cdn",
                config={
                    "responsive": True,
                    "displaylogo": False,
                    "displayModeBar": True,
                    "modeBarButtonsToAdd": ["hoverClosestCartesian"]
                }
            )
            fig.show()
        else:
            fig.show()


#%%
class AbacoPortate:
    def __init__(self):
        self.s = np.array([0,
            0.04176044, 0.17815168077733734, 0.3039688493551962, 0.4083163648054873,
            0.5228092737470083, 0.7302897152859644, 0.9372343085771442, 1.0817347193941342,
            1.2776051155646055, 1.6071160647304688, 1.946772407387561, 2.4303218661808312,
            2.9241238881148863, 3.376701318186689, 3.7470796270496196, 4.220412245918622,
            4.8994391455006605
        ])

        self.q = np.array([0,
            0.075095917, 0.38377022827135376, 0.6590847711927983, 0.8301789733147573,
            0.9846318722537777, 1.185150573357625, 1.323167934840853, 1.3776958525345622,
            1.4240188618583218, 1.4581759725645698, 1.475691780087879, 1.4769006537348623,
            1.473968492123031, 1.4625999356982105, 1.4635258814703676, 1.4730425463508734,
            1.4747401135998284
        ])

    def plot(self, export_html=False, filename="Art1_Abachi_portata.html"):
        s_interp = np.linspace(self.s.min(), self.s.max(), 300)
        q_interp = CubicSpline(self.s, self.q)(s_interp)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=s_interp,
            y=q_interp,
            mode='lines',
            name="q",
            hovertemplate="s: %{x:.2f}<br>q: %{y:.3f}<extra></extra>"
        ))

        fig.update_layout(
            title="Fattore di portata",
            xaxis_title="s",
            yaxis_title="q",
            template="plotly_white",
            font=dict(family="Roboto", size=14, color="black"),
            margin=dict(t=100, b=50, l=50, r=50),
            hovermode="closest",
            showlegend=False
        )

        fig.update_xaxes(
            showspikes=True,
            spikecolor="grey",
            spikethickness=1,
            linecolor="black",
            linewidth=1
        )

        fig.update_yaxes(
            showspikes=True,
            spikecolor="grey",
            spikethickness=1,
            linecolor="black",
            linewidth=1,
            showgrid=True,
            gridcolor="#EAF2F6"
        )

        if export_html:
            fig.write_html(
                filename,
                include_plotlyjs="cdn",
                config={
                    "responsive": True,
                    "displaylogo": False,
                    "displayModeBar": True,
                    "modeBarButtonsToAdd": ["hoverClosestCartesian"]
                }
            )
        fig.show()
