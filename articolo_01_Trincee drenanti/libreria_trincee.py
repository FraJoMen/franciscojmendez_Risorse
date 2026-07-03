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
            "x_min": 0.487, "x_max": 6.003,
            "nodi_interni": [1.036103, 3.309614],
            "coef": [-2.76089534, -1.81403305, -0.68220560, -0.62888476, -0.66221600, -0.65872688]
        }
        self.curve_T50_n1_d1p0 = {
            "x_min": 0.484, "x_max": 6.000,
            "nodi_interni": [0.792061, 2.721681],
            "coef": [-2.69648223, -1.84144584, -0.64705307, -0.35262756, -0.49464053, -0.46001051]
        }
        self.curve_T90_n1_d0p5 = {
            "x_min": 0.498, "x_max": 6.013,
            "nodi_interni": [1.553947, 4.272008],
            "coef": [-1.24930520, -0.21297843, 0.68045281, 0.60400063, 0.66241861, 0.62568415]
        }
        self.curve_T90_n1_d1p0 = {
            "x_min": 0.492, "x_max": 6.008,
            "nodi_interni": [1.665461, 3.796127],
            "coef": [-1.23689244, -0.05869091, 0.59287275, 0.71113093, 0.68233148, 0.68113623]
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
            return 1e-2, 1e1
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
                y_min_plot, y_max_plot = 1e-2, 1e1
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
                    rng = [-2, 1]
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

# class AbachiTemporali:
#     def __init__(self):
#         """
#         Dati degli abachi temporali (T50 e T90) per n = 1 e n = 2.5.
#         Le curve sono fornite per diversi valori di D/H0.
#         """

#         # === n = 1.0 ===
#         self.data_T50_n1_d0p5 = {
#             "S/H0": np.array([0.502437236, 0.511793276, 0.531862982, 0.583978966, 0.646998051, 0.736801301,
#                               0.911745566, 1.049949747, 1.215127527, 1.407089472, 1.604566112, 1.818207969,
#                               2.385053489, 2.749065536, 3.113235446, 3.386433917, 3.702550196, 4.104312654,
#                               4.452538356, 4.843555576, 5.170322375, 5.513128099, 5.845283303]),
#             "T": np.array([0.001377717, 0.002033229, 0.003001163, 0.004554195, 0.006546911, 0.009415737,
#                            0.015959247, 0.021757212, 0.028106889, 0.036325806, 0.044875685, 0.053967905,
#                            0.07211513, 0.07799788, 0.080629502, 0.080995708, 0.079961449, 0.080496096,
#                            0.080233188, 0.081489205, 0.081932084, 0.083148177, 0.082854518])
#         }

#         self.data_T50_n1_d1p0 = {
#             "S/H0": np.array([0.508015078, 0.517686845, 0.564319705, 0.627244073, 0.711690489, 0.80694529,
#                               0.982142137, 1.205708342, 1.445692345, 1.648494246, 1.910284452, 2.129472578,
#                               2.380927991, 2.611050792, 2.959118631, 3.237610789, 3.612652229, 3.960846359,
#                               4.255503733, 4.550097963, 4.828653267, 5.042863432, 5.310705071, 5.621464517,
#                               5.916121892]),
#             "T": np.array([0.001293288, 0.001743537, 0.002743031, 0.004051751, 0.00582669, 0.008156263,
#                            0.012859289, 0.019392988, 0.026483098, 0.033016593, 0.040463375, 0.046094689,
#                            0.05067048, 0.054189814, 0.056512188, 0.057810514, 0.057128123, 0.057459022,
#                            0.05722049, 0.058023377, 0.05829209, 0.05956776, 0.059832991, 0.059063717,
#                            0.058818523])
#         }

#         self.data_T90_n1_d0p5 = {
#             "S/H0": np.array([0.504121113, 0.529579224, 0.613994068, 0.70382889, 0.799178408, 0.915955258,
#                               1.064841531, 1.240701405, 1.379379176, 1.560848463, 1.790529246, 2.009622654,
#                               2.239556018, 2.491011431, 2.710483711, 2.956708582, 3.192314506, 3.433340408,
#                               3.647550573, 3.856467051, 4.12963395, 4.429585012, 4.729536074, 4.981275642,
#                               5.318756106, 5.575947224, 5.913459262]),
#             "T": np.array([0.018320797, 0.026801384, 0.038892469, 0.055431204, 0.075515562, 0.102913646,
#                            0.141602216, 0.184623001, 0.219756123, 0.266540349, 0.323543174, 0.378711209,
#                            0.427607263, 0.470055572, 0.49360162, 0.523270121, 0.539772784, 0.546860464,
#                            0.558828017, 0.560767888, 0.568434217, 0.576461402, 0.584601942, 0.59238353,
#                            0.595708878, 0.587527562, 0.58550458])
#         }

#         self.data_T90_n1_d1p0 = {
#             "S/H0": np.array([0.509477946, 0.545776013, 0.619571909, 0.688231982, 0.783549928, 0.884477288,
#                               0.985436221, 1.15581297, 1.363719122, 1.582528376, 1.801495493, 2.041953086,
#                               2.336136871, 2.694665794, 2.946279071, 3.321099501, 3.610336898, 3.819253376,
#                               4.156702268, 4.408473408, 4.686997139, 4.938736707, 5.142264779, 5.474419983,
#                               5.774434191, 5.919100249]),
#             "T": np.array([0.018322425, 0.02585573, 0.036509071, 0.048384121, 0.066514151, 0.085061194,
#                            0.10780027, 0.145717999, 0.195320408, 0.248019, 0.301007318, 0.358893356,
#                            0.40934967, 0.459016656, 0.482266781, 0.507731134, 0.514809602, 0.516596671,
#                            0.524217779, 0.526411564, 0.533655619, 0.540759064, 0.547519044, 0.54558534,
#                            0.543368705, 0.539768423])
#         }
        
#         # === n = 2.5 ===
#         self.data_T50_n2p5_d0p5 = {
#             "S/H0": np.array([0.50428235, 0.56837503, 0.64333464, 0.72380691, 0.8260764, 0.9337635,
#                               1.04696328, 1.1548088, 1.28445153, 1.42492951, 1.56017995, 1.73892978,
#                               1.91238872, 2.12418287, 2.32517346, 2.70583266, 2.94528519, 3.1738708,
#                               3.40800076, 3.68572515, 4.00701228, 4.38827344, 4.60608717, 4.85666008,
#                               5.09088509, 5.47765891, 5.82641434]),
#             "T": np.array([0.002021, 0.002917, 0.004248, 0.006078, 0.008698, 0.012561,
#                            0.017821, 0.024613, 0.034004, 0.047833, 0.063206, 0.085841,
#                            0.111486, 0.137321, 0.164647, 0.206972, 0.227101, 0.246933,
#                            0.261425, 0.276947, 0.296213, 0.314284, 0.329693, 0.339904,
#                            0.350346, 0.365174, 0.367073])
#         }

#         self.data_T50_n2p5_d1p0 = {
#             "S/H0": np.array([0.50082901, 0.52696666, 0.56352768, 0.63294294, 0.71867443, 0.8371651,
#                               0.9939593, 1.15623449, 1.34056035, 1.57389826, 1.79655934, 2.02479644,
#                               2.26412225, 2.5415615, 2.80832392, 3.06425109, 3.32565925, 3.57075118,
#                               3.87584881, 4.13183935, 4.63298518, 4.91080462, 5.16685852, 5.41743144,
#                               5.69534592, 5.9514315]),
#             "T": np.array([0.005346, 0.007309, 0.011426, 0.01709, 0.025799, 0.038275,
#                            0.054336, 0.076458, 0.100205, 0.132603, 0.164822, 0.197701,
#                            0.224811, 0.258077, 0.278279, 0.294707, 0.309356, 0.32177,
#                            0.329055, 0.342315, 0.363847, 0.375268, 0.383485, 0.395362,
#                            0.397, 0.402087])
#         }

#         self.data_T50_n2p5_d1p5 = {
#             "S/H0": np.array([0.52069362, 0.787361, 1.01591492, 1.32072742, 1.60922369, 1.91951717,
#                               2.26256983, 2.61110348, 2.99778226, 3.33548067, 3.62964801, 3.94561257,
#                               4.21801438, 4.52311202, 4.86090547, 5.24229335, 5.48206271, 5.9070767]),
#             "T": np.array([0.198573, 0.219927, 0.241276, 0.267374, 0.293591, 0.322483,
#                            0.348121, 0.372489, 0.398789, 0.419088, 0.432348, 0.446172,
#                            0.456051, 0.466376, 0.477167, 0.488524, 0.49027, 0.497802])
#         }

#         self.data_T50_n2p5_d2p0 = {
#             "S/H0": np.array([0.51429386, 0.67761456, 0.92264312, 1.09138144, 1.33641, 1.55960968,
#                               1.79918894, 2.02790128, 2.33280882, 2.63787477, 2.8720681, 3.23707639,
#                               3.48761762, 3.81993009, 4.16859047, 4.4682388, 4.71342577, 5.0076248,
#                               5.32365272, 5.56342208, 5.91756344]),
#             "T": np.array([0.259512, 0.272015, 0.288026, 0.304633, 0.322564, 0.3445,
#                            0.364748, 0.382693, 0.412884, 0.426016, 0.44304, 0.45754,
#                            0.475939, 0.491276, 0.507231, 0.518673, 0.525235, 0.537039,
#                            0.544407, 0.546352, 0.559129])
#         }

#         self.data_T90_n2p5_d0p5 = {
#             "S/H0": np.array([0.51964286, 0.5625, 0.63214286, 0.7125, 0.825, 0.96428571,
#                               1.11428571, 1.275, 1.47857143, 1.70357143, 1.90178571, 2.12678571,
#                               2.3625, 2.59821429, 2.89821429, 3.16607143, 3.46071429, 3.71785714,
#                               3.94821429, 4.2, 4.52142857, 4.78928571, 5.1375, 5.49642857,
#                               5.72678571, 5.94107143]),
#             "T": np.array([0.002868, 0.00437, 0.006056, 0.008067, 0.011096, 0.014789,
#                            0.019097, 0.023516, 0.02897, 0.034857, 0.039978, 0.045502,
#                            0.049779, 0.054027, 0.058678, 0.062207, 0.065968, 0.068283,
#                            0.070099, 0.072555, 0.074557, 0.075965, 0.078084, 0.079636,
#                            0.07983, 0.080012])
#         }

#         self.data_T90_n2p5_d1p0 = {
#             "S/H0": np.array([0.51964286, 0.55714286, 0.59464286, 0.63214286, 0.69107143,
#                               0.77142857, 0.87857143, 0.98035714, 1.15714286, 1.32321429,
#                               1.47321429, 1.69821429, 1.99821429, 2.26607143, 2.55, 2.94107143,
#                               3.23571429, 3.48214286, 3.7875, 4.17857143, 4.58035714, 5.025,
#                               5.28214286, 5.53928571, 5.7375]),
#             "T": np.array([0.002868, 0.004511, 0.005681, 0.006931, 0.008801, 0.011723,
#                            0.015012, 0.018474, 0.025427, 0.030819, 0.036759, 0.044938,
#                            0.055417, 0.064624, 0.071867, 0.080012, 0.085525, 0.087816,
#                            0.092399, 0.096539, 0.101681, 0.105458, 0.107438, 0.10859,
#                            0.108818])
#         }

#         self.data_T90_n2p5_d1p5 = {
#             "S/H0": np.array([0.51428571, 0.71785714, 0.9, 1.06607143, 1.275, 1.47857143,
#                               1.65, 1.86964286, 2.05714286, 2.28214286, 2.49107143, 2.72678571,
#                               3.00535714, 3.21428571, 3.47678571, 3.72321429, 3.94285714,
#                               4.20535714, 4.41964286, 4.70357143, 4.9125, 5.22321429, 5.52321429,
#                               5.84464286, 5.96785714]),
#             "T": np.array([0.104612, 0.115318, 0.126085, 0.134591, 0.146035, 0.155948,
#                            0.163854, 0.175007, 0.181013, 0.193344, 0.201619, 0.206995,
#                            0.214306, 0.219958, 0.227688, 0.228283, 0.230638, 0.236855,
#                            0.239285, 0.241919, 0.244387, 0.245193, 0.247933, 0.246811,
#                            0.249103])
#         }

#         self.data_T90_n2p5_d2p0 = {
#             "S/H0": np.array([0.525, 0.69107143, 0.87321429, 0.98571429, 1.15714286,
#                               1.28571429, 1.4625, 1.63928571, 1.81607143, 2.11071429,
#                               2.34642857, 2.53392857, 2.775, 2.94642857, 3.13928571,
#                               3.36964286, 3.66964286, 3.91071429, 4.14642857, 4.44642857,
#                               4.91785714, 5.44285714, 5.7375]),
#             "T": np.array([0.18978, 0.197814, 0.206222, 0.209773, 0.218665, 0.224241,
#                            0.230076, 0.237946, 0.248046, 0.25685, 0.265801, 0.272749,
#                            0.280038, 0.282783, 0.28562, 0.2909, 0.296497, 0.302012,
#                            0.30518, 0.306151, 0.312608, 0.316856, 0.315332])
#         }
        

#     def add_griglia_secondaria_y(self, fig, row, col, y_min=1e-3, y_max=1e1,
#                                  color="rgba(200,200,200,0.2)", width=0.5):
    
#         # Esponenti log base 10 tra y_min e y_max (senza sforare!)
#         e_min = int(np.floor(np.log10(y_min)))
#         e_max = int(np.floor(np.log10(y_max))) 
    
#         esponenti = np.arange(e_min, e_max)
    
#         for e in esponenti:
#             for m in range(2, 10):  # Minor ticks: 2·10^e ... 9·10^e
#                 y = m * np.power(10.0, e)
#                 if y_min <= y <= y_max:
#                     fig.add_shape(
#                         type="line",
#                         x0=0, x1=1,
#                         y0=y, y1=y,
#                         line=dict(color=color, width=width),
#                         xref="x domain",
#                         yref="y",
#                         row=row,
#                         col=col
#                     )

        
#     def plot_abachi(self):
#         fig = make_subplots(
#             rows=2, cols=2,
#             subplot_titles=["T50 – n=1.0", "T90 – n=1.0", "T50 – n=2.5", "T90 – n=2.5"],
#             vertical_spacing=0.15
#         )
    
#         x_interp = np.linspace(0.5, 6.0, 250)
    
#         configurazioni = [
#             ("T50", "n1", 1, 1),
#             ("T90", "n1", 1, 2),
#             ("T50", "n2p5", 2, 1),
#             ("T90", "n2p5", 2, 2)
#         ]
    
#         for tipo, n_label, r, c in configurazioni:
#             for d in ["0p5", "1p0", "1p5", "2p0"]:
#                 attr = f"data_{tipo}_{n_label}_d{d}"
#                 if hasattr(self, attr):
#                     data = getattr(self, attr)
#                     x = data["S/H0"]
#                     y = data["T"]
#                     spline_log = CubicSpline(x, np.log10(y), extrapolate=False)
#                     y_vals = 10 ** spline_log(x_interp)
#                     fig.add_trace(
#                         go.Scatter(
#                             x=x_interp,
#                             y=y_vals,
#                             mode='lines',
#                             #name=f"{tipo}, n={n_label.replace('p', '.')}, d={d.replace('p', '.')}",
#                             name=f"{tipo}, n={n_label[1:].replace('p', '.')}, d={d.replace('p', '.')}",
#                             hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"
#                         ),
#                         row=r,
#                         col=c
#                     )
    
#             # ✅ Griglia log secondaria con limiti fissi per ogni subplot
#             if (r, c) == (2, 2):  # T90 – n=2.5
#                 y_min_plot = 1e-2
#                 y_max_plot = 1e+1
#             else:
#                 y_min_plot = 1e-3
#                 y_max_plot = 1e+0
    
#             self.add_griglia_secondaria_y(fig, r, c, y_min=y_min_plot, y_max=y_max_plot)
    
#         fig.update_layout(
#             title="Abachi Temporali",
#             height=750,
#             width=1000,
#             template="plotly_white",
#             showlegend=True,
#             title_x=0.5,
#             margin=dict(t=50, b=50, l=50, r=50)
#         )
    
#         tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
#         ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]
    
#         for r in [1, 2]:
#             for c in [1, 2]:
#                 fig.update_xaxes(
#                     title_text="S/H₀",
#                     tickformat=".2f",
#                     row=r,
#                     col=c
#                 )
#                 fig.update_yaxes(
#                     type="log",
#                     title_text="T50" if c == 1 else "T90",
#                     tickmode="array",
#                     tickvals=tickvals,
#                     ticktext=ticktext,
#                     ticks="outside",
#                     ticklen=8,
#                     showgrid=True,
#                     gridcolor="lightgray",
#                     range=(
#                         [-3, -1] if (r == 1 and c == 1) else
#                         [-2,  0] if (r == 1 and c == 2) else
#                         [-3,  0] if (r == 2 and c == 1) else
#                         [-3,  0] if (r == 2 and c == 2) else None
#                     ),
#                     row=r,
#                     col=c
#                 )
       
#         fig.show()

#     def add_griglia_subplot(self, fig, y_min=1e-3, y_max=1e1,
#                                  color="rgba(200,200,200,0.2)", width=0.5):
#         e_min = int(np.floor(np.log10(y_min)))
#         e_max = int(np.floor(np.log10(y_max)))
#         for e in np.arange(e_min, e_max):
#             for m in range(2, 10):
#                 y = m * np.power(10.0, e)
#                 if y_min <= y <= y_max:
#                     fig.add_shape(
#                         type="line",
#                         x0=0, x1=1,
#                         y0=y, y1=y,
#                         line=dict(color=color, width=width),
#                         xref="x domain",
#                         yref="y"
#                     )


#     def get_y_limits(self, tipo, n_label):
#         if tipo == "T50" and n_label == "n1":
#             return 1e-3, 1e-1  # log10 → [–3, -1]
#         elif tipo == "T90" and n_label == "n1":
#             return 1e-2, 1e0  # log10 → [–2, 0]
#         else:  # Tutti gli altri
#             return 1e-3, 1e0  # log10 → [–3, 0]
        
#     def plot_singolo(self, tipo, n_label, d_list=["0p5", "1p0", "1p5", "2p0"], export_html=False, filename="grafico.html"):
#         fig = go.Figure()
#         x_interp = np.linspace(0.5, 6.0, 250)
    
#         for d in d_list:
#             attr = f"data_{tipo}_{n_label}_d{d}"
#             if hasattr(self, attr):
#                 data = getattr(self, attr)
#                 x = data["S/H0"]
#                 y = data["T"]
#                 spline_log = CubicSpline(x, np.log10(y), extrapolate=False)
#                 y_vals = 10 ** spline_log(x_interp)
    
#                 fig.add_trace(go.Scatter(
#                     x=x_interp,
#                     y=y_vals,
#                     mode="lines",
#                     name=f"d={d.replace('p', '.')}",
#                     hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"
#                 ))
    
#         y_min_plot, y_max_plot = self.get_y_limits(tipo, n_label)
#         self.add_griglia_subplot(fig, y_min=y_min_plot, y_max=y_max_plot)
    
#         tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
#         ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]
    
#         fig.update_layout(
#             title=f"Abaco n={n_label[1:].replace('p', '.')}",
#             template="plotly_white",
#             showlegend=True,
#             legend=dict(
#                 orientation='h',
#                 x=1,
#                 xanchor='right',
#                 y=1.1,
#                 yanchor='bottom'
#             ),
#             font=dict(family="Roboto", size=14, color="black"),
#             margin=dict(t=140, b=50, l=50, r=50),
#             hovermode="closest"
#         )
    
#         fig.update_xaxes(
#             title_text="S/H₀",
#             tickformat=".2f",
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1
#         )
    
#         fig.update_yaxes(
#             type="log",
#             title_text=tipo,
#             tickmode="array",
#             tickvals=tickvals,
#             ticktext=ticktext,
#             ticks="outside",
#             ticklen=8,
#             showgrid=True,
#             gridcolor="#EAF2F6",
#             range=[np.log10(y_min_plot), np.log10(y_max_plot)],
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1
#         )
    
#         if export_html:
#             fig.write_html(
#                 filename,
#                 include_plotlyjs="cdn",
#                 config={
#                     "responsive": True,
#                     "displaylogo": False,
#                     "displayModeBar": True,
#                     "modeBarButtonsToAdd": ["hoverClosestCartesian"]
#                 }
#             )
#             fig.show()
#         else:
#             fig.show()

#     def plot_abaco_risultati(self, SuH0, n_label='n=1.0', tipo='T50'):
#         """
#         Plotta tutte le curve dell'abaco temporale per un dato n_label (es. 'n=1.0')
#         evidenziando il punto corrispondente a Su/H0 su ciascuna curva (per ogni d).
    
#         Parametri:
#         - SuH0: valore del rapporto S/H₀ per cui si vuole ricavare T
#         - n_label: stringa del tipo 'n=1.0'
#         - tipo: 'T50' o 'T90'
#         """
#         def clean_label(label):
#             val = label.split('=')[1]
#             if val.endswith('.0'):
#                 val = val[:-2]
#             return val.replace('.', 'p')
    
#         n_clean = clean_label(n_label)
#         d_list = ["0p5", "1p0", "1p5", "2p0"]
    
#         fig = go.Figure()
#         x_interp = np.linspace(0.5, 6.0, 250)
    
#         for d_clean in d_list:
#             dataset_name = f"data_{tipo}_n{n_clean}_d{d_clean}"
#             if not hasattr(self, dataset_name):
#                 continue
    
#             data = getattr(self, dataset_name)
#             x = data["S/H0"]
#             y = data["T"]
    
#             # Interpolazione log su y
#             spline_log = CubicSpline(x, np.log10(y), extrapolate=False)
#             y_interp = 10 ** spline_log(x_interp)
    
#             fig.add_trace(go.Scatter(
#                 x=x_interp,
#                 y=y_interp,
#                 mode="lines",
#                 name=f"d={d_clean.replace('p', '.')}",
#                 hovertemplate="S/H₀: %{x:.2f}<br>T: %{y:.2e}<extra></extra>"
#             ))
    
#             if min(x) <= SuH0 <= max(x):
#                 T_val = 10 ** spline_log(SuH0)
#                 fig.add_trace(go.Scatter(
#                     x=[SuH0],
#                     y=[T_val],
#                     mode="markers",
#                     marker=dict(size=10, color="red", symbol="diamond"),
#                     name=f"Punto d={d_clean.replace('p', '.')}"
#                 ))
    
#         # Griglia, limiti e stile coerente
#         y_min_plot, y_max_plot = self.get_y_limits(tipo, f"n{n_clean}")
#         self.add_griglia_subplot(fig, y_min=y_min_plot, y_max=y_max_plot)
    
#         tickvals = [1e-3, 1e-2, 1e-1, 1e0, 1e1]
#         ticktext = [f"1e{int(np.log10(v))}" for v in tickvals]
    
#         fig.update_layout(
#             title=f"Abachi {tipo} – {n_label}",
#             template="plotly_white",
#             showlegend=True,
#             font=dict(family="Roboto", size=14),
#             margin=dict(t=100),
#             hovermode="closest"
#         )
    
#         fig.update_xaxes(
#             title_text="S / H₀",
#             tickformat=".2f",
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1
#         )
    
#         fig.update_yaxes(
#             type="log",
#             title_text=tipo,
#             tickmode="array",
#             tickvals=tickvals,
#             ticktext=ticktext,
#             ticks="outside",
#             ticklen=8,
#             showgrid=True,
#             gridcolor="#EAF2F6",
#             range=[np.log10(y_min_plot), np.log10(y_max_plot)],
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1
#         )
    
#         fig.show()
        
#     def ricava_T_da_SuH0(self, SuH0, tipo="T50", n_label="n=1.0", d_label="d=1.0"):
#         """
#         Calcola il valore di T (T50 o T90) corrispondente a un dato S/H0
#         per una coppia (n, d) fornite come etichette 'n=1.0', 'd=1.0'.
#         """
#         def clean_d_label(label):
#             value = label.split('=')[1]
#             return value.replace('.', 'p')
    
#         n_clean = n_label.split('=')[1]  # es: 'n=1.0' → '1.0' (n va lasciato così!)
#         d_clean = clean_d_label(d_label)  # es: 'd=1.0' → '1p0'
    
#         nome_df = f"data_{tipo}_n{n_clean.replace('.0','')}_d{d_clean}"  # es: data_T50_n1_d1p0
    
#         if not hasattr(self, nome_df):
#             raise ValueError(f"Dataset {nome_df} non disponibile.")
    
#         data = getattr(self, nome_df)
#         x = data["S/H0"]
#         y = data["T"]
    
#         if SuH0 < min(x) or SuH0 > max(x):
#             raise ValueError(f"S/H0 = {SuH0:.3f} è fuori dall'intervallo ({min(x):.2f}, {max(x):.2f}) per {nome_df}")
    
#         spline_log = CubicSpline(x, np.log10(y), extrapolate=False)
#         log_T = spline_log(SuH0)
#         return float(10**log_T)


# #%%
# class AbacoPortate:
#     def __init__(self):
#         self.s = np.array([0,
#             0.04176044, 0.17815168077733734, 0.3039688493551962, 0.4083163648054873,
#             0.5228092737470083, 0.7302897152859644, 0.9372343085771442, 1.0817347193941342,
#             1.2776051155646055, 1.6071160647304688, 1.946772407387561, 2.4303218661808312,
#             2.9241238881148863, 3.376701318186689, 3.7470796270496196, 4.220412245918622,
#             4.8994391455006605
#         ])

#         self.q = np.array([0,
#             0.075095917, 0.38377022827135376, 0.6590847711927983, 0.8301789733147573,
#             0.9846318722537777, 1.185150573357625, 1.323167934840853, 1.3776958525345622,
#             1.4240188618583218, 1.4581759725645698, 1.475691780087879, 1.4769006537348623,
#             1.473968492123031, 1.4625999356982105, 1.4635258814703676, 1.4730425463508734,
#             1.4747401135998284
#         ])

#     def plot(self, export_html=False, filename="Art1_Abachi_portata.html"):
#         s_interp = np.linspace(self.s.min(), self.s.max(), 300)
#         q_interp = CubicSpline(self.s, self.q)(s_interp)

#         fig = go.Figure()
#         fig.add_trace(go.Scatter(
#             x=s_interp,
#             y=q_interp,
#             mode='lines',
#             name="q",
#             hovertemplate="s: %{x:.2f}<br>q: %{y:.3f}<extra></extra>"
#         ))

#         fig.update_layout(
#             title="Fattore di portata",
#             xaxis_title="s",
#             yaxis_title="q",
#             template="plotly_white",
#             font=dict(family="Roboto", size=14, color="black"),
#             margin=dict(t=100, b=50, l=50, r=50),
#             hovermode="closest",
#             showlegend=False
#         )

#         fig.update_xaxes(
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1
#         )

#         fig.update_yaxes(
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1,
#             showgrid=True,
#             gridcolor="#EAF2F6"
#         )

#         if export_html:
#             fig.write_html(
#                 filename,
#                 include_plotlyjs="cdn",
#                 config={
#                     "responsive": True,
#                     "displaylogo": False,
#                     "displayModeBar": True,
#                     "modeBarButtonsToAdd": ["hoverClosestCartesian"]
#                 }
#             )
#         fig.show()
        
#     def calcola_portata(self, S, kv, kh, D):
#         """
#         Calcola la portata drenata per metro lineare di trincea e la visualizza in l/h.
    
#         Parametri:
#         - S: interasse delle trincee [m]
#         - kv: permeabilità verticale [m/s]
#         - kh: permeabilità orizzontale [m/s]
#         - D: profondità del piano di scorrimento [m]
    
#         Ritorna:
#         - Q_lh: portata in litri all’ora (l/h) per metro lineare
#         """
#         s_adim = (S * np.sqrt(kv / kh)) / (2 * D)
    
#         # Interpolazione del fattore di portata adimensionale
#         spline = CubicSpline(self.s, self.q, extrapolate=False)
#         q_adim = float(spline(s_adim))
    
#         # Calcolo della portata in l/h
#         Q_lh = q_adim * kv * D * 1000 * 3600  # da m³/s → l/h
    
#         # Dati per grafico
#         s_plot = np.linspace(0, self.s.max(), 300)
#         q_plot = spline(s_plot)
#         S_plot = 2 * D * s_plot / np.sqrt(kv / kh)
#         Q_plot_lh = q_plot * kv * D * 1000 * 3600  # l/h
    
#         fig = go.Figure()
    
#         fig.add_trace(go.Scatter(
#             x=S_plot,
#             y=Q_plot_lh,
#             mode="lines",
#             name="Q(S)",
#             hovertemplate="S = %{x:.2f} m<br>Q = %{y:.2e} l/h<extra></extra>"
#         ))
    
#         fig.add_trace(go.Scatter(
#             x=[S],
#             y=[Q_lh],
#             mode="markers",
#             marker=dict(size=10, color="red", symbol="diamond"),
#             name="Punto di progetto",
#             hovertemplate="S = %{x:.2f} m<br>Q = %{y:.2e} l/h<extra></extra>"
#         ))
    
#         fig.update_layout(
#             title="Portata drenata per metro lineare",
#             xaxis_title="Interasse S [m]",
#             yaxis_title="Q [l/h]",
#             template="plotly_white",
#             showlegend=False,
#             font=dict(family="Roboto", size=14),
#             margin=dict(t=100, b=50, l=50, r=50),
#             hovermode="closest"
#         )
    
#         fig.update_xaxes(
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1
#         )
    
#         fig.update_yaxes(
#             tickformat=".1e",  # ✅ notazione scientifica
#             showspikes=True,
#             spikecolor="grey",
#             spikethickness=1,
#             linecolor="black",
#             linewidth=1,
#             showgrid=True,
#             gridcolor="#EAF2F6"
#         )
    
#         fig.show()
#         return Q_lh


# def calcola_tempo_reale(T_adim, H0, kv, gamma_w, E, nu):
#     """
#     Calcola il tempo reale corrispondente a un tempo adimensionale T,
#     restituendo il risultato con unità di misura intelligenti.

#     Parametri:
#     - T_adim: tempo adimensionale (T)
#     - H0: profondità del dreno [m]
#     - kv: permeabilità verticale [m/s]
#     - gamma_w: peso specifico dell'acqua [kN/m³]
#     - E: modulo di Young [kPa]
#     - nu: coefficiente di Poisson

#     Ritorna:
#     - Stringa del tipo "5.6 mesi", "12.3 giorni" o "4.2 ore"
#     """
#     # Calcolo tempo in secondi
#     coeff = (2 * (1 + nu) * (1 - 2 * nu) * gamma_w * H0**2) / (E * kv)
#     t_sec = T_adim * coeff

#     # Conversione e scelta dell'unità più adatta
#     if t_sec >= 30 * 86400:
#         t_mesi = t_sec / (30 * 86400)
#         return f"{t_mesi:.2f} mesi"
#     elif t_sec >= 86400:
#         t_giorni = t_sec / 86400
#         return f"{t_giorni:.2f} giorni"
#     else:
#         t_ore = t_sec / 3600
#        return f"{t_ore:.2f} ore"
