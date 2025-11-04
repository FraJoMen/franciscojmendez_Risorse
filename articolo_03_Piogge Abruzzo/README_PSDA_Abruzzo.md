# 🌧️ Mappe pluviometriche Abruzzo (PSDA – AUBAC 2025)

Questo repository contiene i **raster** e i **layer GIS** relativi alla regionalizzazione pluviometrica del *Piano Stralcio di Difesa dalle Alluvioni (PSDA Abruzzo)*, rielaborati e digitalizzati per la consultazione e l’uso in ambiente QGIS.

📄 **Approfondimento completo:**  
🔗 [Articolo sul sito di Francisco J. Mendez](https://www.franciscojmendez.com/progetti/mappe-piogge-abruzzo/)

---

## 🗂️ Struttura del progetto

```
articolo_03_Piogge Abruzzo/
└─ cartografia/
   ├─ data/
   │  ├─ RASTER/   → GeoTIFF: RAS_h_TR20–500, RAS_n_TR20–500
   │  └─ GPKG/     → GeoPackage: statistiche comunali e tematismi
   ├─ layers/      → shapefile/GeoPackage di riferimento
   └─ progetto.qgz → progetto QGIS (percorsi relativi)
```

---

## 🧭 Utilizzo

1. Scarica il file compresso **cartografia.zip**, che contiene l'intera struttura del progetto QGIS pronta all'uso:  
   <br>Puoi anche scaricare l'intero pacchetto direttamente dal repository GitHub: <a href="https://github.com/FraJoMen/franciscojmendez_Risorse/tree/main/articolo_03_Piogge%20Abruzzo" target="_blank">articolo_03_Piogge Abruzzo</a>
2. Apri in **QGIS ≥ 3.30** il file:  
   `articolo_03_Piogge Abruzzo/cartografia/progetto.qgz`
3. Verifica che i percorsi dei layer siano impostati su **Relativi** (*Progetto → Proprietà → Generale → Percorsi*).

---

## ⚖️ Licenza

Questo progetto è distribuito con licenza **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Ciò significa che i dati e le elaborazioni possono essere utilizzati, condivisi e adattati liberamente — anche per scopi professionali e commerciali — a condizione di citare correttamente la fonte originale.

> Fonte: PSDA Abruzzo (BETA Studio – WL | Delft Hydraulics, 2002)  
> Digitalizzazione e interpolazione: F.J. Mendez (2025)  
> Licenza: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

---

✉️ Per segnalazioni o contributi:  
[Apri una issue su GitHub](https://github.com/FraJoMen/franciscojmendez_Risorse/issues)
