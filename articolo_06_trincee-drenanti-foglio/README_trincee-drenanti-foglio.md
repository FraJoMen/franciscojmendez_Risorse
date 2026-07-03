# Trincee_Drenanti

Foglio di calcolo Excel per il **dimensionamento di massima delle trincee drenanti**
secondo il metodo di **Desideri, Miliziano e Rampello (1997)**.

Questo strumento accompagna l'articolo tecnico pubblicato su [franciscojmendez.com](#).

---

## 📂 Contenuto del repository

| File | Descrizione |
|---|---|
| `Trincee_Drenanti.xlsx` | Workbook Excel senza macro — per chi vuole esaminare il contenuto prima di abilitare il VBA |
| `Trincee_Drenanti_v1_0.xlsm` | Workbook Excel con modulo VBA già importato — pronto all'uso |
| `ModuloTrincee_v1_0.bas` | Modulo VBA esportato — per chi vuole leggere il codice sorgente prima di importarlo |

---

## 📋 Struttura del workbook

| Foglio | Visibile | Contenuto |
|---|---|---|
| `Credits` | ✅ | Informazioni sull'autore e riferimenti |
| `DATI_INPUT` | ✅ | Geometria del versante, parametri geotecnici e obiettivi progettuali |
| `ANALISI` | ✅ | Verifica sequenziale: F(Z), efficienza richiesta, interasse, tempi, portata |
| `Abaco_Efficienza_n4` | ✅ | Abaco di efficienza idraulica per n = 4 |
| `Abaco_Efficienza_n2,5` | ✅ | Abaco di efficienza idraulica per n = 2.5 |
| `Abaco_Efficienza_n1,5` | ✅ | Abaco di efficienza idraulica per n = 1.5 |
| `Abaco_Efficienza_n1` | ✅ | Abaco di efficienza idraulica per n = 1 |
| `Abaco_Tempi_T90-n1` | ✅ | Abaco dei tempi caratteristici T90 per n = 1 |
| `Abaco_Tempi_T90-n2,5` | ✅ | Abaco dei tempi caratteristici T90 per n = 2.5 |
| `Abaco_Tempi_T50-n1` | ✅ | Abaco dei tempi caratteristici T50 per n = 1 |
| `Abaco_Tempi_T50-n2,5` | ✅ | Abaco dei tempi caratteristici T50 per n = 2.5 |
| `Abaco_Portata` | ✅ | Abaco del fattore di portata adimensionale q |
| `DB_Abachi` | 🔒 nascosto | Database delle coordinate digitalizzate dagli abachi originali (Desideri et al., 1997) |

---

## 🧮 Metodo di calcolo

Il metodo si basa sui parametri adimensionali:

$$n = \frac{H}{H_0} \qquad d = \frac{D}{H_0}$$

dove **H** è la profondità dello strato impermeabile, **H₀** la profondità della trincea e **D** la profondità della superficie di scorrimento.

La procedura di verifica si articola in sei passi sequenziali:

1. **F(Z)** — calcolo del coefficiente di sicurezza lungo la profondità nelle tre condizioni di falda (iniziale, satura, asciutta)
2. **Obiettivi progettuali** — definizione di F_target, F_short e orizzonte temporale
3. **Efficienza richiesta** — quota del margine massimo disponibile necessaria per raggiungere F_target:

$$E_{\text{richiesta}} = \frac{F_{\text{target}} - F_0}{F_{\text{max}} - F_0}$$

4. **Interasse** — lettura dell'abaco di efficienza e scelta di S compatibile con E richiesta
5. **Tempi** — calcolo di T50 e T90 e verifica che F_short sia raggiunto entro l'orizzonte di breve termine
6. **Portata** — stima della portata drenata per metro di trincea e per ramo

---

## 🛠️ Funzioni VBA disponibili

Le funzioni VBA sono richiamabili direttamente dalle celle, senza macro o pulsanti.

Il repository offre due percorsi:

- **Uso immediato** — scaricare `Trincee_Drenanti_v1_0.xlsm`, il modulo è già importato e pronto all'uso.
- **Uso consapevole** — leggere prima il codice sorgente in `ModuloTrincee_v1_0.bas`, poi importarlo manualmente nel file `.xlsx`:
  1. Aprire Excel e premere `Alt + F11`
  2. Dal menu: *File → Importa file...*
  3. Selezionare `ModuloTrincee_v1_0.bas`
  4. Salvare il file come `.xlsm` per mantenere le macro attive

| Funzione | Descrizione |
|---|---|
| `GetFZ(phi, c, gamma, beta, hw, h)` | Restituisce il coefficiente di sicurezza F in forma chiusa |
| `GetEfficienza(n, d, SuH0)` | Restituisce l'efficienza idraulica media E interpolata dagli abachi |
| `GetSuH0(n, d, E)` | Restituisce il rapporto S/H₀ massimo compatibile con l'efficienza richiesta |
| `GetT(n, d, SuH0, grado)` | Restituisce il fattore di tempo T adimensionale (T50 o T90) |
| `GetQadim(n, d, SuH0)` | Restituisce il fattore di portata adimensionale q |

---

## 📐 Campi di validità

| Parametro | Valori disponibili |
|---|---|
| n = H/H₀ | 1 — 1.5 — 2.5 — 4 |
| d = D/H₀ | 0.5 — 1 — 1.5 — 2 |
| S/H₀ | 0.5 – 4 (intervallo degli abachi) |

Valori fuori intervallo restituiscono `#N/A`. Per coppie (n, d) non coincidenti con i punti discreti disponibili, si raccomanda di scegliere la combinazione più prossima in senso conservativo.

---

## 💻 Requisiti

- Microsoft Excel (versione 2016 o successiva consigliata)
- Testato su Excel 365 (italiano) — alcune formule usano la sintassi italiana
  (es. `NON.DISP()` al posto di `NA()`)

---

## ⚠️ Avvertenze

I dati, le curve e i parametri contenuti in questo strumento sono stati digitalizzati e implementati con la massima attenzione e accuratezza, ma senza alcuna garanzia di completezza, correttezza o idoneità a specifici scopi progettuali. Il foglio di calcolo è uno strumento di supporto alla progettazione e non sostituisce il giudizio professionale del progettista, né la verifica critica dei risultati alla luce del contesto geologico e geotecnico specifico.

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

- Desideri A., Miliziano S., Rampello S. — *Drenaggi a gravità per la stabilizzazione dei pendii*, Argomenti di Ingegneria Geotecnica, Hevelius Edizioni, Benevento, 1997 — [PDF](https://www.ordineingegnerilecce.it/wp-content/uploads/2021/06/DRENAGGIweb-1.pdf)

---

*Sviluppato da [Francisco J. Méndez](https://franciscojmendez.com)*
