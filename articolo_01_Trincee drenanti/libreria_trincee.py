# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 14:12:40 2025

@author: Francisco
"""

# libreria_trincee.py

import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp1d
from scipy.interpolate import BSpline
from plotly.subplots import make_subplots

#%% 
class Pendio:
    def __init__(self, Z, beta_deg, gamma, gamma_w, D=None):
        """
        Inizializza il pendio con i parametri geometrici e fisici fissi.

        Parametri:
        - Z: array di profondità [m]
        - beta_deg: inclinazione del pendio [gradi]
        - gamma: peso specifico del terreno [kN/m³]
        - gamma_w: peso specifico dell’acqua [kN/m³]
        - D: profondità del piano di scorrimento (opzionale) [m]
        """
        self.Z = np.array(Z)
        self.beta = np.radians(beta_deg)
        self.gamma = gamma
        self.gamma_w = gamma_w
        self.D = D

    def calcola_componenti(self, dw):
        Z = np.maximum(self.Z, 1e-3)
        tau = self.gamma * Z * np.cos(self.beta) * np.sin(self.beta)
        sigma = self.gamma * Z * np.cos(self.beta)**2
        affondamento = np.maximum(0, Z - dw)
        u0 = self.gamma_w * affondamento * np.cos(self.beta)**2
        return tau, sigma, u0

    def calcola_F(self, c_list, phi_list, dw_list):
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
        fig = go.Figure()
        for (c_val, phi_val, dw), F in F_dict.items():
            if c_val == c and phi_val == phi:
                fig.add_trace(go.Scatter(
                    x=self.Z,
                    y=F,
                    mode='lines+markers',
                    name=f'dw={dw} m'
                ))
                if self.D is not None:
                    interp = interp1d(self.Z, F, kind='linear', fill_value='extrapolate')
                    FD = float(interp(self.D))
                    fig.add_trace(go.Scatter(
                        x=[self.D],
                        y=[FD],
                        mode='markers',
                        marker=dict(size=10, color='red', symbol='circle'),
                        showlegend=False
                    ))
                    fig.add_shape(
                        type='line',
                        x0=self.D, x1=self.D,
                        y0=0, y1=FD,
                        line=dict(color='red', width=1, dash='dot')
                    )

        fig.update_layout(
            title=f"F(Z) per c'={c} kPa, φ={phi}°",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            template="plotly_white"
        )
        fig.show()

    def plot_F_vs_Z_c_phi(self, F_dict, dw):
        fig = go.Figure()
        for (c_val, phi_val, dw_val), F in F_dict.items():
            if dw_val == dw:
                fig.add_trace(go.Scatter(
                    x=self.Z,
                    y=F,
                    mode='lines+markers',
                    name=f"c'={c_val}, φ={phi_val}°"
                ))
                if self.D is not None:
                    interp = interp1d(self.Z, F, kind='linear', fill_value='extrapolate')
                    FD = float(interp(self.D))
                    fig.add_trace(go.Scatter(
                        x=[self.D],
                        y=[FD],
                        mode='markers',
                        marker=dict(size=10, color='red', symbol='circle'),
                        showlegend=False
                    ))
                    fig.add_shape(
                        type='line',
                        x0=self.D, x1=self.D,
                        y0=0, y1=FD,
                        line=dict(color='red', width=1, dash='dot')
                    )

        fig.update_layout(
            title=f"F(Z) per dw={dw} m",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            template="plotly_white"
        )
        fig.show()

    def plot_confronto_F_vs_Z(self, F_dict, chiavi):
        fig = go.Figure()

        for chiave in chiavi:
            c, phi, dw = chiave
            if chiave in F_dict:
                F = F_dict[chiave]
                fig.add_trace(go.Scatter(
                    x=self.Z,
                    y=F,
                    mode='lines+markers',
                    name=f"c'={c:.1f}, φ={phi:.1f}°, dw={dw:.1f} m"
                ))
                if self.D is not None:
                    interp = interp1d(self.Z, F, kind='linear', fill_value='extrapolate')
                    FD = float(interp(self.D))
                    fig.add_trace(go.Scatter(
                        x=[self.D],
                        y=[FD],
                        mode='markers',
                        marker=dict(size=10, color='red', symbol='circle'),
                        showlegend=False
                    ))
                    fig.add_shape(
                        type='line',
                        x0=self.D, x1=self.D,
                        y0=0, y1=FD,
                        line=dict(color='red', width=1, dash='dot')
                    )

        fig.update_layout(
            title="F(Z) – confronto tra scenari selezionati",
            xaxis_title="Profondità Z [m]",
            yaxis_title="F",
            template="plotly_white"
        )

        fig.show()
        
    def stima_FD(self, F_curve):
        if self.D is None:
            raise ValueError("Profondità D non definita nel pendio.")
        interp = interp1d(self.Z, F_curve, kind='linear', fill_value='extrapolate')
        return float(interp(self.D))

    def calcolo_efficienza_progetto(self, F_dict, c_proj, phi_proj, dw_init, dw_dry, F_target=1.5):
        """
        Calcola i valori F0, Fmax, ΔF, ΔFmax e l'efficienza richiesta.
    
        Parametri:
        - F_dict: dizionario delle curve F(Z)
        - c_proj: coesione di progetto
        - phi_proj: angolo di attrito di progetto
        - dw_init: falda iniziale (per F0)
        - dw_dry: falda finale (per Fmax)
        - F_target: valore obiettivo del coefficiente di sicurezza
    
        Restituisce:
        - F0: coeff. sicurezza iniziale (Z=D)
        - Fmax: coeff. sicurezza massimo ottenibile (Z=D)
        - ΔF: incremento richiesto
        - ΔFmax: incremento massimo ottenibile
        - E: efficienza richiesta
        """
        if self.D is None:
            raise ValueError("Profondità D non definita nel pendio.")
        
        chiave_init = (c_proj, phi_proj, dw_init)
        chiave_dry = (c_proj, phi_proj, dw_dry)
    
        if chiave_init not in F_dict:
            raise KeyError(f"Nessuna curva trovata per {chiave_init}")
        if chiave_dry not in F_dict:
            raise KeyError(f"Nessuna curva trovata per {chiave_dry}")
        
        F0 = self.stima_FD(F_dict[chiave_init])
        Fmax = self.stima_FD(F_dict[chiave_dry])
        deltaF = F_target - F0
        deltaFmax = Fmax - F0
        E = deltaF / deltaFmax
        return F0, Fmax, deltaF, deltaFmax, E


#%%

# -*- coding: utf-8 -*-

class AbachiEfficienza:
    def __init__(self):
        """
        Abachi di efficienza idraulica (Desideri, Miliziano, Rampello, 1997).
        Le curve E(S/H0) sono rappresentate da polinomi di regressione:
            E = polyval(coef, S/H0)
        ottenuti con fit_abachi_lineari.py sui punti digitalizzati.
        """

        # ── n = 1.0 ──────────────────────────────────────────────────────────
        self.coef_n1_d0p5 = {
            "grado": 5,
            "coef":  [ 0.00121912, -0.02250450,  0.15478454, -0.45999063,  0.36069463,  0.91336230],
            "x_min": 0.537, "x_max": 5.979
        }
        self.coef_n1_d1p0 = {
            "grado": 3,
            "coef":  [-0.00218553,  0.04721918, -0.35540193,  1.11500140],
            "x_min": 0.514, "x_max": 5.991
        }

        # ── n = 1.5 ──────────────────────────────────────────────────────────
        self.coef_n1p5_d0p5 = {
            "grado": 4,
            "coef":  [-0.00196047,  0.02895013, -0.13095397,  0.05190368,  1.00916626],
            "x_min": 0.503, "x_max": 5.982
        }
        self.coef_n1p5_d1p0 = {
            "grado": 3,
            "coef":  [ 0.00044378,  0.01254924, -0.22434232,  1.07909332],
            "x_min": 0.506, "x_max": 5.977
        }
        self.coef_n1p5_d1p5 = {
            "grado": 3,
            "coef":  [ 0.00019433,  0.00942158, -0.15336100,  0.72345807],
            "x_min": 0.504, "x_max": 5.974
        }

        # ── n = 2.5 ──────────────────────────────────────────────────────────
        self.coef_n2p5_d0p5 = {
            "grado": 4,
            "coef":  [-0.00205685,  0.02941543, -0.12866180,  0.04468809,  1.01812512],
            "x_min": 0.635, "x_max": 5.932
        }
        self.coef_n2p5_d1p0 = {
            "grado": 3,
            "coef":  [-0.00011242,  0.01817626, -0.23493448,  1.08665247],
            "x_min": 0.509, "x_max": 5.906
        }
        self.coef_n2p5_d1p5 = {
            "grado": 3,
            "coef":  [-0.00034503,  0.01460161, -0.16243576,  0.72637179],
            "x_min": 0.498, "x_max": 5.918
        }
        self.coef_n2p5_d2p0 = {
            "grado": 3,
            "coef":  [-0.00007626,  0.00904423, -0.11626783,  0.54137795],
            "x_min": 0.499, "x_max": 5.895
        }

        # ── n = 4.0 ──────────────────────────────────────────────────────────
        self.coef_n4_d0p5 = {
            "grado": 5,
            "coef":  [ 0.00084181, -0.01549314,  0.10753860, -0.32943443,  0.26444043,  0.93460520],
            "x_min": 0.606, "x_max": 5.932
        }
        self.coef_n4_d1p0 = {
            "grado": 3,
            "coef":  [-0.00029930,  0.01969709, -0.23694088,  1.08244593],
            "x_min": 0.500, "x_max": 5.971
        }
        self.coef_n4_d1p5 = {
            "grado": 3,
            "coef":  [-0.00018186,  0.01314575, -0.15937360,  0.72563318],
            "x_min": 0.504, "x_max": 5.946
        }
        self.coef_n4_d2p0 = {
            "grado": 3,
            "coef":  [ 0.00001497,  0.00833845, -0.11518106,  0.54051694],
            "x_min": 0.486, "x_max": 5.969
        }

        # ── mappa per accesso dinamico ────────────────────────────────────────
        self._mappa = {
            ("1",   "0.5"): self.coef_n1_d0p5,
            ("1",   "1.0"): self.coef_n1_d1p0,
            ("1.5", "0.5"): self.coef_n1p5_d0p5,
            ("1.5", "1.0"): self.coef_n1p5_d1p0,
            ("1.5", "1.5"): self.coef_n1p5_d1p5,
            ("2.5", "0.5"): self.coef_n2p5_d0p5,
            ("2.5", "1.0"): self.coef_n2p5_d1p0,
            ("2.5", "1.5"): self.coef_n2p5_d1p5,
            ("2.5", "2.0"): self.coef_n2p5_d2p0,
            ("4",   "0.5"): self.coef_n4_d0p5,
            ("4",   "1.0"): self.coef_n4_d1p0,
            ("4",   "1.5"): self.coef_n4_d1p5,
            ("4",   "2.0"): self.coef_n4_d2p0,
        }

    # ── utility ───────────────────────────────────────────────────────────────

    def _get_coef(self, n, d):
        """Restituisce il dizionario coef per la coppia (n, d)."""
        n_key = str(float(n)).rstrip("0").rstrip(".")
        d_key = f"{float(d):.1f}"
        key   = (n_key, d_key)
        if key not in self._mappa:
            raise ValueError(
                f"Coppia (n={n}, d={d}) non disponibile. "
                f"Disponibili: {sorted(self._mappa.keys())}"
            )
        return self._mappa[key]

    def _valuta(self, coef_dict, x):
        """Valuta il polinomio in x, restituisce NaN fuori intervallo."""
        x    = np.asarray(x, dtype=float)
        out  = np.where(
            (x >= coef_dict["x_min"]) & (x <= coef_dict["x_max"]),
            np.polyval(coef_dict["coef"], x),
            np.nan
        )
        return float(out) if out.ndim == 0 else out

    # ── metodi pubblici ───────────────────────────────────────────────────────

    def calcola_efficienza(self, S_H0, n, d):
        """
        Restituisce l'efficienza E per un dato S/H0, n e d.
        Restituisce NaN se S/H0 è fuori dall'intervallo della curva.
        """
        return self._valuta(self._get_coef(n, d), S_H0)

    def ricava_SuH0_per_efficienza(self, E_target, n_label, d_label):
        """
        Calcola S/H0 corrispondente a E_target per la coppia (n, d).
        Parametri: n_label = 'n=1.0', d_label = 'd=1.0'
        """
        from scipy.optimize import brentq

        n = n_label.split("=")[1]
        d = d_label.split("=")[1]
        c = self._get_coef(n, d)

        f = lambda x: np.polyval(c["coef"], x) - E_target
        try:
            return float(brentq(f, c["x_min"], c["x_max"]))
        except ValueError:
            raise ValueError(
                f"E_target={E_target:.4f} fuori dal range di E per n={n}, d={d} "
                f"(E_min={self._valuta(c, c['x_max']):.4f}, "
                f"E_max={self._valuta(c, c['x_min']):.4f})"
            )

    # ── plot ─────────────────────────────────────────────────────────────────

    def _curve_per_n(self, n_label):
        """Restituisce la lista di (d_label, coef_dict) per un dato n."""
        catalogo = {
            "n=1.0": [("d=0.5", self.coef_n1_d0p5),   ("d=1.0", self.coef_n1_d1p0)],
            "n=1.5": [("d=0.5", self.coef_n1p5_d0p5),  ("d=1.0", self.coef_n1p5_d1p0),
                      ("d=1.5", self.coef_n1p5_d1p5)],
            "n=2.5": [("d=0.5", self.coef_n2p5_d0p5),  ("d=1.0", self.coef_n2p5_d1p0),
                      ("d=1.5", self.coef_n2p5_d1p5),  ("d=2.0", self.coef_n2p5_d2p0)],
            "n=4.0": [("d=0.5", self.coef_n4_d0p5),    ("d=1.0", self.coef_n4_d1p0),
                      ("d=1.5", self.coef_n4_d1p5),    ("d=2.0", self.coef_n4_d2p0)],
        }
        if n_label not in catalogo:
            raise ValueError(f"n non valido: {n_label}. Scegli tra {list(catalogo)}")
        return catalogo[n_label]

    def plot_abachi(self):
        """Traccia tutti gli abachi di efficienza (4 subplot)."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["n=1.0", "n=1.5", "n=2.5", "n=4.0"],
            vertical_spacing=0.18
        )
        posizioni = [("n=1.0", 1, 1), ("n=1.5", 1, 2), ("n=2.5", 2, 1), ("n=4.0", 2, 2)]

        for n_label, r, c in posizioni:
            for d_label, coef in self._curve_per_n(n_label):
                x = np.linspace(coef["x_min"], coef["x_max"], 200)
                y = np.polyval(coef["coef"], x)
                fig.add_trace(
                    go.Scatter(x=x, y=y, mode="lines", name=f"{n_label}, {d_label}",
                               hovertemplate="S/H₀ = %{x:.2f}<br>Efficienza = %{y:.3f}"
                                             "<extra>%{fullData.name}</extra>"),
                    row=r, col=c
                )

        fig.update_layout(
            title="Abachi Efficienza Idraulica", height=700, width=1000,
            template="plotly_white", showlegend=True, title_x=0.5,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        fig.update_xaxes(title_text="S/H₀")
        fig.update_yaxes(title_text="Efficienza")
        fig.show()

    def plot_singolo(self, n_value, export_html=False, filename="grafico.html"):
        """Traccia le curve di efficienza per un singolo valore di n."""
        fig = go.Figure()

        for d_label, coef in self._curve_per_n(n_value):
            x = np.linspace(coef["x_min"], coef["x_max"], 200)
            y = np.polyval(coef["coef"], x)
            fig.add_trace(go.Scatter(
                x=x, y=y, mode="lines", name=d_label,
                hovertemplate="S/H₀ = %{x:.2f}<br>Efficienza = %{y:.3f}"
                              "<extra>%{fullData.name}</extra>"
            ))

        fig.update_layout(
            title=f"Abaco {n_value}", xaxis_title="S/H₀", yaxis_title="Efficienza",
            template="plotly_white", showlegend=True,
            legend=dict(orientation="h", x=1, xanchor="right", y=1.1, yanchor="bottom"),
            font=dict(family="Roboto", size=14, color="black"),
            margin=dict(t=140, b=50, l=50, r=50), hovermode="closest"
        )
        fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1)
        fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1)

        if export_html:
            fig.write_html(filename, include_plotlyjs="cdn",
                           config={"responsive": True, "displaylogo": False,
                                   "displayModeBar": True})
        fig.show()

    def plot_abaco_risultati(self, E_target, n_label="n=1.0"):
        """
        Traccia le curve per n_label evidenziando il punto S/H0
        corrispondente a E_target su ciascuna curva.
        """
        from scipy.optimize import brentq
        fig = go.Figure()

        for d_label, coef in self._curve_per_n(n_label):
            x = np.linspace(coef["x_min"], coef["x_max"], 200)
            y = np.polyval(coef["coef"], x)
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=d_label))

            try:
                f     = lambda xv: np.polyval(coef["coef"], xv) - E_target
                SuH0  = brentq(f, coef["x_min"], coef["x_max"])
                fig.add_trace(go.Scatter(
                    x=[SuH0], y=[E_target], mode="markers",
                    marker=dict(size=10, color="red", symbol="diamond"),
                    name=f"Target {d_label}", showlegend=False
                ))
            except ValueError:
                pass  # E_target fuori range per questa curva

        fig.update_layout(
            title=f"Abaco {n_label}", xaxis_title="S / H₀",
            yaxis_title="Efficienza idraulica media",
            template="plotly_white", hovermode="closest",
            font=dict(family="Roboto", size=14), margin=dict(t=100)
        )
        fig.show()





#%%
class AbachiTemporali:
    def __init__(self):
        """
        Abachi temporali (T50 e T90) per n = 1 e n = 2.5
        (Desideri, Miliziano, Rampello, 1997).

        Ogni curva è rappresentata da una B-spline cubica di regressione
        (continuità C2), fittata su log10(T) con fit_piecewise.py:

            T(S/H0) = 10 ** BSpline(t_full, coef, k=3)(S_H0)

        t_full è il vettore di nodi completo, ottenuto ripetendo
        x_min e x_max (k+1) volte agli estremi e inserendo i nodi interni:

            t_full = [x_min]*4 + nodi_interni + [x_max]*4
        """

        GRADO = 3  # cubica, C2 ai nodi

        # ── n = 1.0 ──────────────────────────────────────────────────────────
        self.curve_T50_n1_d0p5 = {
            "x_min": 0.487, "x_max": 5.994,
            "nodi_interni": [1.028206, 3.271635],
            "coef": [-2.81712701, -2.11462624, -1.27929248, -1.20095732, -1.25529053, -1.23731729]
        }
        self.curve_T50_n1_d1p0 = {
            "x_min": 0.480, "x_max": 5.990,
            "nodi_interni": [0.859236, 3.316708],
            "coef": [-2.78563217, -2.05122586, -1.09786364, -1.07880442, -1.10391355, -1.09504429]
        }
        self.curve_T90_n1_d0p5 = {
            "x_min": 0.498, "x_max": 5.942,
            "nodi_interni": [1.64297],
            "coef": [-1.68466706, -0.84838738, -0.04083293, -0.31716448, -0.26538603]
        }
        self.curve_T90_n1_d1p0 = {
            "x_min": 0.493, "x_max": 5.997,
            "nodi_interni": [1.368356, 3.647312],
            "coef": [-1.69197586, -0.97294802, -0.28291265, -0.24493942, -0.22101172, -0.24215316]
        }

        # ── n = 2.5 ──────────────────────────────────────────────────────────
        self.curve_T50_n2p5_d0p5 = {
            "x_min": 0.498, "x_max": 5.970,
            "nodi_interni": [1.144190, 3.144529],
            "coef": [-2.76554227, -1.89362487, -1.03867114, -0.71339992, -0.65438117, -0.65676024]
        }
        self.curve_T50_n2p5_d1p0 = {
            "x_min": 0.490, "x_max": 5.968,
            "nodi_interni": [1.398732, 3.593282],
            "coef": [-2.73837897, -1.55693130, -0.78725423, -0.49975407, -0.46274246, -0.45514185]
        }
        self.curve_T50_n2p5_d1p5 = {
            "x_min": 0.504, "x_max": 5.981,
            "nodi_interni": [3.148895],
            "coef": [-0.44771107, -0.13870722, 0.08130029, 0.08425058, 0.09092220]
        }
        self.curve_T50_n2p5_d2p0 = {
            "x_min": 0.513, "x_max": 5.984,
            "nodi_interni": [3.640929],
            "coef": [-0.05473919, 0.11828186, 0.23568900, 0.24928388, 0.24316345]
        }
        self.curve_T90_n2p5_d0p5 = {
            "x_min": 0.494, "x_max": 6.013,
            "nodi_interni": [0.713944, 2.156649, 4.477424],
            "coef": [-1.68632268, -1.47736563, -0.44213838, 0.51374517, 0.42034107, 0.60733429, 0.55098422]
        }
        self.curve_T90_n2p5_d1p0 = {
            "x_min": 0.491, "x_max": 6.021,
            "nodi_interni": [0.652741, 1.153957, 3.621675],
            "coef": [-1.26261103, -0.91833432, -0.40439888, 0.46076276, 0.49100961, 0.60759610, 0.59869541]
        }
        self.curve_T90_n2p5_d1p5 = {
            "x_min": 0.507, "x_max": 6.021,
            "nodi_interni": [2.153749, 4.188183],
            "coef": [0.32821908, 0.41651276, 0.60581081, 0.66880620, 0.70391206, 0.69807720]
        }
        self.curve_T90_n2p5_d2p0 = {
            "x_min": 0.514, "x_max": 5.992,
            "nodi_interni": [2.280312, 3.524197],
            "coef": [0.44070794, 0.51347597, 0.63117748, 0.71785380, 0.74074361, 0.74500560]
        }

        self._grado = GRADO

        # ── mappa per accesso dinamico ──────────────────────────────────────
        self._mappa = {
            ("T50", "1",   "0.5"): self.curve_T50_n1_d0p5,
            ("T50", "1",   "1.0"): self.curve_T50_n1_d1p0,
            ("T90", "1",   "0.5"): self.curve_T90_n1_d0p5,
            ("T90", "1",   "1.0"): self.curve_T90_n1_d1p0,
            ("T50", "2.5", "0.5"): self.curve_T50_n2p5_d0p5,
            ("T50", "2.5", "1.0"): self.curve_T50_n2p5_d1p0,
            ("T50", "2.5", "1.5"): self.curve_T50_n2p5_d1p5,
            ("T50", "2.5", "2.0"): self.curve_T50_n2p5_d2p0,
            ("T90", "2.5", "0.5"): self.curve_T90_n2p5_d0p5,
            ("T90", "2.5", "1.0"): self.curve_T90_n2p5_d1p0,
            ("T90", "2.5", "1.5"): self.curve_T90_n2p5_d1p5,
            ("T90", "2.5", "2.0"): self.curve_T90_n2p5_d2p0,
        }

    # ── utility ───────────────────────────────────────────────────────────────

    def _get_curva(self, tipo, n, d):
        n_key = str(float(n)).rstrip("0").rstrip(".") if float(n) != 2.5 else "2.5"
        if float(n) == 1:
            n_key = "1"
        d_key = f"{float(d):.1f}"
        key = (tipo, n_key, d_key)
        if key not in self._mappa:
            raise ValueError(
                f"Curva non disponibile: tipo={tipo}, n={n}, d={d}. "
                f"Disponibili: {sorted(self._mappa.keys())}"
            )
        return self._mappa[key]

    def _bspline(self, curva):
        """Ricostruisce la BSpline cubica dai nodi interni + coefficienti."""
        k = self._grado
        t_full = ([curva["x_min"]] * (k + 1)
                  + list(curva["nodi_interni"])
                  + [curva["x_max"]] * (k + 1))
        return BSpline(t_full, curva["coef"], k)

    def _valuta_T(self, curva, x):
        """Valuta T(S/H0), NaN fuori intervallo."""
        x   = np.asarray(x, dtype=float)
        spl = self._bspline(curva)
        out = np.where(
            (x >= curva["x_min"]) & (x <= curva["x_max"]),
            10 ** spl(x),
            np.nan
        )
        return float(out) if out.ndim == 0 else out

    def _curve_disponibili(self, tipo, n):
        """Lista (d_label, curva) disponibili per tipo e n dati."""
        n_key = "1" if float(n) == 1 else "2.5"
        return [
            (d, c) for (t, nn, d), c in self._mappa.items()
            if t == tipo and nn == n_key
        ]

    # ── metodi pubblici ───────────────────────────────────────────────────────

    def ricava_T_da_SuH0(self, SuH0, tipo="T50", n_label="n=1.0", d_label="d=1.0"):
        """
        Calcola T (T50 o T90) per un dato S/H0, con (n, d) date come
        'n=1.0', 'd=1.0'. Solleva ValueError se S/H0 è fuori intervallo.
        """
        n = self._normalizza_n(n_label)
        d = d_label.split("=")[1] if "=" in d_label else d_label.replace("d", "", 1).replace("p", ".")
        curva = self._get_curva(tipo, n, d)

        if SuH0 < curva["x_min"] or SuH0 > curva["x_max"]:
            raise ValueError(
                f"S/H0={SuH0:.3f} fuori dall'intervallo "
                f"({curva['x_min']:.3f}, {curva['x_max']:.3f}) per {tipo} n={n} d={d}"
            )
        return self._valuta_T(curva, SuH0)

    # ── plot ─────────────────────────────────────────────────────────────────

    def add_griglia_secondaria_y(self, fig, row, col, y_min=1e-3, y_max=1e1,
                                 color="rgba(200,200,200,0.2)", width=0.5):
        e_min = int(np.floor(np.log10(y_min)))
        e_max = int(np.floor(np.log10(y_max)))
        for e in np.arange(e_min, e_max):
            for m in range(2, 10):
                y = m * np.power(10.0, e)
                if y_min <= y <= y_max:
                    fig.add_shape(type="line", x0=0, x1=1, y0=y, y1=y,
                                 line=dict(color=color, width=width),
                                 xref="x domain", yref="y", row=row, col=col)

    def add_griglia_subplot(self, fig, y_min=1e-3, y_max=1e1,
                            color="rgba(200,200,200,0.2)", width=0.5):
        e_min = int(np.floor(np.log10(y_min)))
        e_max = int(np.floor(np.log10(y_max)))
        for e in np.arange(e_min, e_max):
            for m in range(2, 10):
                y = m * np.power(10.0, e)
                if y_min <= y <= y_max:
                    fig.add_shape(type="line", x0=0, x1=1, y0=y, y1=y,
                                 line=dict(color=color, width=width),
                                 xref="x domain", yref="y")

    def get_y_limits(self, tipo, n_label):
        # Limiti aggiornati sui dati redigitalizzati (T90 arriva fino a ~5.6)
        if tipo == "T50" and n_label == "n1":
            return 1e-3, 1e0
        elif tipo == "T90" and n_label == "n1":
            return 1e-2, 1e0
        elif tipo == "T50":  # n=2.5: alcune curve (d=1.5, d=2.0) superano 1
            return 1e-3, 1e1
        else:  # T90 n=2.5: arriva fino a ~5.6
            return 1e-2, 1e1

    def plot_abachi(self):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["T50 – n=1.0", "T90 – n=1.0", "T50 – n=2.5", "T90 – n=2.5"],
            vertical_spacing=0.15
        )
        configurazioni = [("T50", "1", 1, 1), ("T90", "1", 1, 2),
                          ("T50", "2.5", 2, 1), ("T90", "2.5", 2, 2)]

        for tipo, n, r, c in configurazioni:
            for d_key, curva in self._curve_disponibili(tipo, n):
                x = np.linspace(curva["x_min"], curva["x_max"], 250)
                y = self._valuta_T(curva, x)
                fig.add_trace(
                    go.Scatter(x=x, y=y, mode='lines',
                              name=f"{tipo}, n={n}, d={d_key}",
                              hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"),
                    row=r, col=c
                )
            # Limiti aggiornati sui dati redigitalizzati
            if (r, c) == (1, 1):      # T50 n=1
                y_min_plot, y_max_plot = 1e-3, 1e0
            elif (r, c) == (1, 2):    # T90 n=1
                y_min_plot, y_max_plot = 1e-2, 1e0
            elif (r, c) == (2, 1):    # T50 n=2.5
                y_min_plot, y_max_plot = 1e-3, 1e1
            else:                     # T90 n=2.5
                y_min_plot, y_max_plot = 1e-2, 1e1
            self.add_griglia_secondaria_y(fig, r, c, y_min=y_min_plot, y_max=y_max_plot)

        fig.update_layout(title="Abachi Temporali", height=750, width=1000,
                          template="plotly_white", showlegend=True, title_x=0.5,
                          margin=dict(t=50, b=50, l=50, r=50))

        tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
        ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]
        for r in [1, 2]:
            for c in [1, 2]:
                fig.update_xaxes(title_text="S/H₀", tickformat=".2f", row=r, col=c)
                # Range log10 coerenti con get_y_limits (dati redigitalizzati)
                if (r, c) == (1, 1):      # T50 n=1
                    rng = [-3, 0]
                elif (r, c) == (1, 2):    # T90 n=1
                    rng = [-2, 0]
                elif (r, c) == (2, 1):    # T50 n=2.5
                    rng = [-3, 1]
                else:                     # T90 n=2.5
                    rng = [-2, 1]
                fig.update_yaxes(
                    type="log", title_text="T50" if c == 1 else "T90",
                    tickmode="array", tickvals=tickvals, ticktext=ticktext,
                    ticks="outside", ticklen=8, showgrid=True, gridcolor="lightgray",
                    range=rng,
                    row=r, col=c
                )
        fig.show()

    def _normalizza_n(self, n_label):
        """
        Accetta sia il vecchio formato ('n1', 'n2p5') sia il nuovo ('n=1.0', 'n=2.5')
        e restituisce sempre il valore numerico come stringa ('1' o '2.5').
        """
        s = n_label.strip()
        if "=" in s:
            s = s.split("=")[1]
        else:
            s = s.replace("n", "", 1)  # 'n1' -> '1', 'n2p5' -> '2p5'
        s = s.replace("p", ".")
        if s.endswith(".0"):
            s = s[:-2]
        return "1" if float(s) == 1 else "2.5"

    def plot_singolo(self, tipo, n_label, d_list=None, export_html=False, filename="grafico.html"):
        fig = go.Figure()
        n = self._normalizza_n(n_label)
        curve = self._curve_disponibili(tipo, n)
        if d_list is not None:
            curve = [(d, c) for d, c in curve if d in d_list]

        for d_key, curva in curve:
            x = np.linspace(curva["x_min"], curva["x_max"], 250)
            y = self._valuta_T(curva, x)
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"d={d_key}",
                                     hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"))

        y_min_plot, y_max_plot = self.get_y_limits(tipo, f"n{n.replace('.','p')}" if n != "1" else "n1")
        self.add_griglia_subplot(fig, y_min=y_min_plot, y_max=y_max_plot)
        tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
        ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]

        fig.update_layout(
            title=f"Abaco n={n}", template="plotly_white", showlegend=True,
            legend=dict(orientation='h', x=1, xanchor='right', y=1.1, yanchor='bottom'),
            font=dict(family="Roboto", size=14, color="black"),
            margin=dict(t=140, b=50, l=50, r=50), hovermode="closest"
        )
        fig.update_xaxes(title_text="S/H₀", tickformat=".2f", showspikes=True,
                         spikecolor="grey", spikethickness=1, linecolor="black", linewidth=1)
        fig.update_yaxes(type="log", title_text=tipo, tickmode="array", tickvals=tickvals,
                         ticktext=ticktext, ticks="outside", ticklen=8, showgrid=True,
                         gridcolor="#EAF2F6", range=[np.log10(y_min_plot), np.log10(y_max_plot)],
                         showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1)

        if export_html:
            fig.write_html(filename, include_plotlyjs="cdn",
                           config={"responsive": True, "displaylogo": False,
                                   "displayModeBar": True, "modeBarButtonsToAdd": ["hoverClosestCartesian"]})
        fig.show()

    def plot_abaco_risultati(self, SuH0, n_label='n=1.0', tipo='T50'):
        n = self._normalizza_n(n_label)
        fig = go.Figure()

        for d_key, curva in self._curve_disponibili(tipo, n):
            x = np.linspace(curva["x_min"], curva["x_max"], 250)
            y = self._valuta_T(curva, x)
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=f"d={d_key}",
                                     hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"))
            if curva["x_min"] <= SuH0 <= curva["x_max"]:
                T_val = self._valuta_T(curva, SuH0)
                fig.add_trace(go.Scatter(x=[SuH0], y=[T_val], mode="markers",
                                         marker=dict(size=10, color="red", symbol="diamond"),
                                         name=f"Punto d={d_key}"))

        y_min_plot, y_max_plot = self.get_y_limits(tipo, f"n{n.replace('.','p')}" if n != "1" else "n1")
        self.add_griglia_subplot(fig, y_min=y_min_plot, y_max=y_max_plot)
        tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
        ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]

        fig.update_layout(title=f"Abachi {tipo} – {n_label}", template="plotly_white",
                          showlegend=True, font=dict(family="Roboto", size=14),
                          margin=dict(t=100), hovermode="closest")
        fig.update_xaxes(title_text="S / H₀", tickformat=".2f", showspikes=True,
                         spikecolor="grey", spikethickness=1, linecolor="black", linewidth=1)
        fig.update_yaxes(type="log", title_text=tipo, tickmode="array", tickvals=tickvals,
                         ticktext=ticktext, ticks="outside", ticklen=8, showgrid=True,
                         gridcolor="#EAF2F6", range=[np.log10(y_min_plot), np.log10(y_max_plot)],
                         showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1)
        fig.show()


#%%
class AbacoPortate:
    def __init__(self):
        """
        Abaco del fattore di portata adimensionale q(s).
        Fit polinomiale diretto (grado 6) ottenuto con fit_abachi_lineari.py.
        """
        self.grado  = 6
        self.coef   = [-0.00052235, 0.01441760, -0.14951922, 0.76637241,
                       -2.07136723, 2.81031175, -0.02558556]
        self.s_min  = 0.0
        self.s_max  = 4.899

    def _valuta_q(self, s):
        s   = np.asarray(s, dtype=float)
        out = np.where(
            (s >= self.s_min) & (s <= self.s_max),
            np.polyval(self.coef, s),
            np.nan
        )
        return float(out) if out.ndim == 0 else out

    def plot(self, export_html=False, filename="Art1_Abachi_portata.html"):
        s_interp = np.linspace(self.s_min, self.s_max, 300)
        q_interp = self._valuta_q(s_interp)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s_interp, y=q_interp, mode='lines', name="q",
                                 hovertemplate="s: %{x:.2f}<br>q: %{y:.3f}<extra></extra>"))
        fig.update_layout(title="Fattore di portata", xaxis_title="s", yaxis_title="q",
                          template="plotly_white", font=dict(family="Roboto", size=14, color="black"),
                          margin=dict(t=100, b=50, l=50, r=50), hovermode="closest", showlegend=False)
        fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1)
        fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1, showgrid=True, gridcolor="#EAF2F6")

        if export_html:
            fig.write_html(filename, include_plotlyjs="cdn",
                           config={"responsive": True, "displaylogo": False,
                                   "displayModeBar": True, "modeBarButtonsToAdd": ["hoverClosestCartesian"]})
        fig.show()

    def calcola_portata(self, S, kv, kh, D):
        """
        Calcola la portata drenata per metro lineare di trincea [l/h].

        Parametri:
        - S: interasse delle trincee [m]
        - kv: permeabilità verticale [m/s]
        - kh: permeabilità orizzontale [m/s]
        - D: profondità del piano di scorrimento [m]
        """
        s_adim = (S * np.sqrt(kv / kh)) / (2 * D)
        q_adim = self._valuta_q(s_adim)
        if np.isnan(q_adim):
            raise ValueError(
                f"s={s_adim:.3f} fuori dall'intervallo ({self.s_min}, {self.s_max})"
            )

        Q_lh = q_adim * kv * D * 1000 * 3600  # m³/s → l/h

        s_plot   = np.linspace(self.s_min, self.s_max, 300)
        q_plot   = self._valuta_q(s_plot)
        S_plot   = 2 * D * s_plot / np.sqrt(kv / kh)
        Q_plot_lh = q_plot * kv * D * 1000 * 3600

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=S_plot, y=Q_plot_lh, mode="lines", name="Q(S)",
                                 hovertemplate="S = %{x:.2f} m<br>Q = %{y:.2e} l/h<extra></extra>"))
        fig.add_trace(go.Scatter(x=[S], y=[Q_lh], mode="markers",
                                 marker=dict(size=10, color="red", symbol="diamond"),
                                 name="Punto di progetto",
                                 hovertemplate="S = %{x:.2f} m<br>Q = %{y:.2e} l/h<extra></extra>"))
        fig.update_layout(title="Portata drenata per metro lineare", xaxis_title="Interasse S [m]",
                          yaxis_title="Q [l/h]", template="plotly_white", showlegend=False,
                          font=dict(family="Roboto", size=14), margin=dict(t=100, b=50, l=50, r=50),
                          hovermode="closest")
        fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=1,
                         linecolor="black", linewidth=1)
        fig.update_yaxes(tickformat=".1e", showspikes=True, spikecolor="grey",
                         spikethickness=1, linecolor="black", linewidth=1,
                         showgrid=True, gridcolor="#EAF2F6")
        fig.show()
        return Q_lh


def calcola_tempo_reale(T_adim, H0, kv, gamma_w, E, nu):
    """
    Calcola il tempo reale corrispondente a un tempo adimensionale T,
    restituendo il risultato con unità di misura intelligenti.

    Parametri:
    - T_adim: tempo adimensionale (T)
    - H0: profondità del dreno [m]
    - kv: permeabilità verticale [m/s]
    - gamma_w: peso specifico dell'acqua [kN/m³]
    - E: modulo di Young [kPa]
    - nu: coefficiente di Poisson

    Ritorna:
    - Stringa del tipo "5.6 mesi", "12.3 giorni" o "4.2 ore"
    """
    coeff = (2 * (1 + nu) * (1 - 2 * nu) * gamma_w * H0**2) / (E * kv)
    t_sec = T_adim * coeff

    if t_sec >= 30 * 86400:
        return f"{t_sec / (30 * 86400):.2f} mesi"
    elif t_sec >= 86400:
        return f"{t_sec / 86400:.2f} giorni"
    else:
        return f"{t_sec / 3600:.2f} ore"


