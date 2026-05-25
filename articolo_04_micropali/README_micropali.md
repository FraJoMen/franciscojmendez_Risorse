# Micropali_BustamanteDoix

Foglio di calcolo Excel per la stima della **capacità portante assiale di micropali iniettati**
secondo il metodo di **Bustamante–Doix (1985)**, con raccordo alla verifica secondo le **NTC 2018**.

Questo strumento accompagna l'articolo tecnico pubblicato su [franciscojmendez.com](https://www.franciscojmendez.com/il-metodo-bustamante-doix-per-il-calcolo-dei-micropali/).

---

## 📂 Contenuto del repository

| File | Descrizione |
|---|---|
| `Micropali_BustamanteDoix.xlsx` | Workbook Excel senza macro — per chi vuole esaminare il contenuto prima di abilitare il VBA |
| `Micropali_BustamanteDoix.xlsm` | Workbook Excel con modulo VBA già importato — pronto all'uso |
| `ModuloBustamanteDoix.bas` | Modulo VBA esportato — per chi vuole leggere il codice sorgente prima di importarlo |

---

## 📋 Struttura del workbook

| Foglio | Visibile | Contenuto |
|---|---|---|
| `Credits` | ✅ | Informazioni sull'autore e riferimenti |
| `DATI_INPUT` | ✅ | Dati generali del micropalo, stratigrafia, tipo di terreno e iniezione per strato |
| `TAB_ALPHA` | ✅ | Tabella dei coefficienti di sbulbatura α per categoria di terreno e sistema di iniezione (IGU/IRS) |
| `CALCOLO-Qmedio` | ✅ | Calcolo della resistenza laterale con valori medi di p_l |
| `CALCOLO-Qminimo` | ✅ | Calcolo della resistenza laterale con valori minimi di p_l |
| `NTC2018` | ✅ | Lookup automatico dei fattori di correlazione ξ3/ξ4 |
| `Grafico-SG` | ✅ | Grafico di riferimento — sabbie e ghiaie |
| `Grafico-AL` | ✅ | Grafico di riferimento — argille e limi |
| `Grafico-MC` | ✅ | Grafico di riferimento — crete, marne e marne calcaree |
| `Grafico-RA` | ✅ | Grafico di riferimento — rocce alterate e frantumate |
| `ABACO-SG` | 🔒 nascosto | Dati abaco sabbie e ghiaie (con colonne debug per i grafici) |
| `ABACO-AL` | 🔒 nascosto | Dati abaco argille e limi |
| `ABACO-MC` | 🔒 nascosto | Dati abaco crete, marne e marne calcaree |
| `ABACO-RA` | 🔒 nascosto | Dati abaco rocce alterate e frantumate |
| `DB_Abachi` | 🔒 nascosto | Database delle coordinate digitalizzate dagli abachi originali (Bustamante–Doix, 1985) |

---

## 🧮 Metodo di calcolo

Il metodo Bustamante–Doix stima la resistenza laterale del bulbo iniettato come:

$$Q_s = \sum_i \pi \, D_{s,i} \, q_{s,i} \, l_{s,i}$$

dove per ogni strato *i*:
- **D_s,i** = diametro del bulbo iniettato = α · D_d
- **q_s,i** = attrito laterale limite ricavato dagli abachi in funzione di p_l e del tipo di iniezione
- **l_s,i** = lunghezza del tratto iniettato ricadente nello strato

Il valore di **α** dipende dal tipo di terreno e dalla modalità di iniezione (IGU o IRS).

Il raccordo normativo segue lo schema NTC 2018:

$$Q_{s,cal} \rightarrow Q_{s,k} = \min\!\left(\frac{Q_{s,med}}{\xi_3};\,\frac{Q_{s,min}}{\xi_4}\right) \rightarrow Q_{s,d} = \frac{Q_{s,k}}{\gamma_R}$$

---

## 🛠️ Funzioni VBA disponibili

Le funzioni VBA sono richiamabili direttamente dalle celle, senza macro o pulsanti.

Il repository offre due percorsi:

- **Uso immediato** — scaricare `Micropali_BustamanteDoix.xlsm`, il modulo è già importato e pronto all'uso.
- **Uso consapevole** — leggere prima il codice sorgente in `ModuloBustamanteDoix.bas`, poi importarlo manualmente nel file `.xlsx`:
  1. Aprire Excel e premere `Alt + F11`
  2. Dal menu: *File → Importa file...*
  3. Selezionare `ModuloBustamanteDoix.bas`
  4. Salvare il file come `.xlsm` per mantenere le macro attive

| Funzione | Descrizione |
|---|---|
| `GetQs(tipoTerreno, tipoIniezione, pl)` | Restituisce q_s interpolato dagli abachi |
| `GetAlpha(tipoTerreno, tipoIniezione)` | Restituisce il coefficiente α |
| `GetVi_min(tipoTerreno, tipoIniezione, Dd, Ls)` | Restituisce la quantità minima di malta V_i |
| `GetPl_fromNSPT(tipoTerreno, NSPT)` | Stima p_l da N_SPT (non disponibile per rocce alterate) |

---

## 📐 Campi di validità

| Tipo terreno | Codice | Intervallo p_l valido |
|---|---|---|
| Sabbie e ghiaie | `SG` | 0.25 – 7.0 MPa |
| Argille e limi | `AL` | 0.25 – 2.5 MPa |
| Marne e crete | `MC` | 1.0 – 8.0 MPa |
| Rocce alterate | `RA` | 1.4 – 8.2 MPa |

Valori fuori intervallo restituiscono `#N/A`.

---

## 💻 Requisiti

- Microsoft Excel (versione 2016 o successiva consigliata)
- Testato su Excel 365 (italiano) — alcune formule usano la sintassi italiana
  (es. `NON.DISP()` al posto di `NA()`)

---

## ⚠️ Avvertenze

I dati, le curve e i parametri contenuti in questo strumento sono stati digitalizzati e implementati con la massima attenzione e accuratezza, ma senza alcuna garanzia di completezza, correttezza o idoneità a specifici scopi progettuali. Il foglio di calcolo è uno strumento di supporto alla progettazione e non sostituisce il giudizio professionale del progettista, né la verifica critica dei risultati alla luce del contesto geotecnico specifico.

L'utilizzo è libero nei termini della licenza GNU GPL v3, e avviene sotto la responsabilità esclusiva dell'utente.

---

## 💬 Contribuisci o commenta

- Apri una **issue** su GitHub per suggerire modifiche o segnalare errori
- Lascia un **commento** direttamente sull'articolo sul sito
- Usa il [modulo contatti](https://franciscojmendez.com/contatti/) per dubbi o osservazioni

---

## 📜 Licenza

Questo progetto è distribuito con licenza **GNU General Public License v3.0**.
Chiunque può usarlo, modificarlo e redistribuirlo, purché mantenga la stessa licenza.
👉 [Consulta il testo completo](https://www.gnu.org/licenses/gpl-3.0.it.html)

---

## 📚 Riferimenti

- Bustamante M., Doix B. — *Une méthode pour le calcul des tirants et des micropieux injectés*, Bulletin de Liaison des Laboratoires des Ponts et Chaussées, 1985
- NTC 2018 — *Norme Tecniche per le Costruzioni*, D.M. 17 gennaio 2018
- Circolare n. 7/2019 — *Istruzioni per l'applicazione delle NTC 2018*
- FHWA NHI-05-039 — *Micropile Design and Construction*, Federal Highway Administration

---

*Sviluppato da [Francisco J. Méndez](https://franciscojmendez.com)*
