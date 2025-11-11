# 🌧️ Mappe pluviometriche Abruzzo (PSDA – AUBAC 2025)

Questo repository contiene i **raster**, i **layer GIS** e il **progetto QGIS** relativi alla regionalizzazione pluviometrica del *Piano Stralcio di Difesa dalle Alluvioni (PSDA Abruzzo)*, rielaborati e digitalizzati per la consultazione e l’uso tecnico.

📄 **Approfondimento completo:**  
🔗 [Articolo sul sito di Francisco J. Mendez](https://www.franciscojmendez.com/progetti/mappe-piogge-abruzzo/)

---

## 🌐 WebGIS interattivo

Per una **rapida consultazione a scala comunale**, è stato elaborato — tramite il repository  
👉 [psda-abruzzo-webgis](https://github.com/FraJoMen/psda-abruzzo-webgis) —  
un **WebGIS interattivo** che consente di esplorare i parametri pluviometrici derivati dal PSDA Abruzzo.

🗺️ **WebGIS – Piogge PSDA Abruzzo:**  
👉 **[Apri la mappa interattiva](https://frajomen.github.io/psda-abruzzo-webgis/)**

---

## 🗂️ Struttura del progetto

```
articolo_03_Piogge Abruzzo/
└─ cartografia/
   ├─ data/
   │  ├─ RASTER/             → GeoTIFF dei parametri h(1,T) e n(T)
   │  │    ├─ RAS_h_TR20–500 → Raster del parametro di scala h(1,T)
   │  │    └─ RAS_n_TR20–500 → Raster del parametro di forma n(T)
   │  ├─ Isolonee_h_TR*.shp  → Isolinee digitalizzate di h per ciascun T
   │  ├─ Isolonee_n_TR*.shp  → Isolinee digitalizzate di n per ciascun T
   │  ├─ Comuni_Analizzati.gpkg → Layer con valori medi comunali e tematismi
   │  ├─ Statistiche_Comunali_CPP.csv → Tabella CSV con statistiche comunali h(1,T), n(T)
   │  ├─ Perimetro.*         → Perimetro d’ambito utilizzato per le elaborazioni
   │  └─ PerimetroAbruzzo.*  → Perimetro regionale di riferimento
   ├─ layers/                → Shapefile e GeoPackage di supporto
   └─ Elaborazione_PioggeAbruzzoPSDA.qgz → Progetto QGIS preconfigurato (percorsi relativi)
```

> **Nota** — Estrai lo ZIP mantenendo la posizione relativa del file `.qgz` rispetto alla cartella `data/`. In questo modo QGIS risolverà automaticamente tutti i percorsi. Tutti i dati sono nel sistema di riferimento **WGS84 / UTM 33N**.

---

## 🧭 Utilizzo

1. Scarica il file compresso **cartografia.zip**, che contiene l’intera struttura del progetto QGIS pronta all’uso.  
   👉 [Vai al repository GitHub](https://github.com/FraJoMen/franciscojmendez_Risorse/tree/main/articolo_03_Piogge%20Abruzzo)
2. Apri in **QGIS ≥ 3.30** il file:
   ```
   articolo_03_Piogge Abruzzo/cartografia/Elaborazione_PioggeAbruzzoPSDA.qgz
   ```
3. Verifica i percorsi dei layer   

---

## ⚖️ Licenza

Questo progetto è distribuito con licenza **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Ciò significa che i dati e le elaborazioni possono essere utilizzati, condivisi e adattati liberamente — anche per scopi professionali e commerciali — a condizione di citare correttamente la fonte originale.

> **Fonte:** PSDA Abruzzo (BETA Studio – WL | Delft Hydraulics, 2002)  
> **Digitalizzazione e interpolazione:** Francisco J. Mendez (2025)  
> **Licenza:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## ⚠️ Avvertenze

I dati e le mappe qui presentati sono condivisi con la **massima attenzione e accuratezza**, ma **senza alcuna garanzia** di completezza, correttezza o idoneità a specifici scopi progettuali. L’utilizzo è libero, a condizione che venga **citata la fonte**, e avviene sotto la **responsabilità esclusiva dell’utente**.

---

✉️ **Per segnalazioni o contributi:**  
[Apri una issue su GitHub](https://github.com/FraJoMen/franciscojmendez_Risorse/issues)
