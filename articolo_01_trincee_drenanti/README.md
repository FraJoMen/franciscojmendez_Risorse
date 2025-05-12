# Articolo 1 – Dimensionamento di Massima delle Trincee Drenanti

Questo progetto contiene il materiale di supporto all’articolo:

📄 **Dimensionamento di Massima delle Trincee Drenanti**  
👉 [Leggi l’articolo completo sul sito](https://www.franciscojmendez.com/trincee-drenanti-dimensionamento-massima/)

---

## 📖 Contenuti

Questa repository contiene una raccolta completa di strumenti ed esempi per il **dimensionamento idraulico delle trincee drenanti**, basati su abachi numerici e simulazioni teoriche. 

### File principali

- `libreria_trincee.py` → **libreria Python modulare**, contenente le `classi`:
  - `Pendio`: per la valutazione del coefficiente di sicurezza $F(Z)$;
  - `AbachiEfficienza`: per l’interrogazione degli abachi statici di efficienza idraulica media;
  - `AbachiTemporali`: per l’interpolazione dei tempi caratteristici $T_{50}$ e $T_{90}$;
  - `AbacoPortate`: per il calcolo della portata drenata da ciascuna trincea.
- `uso_funzioni_libreria_trincee.ipynb` → notebook di **esplorazione e uso guidato** delle funzioni disponibili nella libreria  `libreria_trincee.py`, con esempi sintetici e visualizzazioni interattive.
- `esempio_progetto.ipynb` → notebook che rappresenta un **caso studio completo**, con dati progettuali reali, verifiche, grafici e stime ingegneristiche commentate passo passo.

Tutti i dati di input sono forniti direttamente nei notebook, rendendo l'esecuzione immediata e **indipendente da file esterni**


### 📁 Cartella `data`

La cartella `data/` contiene le risorse tecniche fondamentali utilizzate per la costruzione della libreria `libreria_trincee.py`:

- le immagini originali dei grafici tratti dalla letteratura scientifica, usati come riferimento;
- i dati numerici degli abachi, suddivisi per tipo e parametro, in formato CSV;
- file html con grafici Plotly esportati in HTML per consultazione interattiva offline.


---

## 🧠 Obiettivo

Il progetto implementa un approccio semplificato per valutare l’efficienza idraulica delle trincee drenanti, basato sugli abachi derivati da simulazioni numeriche condotte in condizioni semplificate.

Sono considerati:

- parametri adimensionali S/H₀, B/H₀, H/H₀;
- l’efficienza idraulica media e puntuale;
- la relazione tra incremento di stabilità e dissipazione della pressione interstiziale.

---

## 🛠️ Esempio di utilizzo

Il notebook `esempio_progetto.ipynb` mostra come:
- studiare la stabilità del versante;
- calcolare l’efficienza idraulica in linea con gli obiettivi progettuale;
- valutare gli effetti dell'opera di drenaggio;
- visualizzare i risultati con grafici e formule.

👉 Il notebook può essere **eseguito e modificato liberamente**, ed eventualmente **esportato in Html/ PDF** per essere allegato a relazioni tecniche, report o documentazione di progetto.

---

## 📥 Dipendenze

Per eseguire il codice, sono necessarie le seguenti librerie Python:

*   numpy
*   plotly
*   scipy
*   matplotlib

Si raccomanda di **installare la distribuzione Anaconda**, per accedere a queste ed altre librerie dedicate al calcolo numerico.  
👉 [Link per Anaconda](https://www.anaconda.com/products/individual)

---

## 💬 Contribuisci o commenta

Puoi:

- aprire una **issue** su GitHub per suggerire modifiche;
- **commentare l’articolo** direttamente sul sito;
- usare il [modulo contatti](https://franciscojmendez.it/contatti/) per dubbi o osservazioni.

---

## 📜 Licenza

Questo progetto è distribuito con licenza **GNU GPL v3**.  
Chiunque può usarlo, modificarlo e redistribuirlo, purché mantenga la stessa licenza.

---

## 📚  Bibliografia
Le formulazioni e gli abachi implementati derivano dai seguenti contributi tecnici e scientifici:


1. **Desideri A., Miliziano S., Rampello S. (1997).** *Drenaggi a gravità per la stabilizzazione dei pendii*. Argomenti di Ingegneria Geotecnica, Hevelius Edizioni, Benevento. [Link al documento PDF](https://www.ordineingegnerilecce.it/wp-content/uploads/2021/06/DRENAGGIweb-1.pdf)
2. **Ordine dei Geologi della Sardegna (s.d.).** *La progettazione delle trincee drenanti per la stabilizzazione dei pendii*. Miscellanea Sarda. [Link al documento PDF](https://www.geologi.sardegna.it/fileadmin/ORGS/Miscellanea_Sarda/La_progettazione_delle_trincee_drenanti_per_la_stabilizzazione_dei_pendii.pdf)
3. **Elzoghby M.M., Jia Z., Luo W. (2021).** *Experimental study on the hydraulic performance of nonwoven geotextile as subsurface drain filter in a silty loam area.* Journal of Rock Mechanics and Geotechnical Engineering, 13(6), 1405–1418. [Link all’articolo](https://www.sciencedirect.com/science/article/pii/S2090447921001660?via%3Dihub)
