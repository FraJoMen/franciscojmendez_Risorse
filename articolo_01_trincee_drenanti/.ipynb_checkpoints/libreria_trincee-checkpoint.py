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
            "S/H0": np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0]),
            "efficienza": np.array([0.537, 0.792, 0.943, 0.997, 0.98, 0.96])  # Efficienza per d=0.5
        }
        self.data_n1_d1 = {
            "S/H0": np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0]),
            "efficienza": np.array([0.514, 0.651, 0.770, 0.943, 0.92, 0.88])  # Efficienza per d=1
        }

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
        fig = make_subplots(rows=2, cols=2, subplot_titles=["n=1, d=0.5", "n=1, d=1", "n=1.5, d=0.5", "n=2.5, d=0.5"])

        # Tracciare la curva per n=1, d=0.5
        spline_n1_d0p5 = CubicSpline(self.data_n1_d0p5["S/H0"], self.data_n1_d0p5["efficienza"])
        fig.add_trace(go.Scatter(x=self.data_n1_d0p5["S/H0"], y=spline_n1_d0p5(self.data_n1_d0p5["S/H0"]), mode='lines', name='n=1, d=0.5'), row=1, col=1)

        # Tracciare la curva per n=1, d=1
        spline_n1_d1 = CubicSpline(self.data_n1_d1["S/H0"], self.data_n1_d1["efficienza"])
        fig.add_trace(go.Scatter(x=self.data_n1_d1["S/H0"], y=spline_n1_d1(self.data_n1_d1["S/H0"]), mode='lines', name='n=1, d=1'), row=1, col=2)

        # Aggiungere altre curve per n=1.5, 2.5 se i dati sono pronti
        # fig.add_trace(go.Scatter(...), row=2, col=1)
        # fig.add_trace(go.Scatter(...), row=2, col=2)

        # Layout con dimensioni aumentate
        fig.update_layout(
            title="Abachi Efficienza Idraulica",
            showlegend=True,
            height=1200,  # Altezza in pixel
            width=1800,  # Larghezza in pixel
            template="plotly_white",
            showlegend=True
        )

        fig.update_xaxes(title_text="S/H0")
        fig.update_yaxes(title_text="Efficienza")
        
        fig.show()
