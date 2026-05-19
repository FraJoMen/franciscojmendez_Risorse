Attribute VB_Name = "ModuloBustamanteDoix"
Option Explicit

' =============================================================================
' MODULO: ModuloBustamanteDoix
' Versione: 1.0
' Autore:   Francisco José Mendez  –  www.franciscojmendez.com
' Articolo: [LINK]
'
' Fonte scientifica:
'   Bustamante M., Doix B. (1985).
'   "Une methode pour le calcul des tirants et des micropieux injectes."
'   Bulletin de Liaison des Laboratoires des Ponts et Chaussees, Paris.
'
' Descrizione:
'   Libreria VBA per il calcolo della portata laterale dei micropali iniettati
'   secondo il metodo Bustamante-Doix. Le funzioni leggono i dati degli abachi
'   dal foglio DB_Abachi del file Excel allegato e restituiscono i parametri
'   di calcolo necessari per la verifica a SLU secondo NTC 2018 (par. 6.4.3).
'
'   Il modulo puo essere importato in qualsiasi cartella di lavoro Excel
'   (.xlsm) tramite l'Editor VBA (Alt+F11 > File > Importa file).
'   Il foglio DB_Abachi deve essere presente nella stessa cartella di lavoro.
'
' Funzioni pubbliche:
'   GetQs(tipoTerreno, curva, pl_MPa)            -> qs [MPa]
'   GetAlpha(tipoTerreno, tipoIniezione)          -> alpha [-]
'   GetVi_min(tipoTerreno, tipoIniezione, Vs_m3) -> Vi,min [m3]
'   GetPl_fromNSPT(tipoTerreno, nspt)            -> pl [MPa]
'
' Licenza: GNU General Public License v3.0
'   Uso libero per scopi didattici e professionali.
'   In caso di modifica o redistribuzione mantenere i riferimenti agli autori
'   e alla fonte scientifica originale.
'   Testo completo: https://www.gnu.org/licenses/gpl-3.0.it.html
' -----------------------------------------------------------------------------
' ⚠AVVERTENZA !!!
' Questo modulo e distribuito nella speranza che possa essere utile,
' ma SENZA ALCUNA GARANZIA. La responsabilita della verifica e della
' validazione dei risultati rimane in capo al professionista che li utilizza.
' =============================================================================

' =============================================================================
' RANGE DI VALIDITA degli abachi (pl in MPa)
' Fuori range -> GetQs restituisce errore #N/A
'   SG: 0.25 - 7.0
'   AL: 0.25 - 2.5
'   MC: 1.00 - 8.0
'   RA: 1.40 - 8.2
' =============================================================================
Private Function PL_Min(abaco As String) As Double
    Select Case UCase(Trim(abaco))
        Case "SG": PL_Min = 0.25
        Case "AL": PL_Min = 0.25
        Case "MC": PL_Min = 1.00
        Case "RA": PL_Min = 1.40
        Case Else: PL_Min = 0
    End Select
End Function

Private Function PL_Max(abaco As String) As Double
    Select Case UCase(Trim(abaco))
        Case "SG": PL_Max = 7.0
        Case "AL": PL_Max = 2.5
        Case "MC": PL_Max = 8.0
        Case "RA": PL_Max = 8.2
        Case Else: PL_Max = 0
    End Select
End Function


' =============================================================================
' GetQs  -  Restituisce q_s [MPa] dalle curve di Bustamante-Doix
'
' Argomenti:
'   tipoTerreno As String : "SG", "AL", "MC", "RA"
'   curva       As String : "IRS" oppure "IGU"
'   pl_MPa      As Double : pressione limite pressiometrica [MPa]
'
' Logica:
'   - Controlla che pl sia nel range di validita dell abaco
'   - AL: curva potenza  qs = a * pl^b  (parametri hardcoded, R2>0.996)
'   - SG, MC, RA: interpolazione lineare sui punti del foglio DB_Abachi
'
' Errori restituiti:
'   #N/A  -> pl fuori range, abaco non riconosciuto, dati DB insufficienti
'   #VAL! -> errore generico
' =============================================================================
Function GetQs(tipoTerreno As String, curva As String, pl_MPa As Double) As Double

    Dim abc As String
    abc = UCase(Trim(tipoTerreno))

    On Error GoTo ErrHandler

    ' Controllo input
    If pl_MPa <= 0 Then
        GetQs = 0
        Exit Function
    End If

    ' Controllo range di validita
    If PL_Max(abc) = 0 Then
        ' Abaco non riconosciuto
        GetQs = CVErr(xlErrNA)
        Exit Function
    End If

    If pl_MPa < PL_Min(abc) Or pl_MPa > PL_Max(abc) Then
        ' pl fuori range: calcolo invalidato
        GetQs = CVErr(xlErrNA)
        Exit Function
    End If

    ' Calcolo qs
    Select Case abc
        Case "AL"
            GetQs = GetQs_Power(curva, pl_MPa)
        Case "SG", "MC", "RA"
            GetQs = GetQs_Interp(abc, curva, pl_MPa)
        Case Else
            GetQs = CVErr(xlErrNA)
    End Select

    Exit Function
ErrHandler:
    GetQs = CVErr(xlErrValue)
End Function


' =============================================================================
' GetQs_Power  -  Curva potenza qs = a * pl^b  (solo abaco AL)
'
' Coefficienti calibrati su punti vettorializzati da Bustamante-Doix (1985):
'   IRS:  a = 0.175425   b = 0.610302   R2 = 0.9966
'   IGU:  a = 0.099367   b = 0.617494   R2 = 0.9981
' =============================================================================
Private Function GetQs_Power(curva As String, pl_MPa As Double) As Double

    Dim a As Double, b As Double

    On Error GoTo ErrHandler

    Select Case UCase(Trim(curva))
        Case "IRS": a = 0.175425: b = 0.610302
        Case "IGU": a = 0.099367: b = 0.617494
        Case Else
            GetQs_Power = CVErr(xlErrNA)
            Exit Function
    End Select

    GetQs_Power = a * (pl_MPa ^ b)

    Exit Function
ErrHandler:
    GetQs_Power = CVErr(xlErrValue)
End Function


' =============================================================================
' GetQs_Interp  -  Interpolazione lineare su DB_Abachi (SG, MC, RA)
' =============================================================================
Private Function GetQs_Interp(abaco As String, curva As String, _
                               pl_MPa As Double) As Double

    Dim ws   As Worksheet
    Dim last As Long, i As Long, j As Long, n As Long
    Dim pl() As Double, qs() As Double, tmp As Double

    On Error GoTo ErrHandler

    Set ws = ThisWorkbook.Sheets("DB_Abachi")
    last   = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    n      = 0
    ReDim pl(1 To last), qs(1 To last)

    For i = 2 To last
        If UCase(Trim(ws.Cells(i,1).Value)) = UCase(Trim(abaco)) And _
           UCase(Trim(ws.Cells(i,2).Value)) = UCase(Trim(curva)) Then
            If IsNumeric(ws.Cells(i,3).Value) And _
               IsNumeric(ws.Cells(i,4).Value) Then
                n = n + 1
                pl(n) = CDbl(ws.Cells(i,3).Value)
                qs(n) = CDbl(ws.Cells(i,4).Value)
            End If
        End If
    Next i

    If n < 2 Then
        GetQs_Interp = CVErr(xlErrNA)
        Exit Function
    End If

    ' Bubble sort per pl crescente
    For i = 1 To n - 1
        For j = 1 To n - i
            If pl(j) > pl(j+1) Then
                tmp=pl(j): pl(j)=pl(j+1): pl(j+1)=tmp
                tmp=qs(j): qs(j)=qs(j+1): qs(j+1)=tmp
            End If
        Next j
    Next i

    ' Interpolazione lineare interna
    ' (range gia controllato in GetQs, qui siamo sicuramente dentro)
    For i = 1 To n - 1
        If pl_MPa >= pl(i) And pl_MPa <= pl(i+1) Then
            GetQs_Interp = qs(i) + (pl_MPa - pl(i)) * _
                           (qs(i+1) - qs(i)) / (pl(i+1) - pl(i))
            Exit Function
        End If
    Next i

    ' Fallback estremi (non dovrebbe mai arrivare qui dopo il check range)
    If pl_MPa <= pl(1) Then
        GetQs_Interp = qs(1)
    ElseIf pl_MPa >= pl(n) Then
        GetQs_Interp = qs(n)
    Else
        GetQs_Interp = CVErr(xlErrNA)
    End If

    Exit Function
ErrHandler:
    GetQs_Interp = CVErr(xlErrValue)
End Function


' =============================================================================
' GetAlpha  -  Coefficiente di sbulbatura suggerito (Bustamante-Doix, Tab. 1)
'
' Argomenti:
'   tipoTerreno    As String : "SG", "AL", "MC", "RA"
'   tipoIniezione  As String : "IRS" oppure "IGU"
'
' Restituisce il valore medio dell intervallo consigliato da Bustamante-Doix.
' L utente puo sovrascriverlo nella colonna "alpha usato" di DATI_INPUT.
'
' Valori (da Tabella 1 Bustamante-Doix 1985):
'   SG:  IRS=1.80  IGU=1.35
'   AL:  IRS=1.70  IGU=1.15
'   MC:  IRS=1.80  IGU=1.15
'   RA:  IRS=1.20  IGU=1.10
' =============================================================================
Function GetAlpha(tipoTerreno As String, tipoIniezione As String) As Double

    On Error GoTo ErrHandler

    Dim abc As String, inj As String
    abc = UCase(Trim(tipoTerreno))
    inj = UCase(Trim(tipoIniezione))

    Select Case abc
        Case "SG"
            If inj = "IRS" Then GetAlpha = 1.80 Else GetAlpha = 1.35
        Case "AL"
            If inj = "IRS" Then GetAlpha = 1.70 Else GetAlpha = 1.15
        Case "MC"
            If inj = "IRS" Then GetAlpha = 1.80 Else GetAlpha = 1.15
        Case "RA"
            If inj = "IRS" Then GetAlpha = 1.20 Else GetAlpha = 1.10
        Case Else
            GetAlpha = CVErr(xlErrNA)
    End Select

    Exit Function
ErrHandler:
    GetAlpha = CVErr(xlErrValue)
End Function


' =============================================================================
' GetVi_min  -  Volume minimo di iniezione consigliato (Bustamante-Doix, Tab. 1)
'
' Argomenti:
'   tipoTerreno    As String : "SG", "AL", "MC", "RA"
'   tipoIniezione  As String : "IRS" oppure "IGU"
'   Vs_m3          As Double : volume teorico del bulbo [m3] = pi*Ds^2/4*ls
'
' Restituisce Vi,min = k * Vs  [m3]
'
' Coefficienti k (da Tabella 1 Bustamante-Doix 1985):
'   SG:  IRS=1.50  IGU=1.50
'   AL:  IRS=2.00  IGU=1.50
'   MC:  IRS=1.75  IGU=1.50
'   RA:  IRS=1.30  IGU=1.30
' =============================================================================
Function GetVi_min(tipoTerreno As String, tipoIniezione As String, _
                   Vs_m3 As Double) As Double

    On Error GoTo ErrHandler

    Dim abc As String, inj As String, k As Double
    abc = UCase(Trim(tipoTerreno))
    inj = UCase(Trim(tipoIniezione))

    Select Case abc
        Case "SG": k = 1.50   ' uguale per IRS e IGU
        Case "AL"
            If inj = "IRS" Then k = 2.00 Else k = 1.50
        Case "MC"
            If inj = "IRS" Then k = 1.75 Else k = 1.50
        Case "RA": k = 1.30   ' uguale per IRS e IGU
        Case Else
            GetVi_min = CVErr(xlErrNA)
            Exit Function
    End Select

    If Vs_m3 <= 0 Then
        GetVi_min = 0
    Else
        GetVi_min = k * Vs_m3
    End If

    Exit Function
ErrHandler:
    GetVi_min = CVErr(xlErrValue)
End Function


' =============================================================================
' GetPl_fromNSPT  -  Converte N_SPT in p_l [MPa]
'
' Argomenti:
'   tipoTerreno As String : "SG", "AL", "MC"
'                           NOTA: "RA" non supportato (restituisce errore).
'                           Per rocce alterate e richiesta la prova
'                           pressiometrica diretta o stima da UCS/RQD.
'   nspt        As Double : numero di colpi SPT
'
' Correlazioni indicative (Bustamante-Doix + letteratura):
'   SG (sabbie e ghiaie)  : pl = 0.0500 * N  [MPa]
'   AL (argille e limi)   : pl = 0.0667 * N  [MPa]
'   MC (marne e calcari)  : pl = 0.0500 * N  [MPa]
'   RA                    : #N/A  (non applicabile)
'
' NOTA: preferire sempre p_l da prova pressiometrica diretta.
'       Queste correlazioni sono indicative e soggette ad ampia dispersione.
' =============================================================================
Function GetPl_fromNSPT(tipoTerreno As String, nspt As Double) As Double

    On Error GoTo ErrHandler

    If nspt <= 0 Then
        GetPl_fromNSPT = 0
        Exit Function
    End If

    Select Case UCase(Trim(tipoTerreno))
        Case "SG": GetPl_fromNSPT = 0.0500 * nspt
        Case "AL": GetPl_fromNSPT = 0.0667 * nspt
        Case "MC": GetPl_fromNSPT = 0.0500 * nspt
        Case "RA"
            ' Non applicabile: la prova SPT non e affidabile
            ' per rocce alterate. Inserire p_l direttamente.
            GetPl_fromNSPT = CVErr(xlErrNA)
        Case Else
            GetPl_fromNSPT = CVErr(xlErrNA)
    End Select

    Exit Function
ErrHandler:
    GetPl_fromNSPT = CVErr(xlErrValue)
End Function
