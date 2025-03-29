# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 14:12:40 2025

@author: Francisco
"""

# libreria_trincee.py

import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp1d

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

    def grafico_interattivo_F(self):
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



    def analisi_intervento(self, S, H0, D):
        """
        Calcola i parametri adimensionali e restituisce un dizionario pronto per l'interpolazione degli abachi.

        S : interasse tra trincee [m]
        H0: profondità trincea [m]
        D : profondità del piano di valutazione efficienza [m]
        """
        if not self.H:
            raise ValueError("Specificare la profondità H del substrato impermeabile nella configurazione del pendio.")

        valori = {
            "S_H0": S / H0,
            "B_H0": 0.16,
            "H_H0": self.H / H0,
            "D_H0": D / H0
        }

        return valori

    def calcola_T(self, t):
        """
        Calcola il tempo adimensionale T dato un tempo t in secondi.
        """
        if None in (self.kv, self.E, self.nu):
            raise ValueError("Per calcolare T è necessario specificare kv, E e nu.")

        coeff = (self.kv * self.gamma_w * (self.H**2)) / (self.E * 2 * (1 + self.nu) * (1 - 2 * self.nu))
        return coeff * t
