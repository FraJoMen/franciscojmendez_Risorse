Attribute VB_Name = "ModuloTrincee"
Option Explicit

' =============================================================================
' MODULO: ModuloTrincee
' Versione: 1.0
' Autore:   Francisco Jose Mendez  -  www.franciscojmendez.com
' Articolo: https://www.franciscojmendez.com/trincee-drenanti-dimensionamento-massima/
'
' Descrizione:
'   Libreria VBA per il dimensionamento di massima delle trincee drenanti
'   (metodo Desideri, Miliziano, Rampello, 1997).
'   GetFZ calcola il coefficiente di sicurezza F(Z) in forma chiusa.
'   Le altre UDF valutano gli abachi (efficienza idraulica, tempi
'   caratteristici T50/T90, fattore di portata) da coefficienti di
'   regressione, in modo identico a "libreria_trincee.py": polinomi
'   (valutati con l'algoritmo di Horner) per efficienza e portata,
'   B-spline cubiche di regressione (valutate con l'algoritmo di
'   De Boor) per i tempi caratteristici T50/T90.
'
' Funzioni pubbliche:
'   GetFZ(Z, dw, c', phi', gamma, gammaw, beta)  -> coeff. sicurezza F(Z) [-]
'   GetEfficienza(n, d, SuH0)        -> efficienza E [-]
'   GetSuH0(n, d, Etarget)           -> rapporto S/H0 [-] (inversa, per bisezione)
'   GetT(tipo, n, d, SuH0)           -> T50 o T90 adimensionale [-]
'   GetQadim(s)                      -> fattore di portata q [-]
'   ConfigValida(tipo, n, d)         -> True se la configurazione esiste
'   GetAbacoXRange(tipo, n, d)       -> testo "min - max" del campo x valido
'   GetAbacoYRange(tipo, n, d)       -> testo "min - max" del campo y valido
'
' Fuori dal campo di validita' dell'abaco -> #N/A (nessuna estrapolazione).
'
' Licenza: GNU General Public License v3.0
' -----------------------------------------------------------------------------
' AVVERTENZA: distribuito SENZA ALCUNA GARANZIA. La verifica e la validazione
' dei risultati restano in capo al professionista che li utilizza.
' =============================================================================

Private Const TOL As Double = 0.0001        ' tolleranza confronto n, d

' =============================================================================
' UDF PUBBLICHE
' =============================================================================

Public Function GetFZ(ByVal Z As Double, ByVal dw As Double, _
                      ByVal cEff As Double, ByVal phiEff As Double, _
                      ByVal gamma As Double, ByVal gammaw As Double, _
                      ByVal beta As Double) As Variant
    ' Coefficiente di sicurezza del pendio infinito a profondita' Z, falda a profondita' dw.
    ' Algebra pura: nessuna interpolazione, nessuna lettura da foglio.
    On Error GoTo ErrHandler
    If Z <= 0 Or gamma <= 0 Then GetFZ = CVErr(xlErrNA): Exit Function

    Dim pi180 As Double: pi180 = 3.14159265358979 / 180#
    Dim cb As Double, sB As Double
    cb = Cos(beta * pi180)
    sB = Sin(beta * pi180)

    Dim u0 As Double
    If Z > dw Then u0 = gammaw * (Z - dw) * cb ^ 2 Else u0 = 0#

    Dim sigma As Double, tau As Double
    sigma = gamma * Z * cb ^ 2
    tau = gamma * Z * cb * sB
    If tau = 0 Then GetFZ = CVErr(xlErrNA): Exit Function

    GetFZ = (cEff + (sigma - u0) * Tan(phiEff * pi180)) / tau
    Exit Function
ErrHandler:
    GetFZ = CVErr(xlErrValue)
End Function

Public Function GetEfficienza(ByVal nVal As Double, ByVal dVal As Double, _
                              ByVal SuH0 As Double) As Variant
    On Error GoTo ErrHandler
    Dim coef As Variant, xMin As Double, xMax As Double
    If Not EffLookup(nVal, dVal, coef, xMin, xMax) Then
        GetEfficienza = CVErr(xlErrNA): Exit Function
    End If
    If SuH0 < xMin Or SuH0 > xMax Then
        GetEfficienza = CVErr(xlErrNA): Exit Function
    End If
    GetEfficienza = EvalPoly(coef, SuH0)
    Exit Function
ErrHandler:
    GetEfficienza = CVErr(xlErrValue)
End Function

Public Function GetT(ByVal tipo As String, ByVal nVal As Double, ByVal dVal As Double, _
                     ByVal SuH0 As Double) As Variant
    On Error GoTo ErrHandler
    Dim tp As String
    tp = UCase(Trim(tipo))
    If tp <> "T50" And tp <> "T90" Then
        GetT = CVErr(xlErrNA): Exit Function
    End If

    Dim knots As Variant, coef As Variant, xMin As Double, xMax As Double
    If Not TLookup(tp, nVal, dVal, knots, coef, xMin, xMax) Then
        GetT = CVErr(xlErrNA): Exit Function
    End If
    If SuH0 < xMin Or SuH0 > xMax Then
        GetT = CVErr(xlErrNA): Exit Function
    End If

    Dim logT As Double
    logT = EvalBSpline(knots, coef, 3, SuH0)
    GetT = 10# ^ logT
    Exit Function
ErrHandler:
    GetT = CVErr(xlErrValue)
End Function

Public Function GetQadim(ByVal s As Double) As Variant
    On Error GoTo ErrHandler
    Const S_MIN As Double = 0#
    Const S_MAX As Double = 4.899
    If s < S_MIN Or s > S_MAX Then
        GetQadim = CVErr(xlErrNA): Exit Function
    End If
    Dim coef(6) As Double
    coef(0) = -0.00052235: coef(1) = 0.0144176: coef(2) = -0.14951922
    coef(3) = 0.76637241: coef(4) = -2.07136723: coef(5) = 2.81031175
    coef(6) = -0.02558556
    GetQadim = EvalPoly(coef, s)
    Exit Function
ErrHandler:
    GetQadim = CVErr(xlErrValue)
End Function

Public Function ConfigValida(ByVal tipo As String, ByVal nVal As Double, _
                             ByVal dVal As Double) As Boolean
    Dim tp As String: tp = UCase(Trim(tipo))
    Dim xMin As Double, xMax As Double

    If tp = "EFF" Then
        Dim coefE As Variant
        ConfigValida = EffLookup(nVal, dVal, coefE, xMin, xMax)
    ElseIf tp = "T50" Or tp = "T90" Then
        Dim k As Variant, c As Variant
        ConfigValida = TLookup(tp, nVal, dVal, k, c, xMin, xMax)
    ElseIf tp = "Q" Then
        ConfigValida = True
    Else
        ConfigValida = False
    End If
End Function

Public Function GetSuH0(ByVal nVal As Double, ByVal dVal As Double, _
                        ByVal Etarget As Double) As Variant
    ' Inversa dell'abaco di efficienza: trova S/H0 tale che E(S/H0) = Etarget,
    ' per bisezione (efficienza decrescente al crescere di S/H0).
    On Error GoTo ErrHandler
    Dim coef As Variant, xLo As Double, xHi As Double
    If Not EffLookup(nVal, dVal, coef, xLo, xHi) Then
        GetSuH0 = CVErr(xlErrNA): Exit Function
    End If

    Dim yLo As Double, yHi As Double
    If Not EffYRange(nVal, dVal, yLo, yHi) Then
        GetSuH0 = CVErr(xlErrNA): Exit Function
    End If
    If Etarget > yHi + TOL Or Etarget < yLo - TOL Then
        GetSuH0 = CVErr(xlErrNA): Exit Function
    End If

    Dim a As Double, b As Double, mid As Double, fm As Double
    Dim it As Long
    a = xLo: b = xHi
    For it = 1 To 200
        mid = 0.5 * (a + b)
        fm = EvalPoly(coef, mid)
        If (fm - Etarget) > 0# Then
            a = mid                ' efficienza ancora troppo alta -> aumenta S/H0
        Else
            b = mid
        End If
        If (b - a) < 0.0000001 Then Exit For
    Next it
    GetSuH0 = 0.5 * (a + b)
    Exit Function
ErrHandler:
    GetSuH0 = CVErr(xlErrValue)
End Function

Public Function GetAbacoXRange(ByVal tipo As String, ByVal nVal As Double, _
                               ByVal dVal As Double) As Variant
    On Error GoTo ErrHandler
    Dim tp As String: tp = UCase(Trim(tipo))
    Dim xMin As Double, xMax As Double

    If tp = "EFF" Then
        Dim coefE As Variant
        If Not EffLookup(nVal, dVal, coefE, xMin, xMax) Then
            GetAbacoXRange = CVErr(xlErrNA): Exit Function
        End If
    ElseIf tp = "T50" Or tp = "T90" Then
        Dim k As Variant, c As Variant
        If Not TLookup(tp, nVal, dVal, k, c, xMin, xMax) Then
            GetAbacoXRange = CVErr(xlErrNA): Exit Function
        End If
    ElseIf tp = "Q" Then
        xMin = 0#: xMax = 4.899
    Else
        GetAbacoXRange = CVErr(xlErrNA): Exit Function
    End If
    GetAbacoXRange = Format(xMin, "0.000") & " - " & Format(xMax, "0.000")
    Exit Function
ErrHandler:
    GetAbacoXRange = CVErr(xlErrValue)
End Function

Public Function GetAbacoYRange(ByVal tipo As String, ByVal nVal As Double, _
                               ByVal dVal As Double) As Variant
    On Error GoTo ErrHandler
    Dim tp As String: tp = UCase(Trim(tipo))
    Dim yMin As Double, yMax As Double

    If tp = "EFF" Then
        If Not EffYRange(nVal, dVal, yMin, yMax) Then
            GetAbacoYRange = CVErr(xlErrNA): Exit Function
        End If
    ElseIf tp = "T50" Or tp = "T90" Then
        If Not TYRange(tp, nVal, dVal, yMin, yMax) Then
            GetAbacoYRange = CVErr(xlErrNA): Exit Function
        End If
    Else
        GetAbacoYRange = CVErr(xlErrNA): Exit Function
    End If
    GetAbacoYRange = Format(yMin, "0.000") & " - " & Format(yMax, "0.000")
    Exit Function
ErrHandler:
    GetAbacoYRange = CVErr(xlErrValue)
End Function

' =============================================================================
' DATI: coefficienti di regressione (da fit_abachi_lineari.py / fit_piecewise.py)
' =============================================================================

Private Function EffLookup(ByVal nVal As Double, ByVal dVal As Double, _
                           ByRef coef As Variant, ByRef xMin As Double, _
                           ByRef xMax As Double) As Boolean
    ' Coefficienti ordinati da grado massimo a grado 0 (convenzione numpy.polyfit).
    EffLookup = True

    If Abs(nVal - 1#) < TOL And Abs(dVal - 0.5) < TOL Then
        coef = Array(0.00121912, -0.0225045, 0.15478454, -0.45999063, 0.36069463, 0.9133623)
        xMin = 0.537: xMax = 5.979
    ElseIf Abs(nVal - 1#) < TOL And Abs(dVal - 1#) < TOL Then
        coef = Array(-0.00218553, 0.04721918, -0.35540193, 1.1150014)
        xMin = 0.514: xMax = 5.991
    ElseIf Abs(nVal - 1.5) < TOL And Abs(dVal - 0.5) < TOL Then
        coef = Array(-0.00196047, 0.02895013, -0.13095397, 0.05190368, 1.00916626)
        xMin = 0.503: xMax = 5.982
    ElseIf Abs(nVal - 1.5) < TOL And Abs(dVal - 1#) < TOL Then
        coef = Array(0.00044378, 0.01254924, -0.22434232, 1.07909332)
        xMin = 0.506: xMax = 5.977
    ElseIf Abs(nVal - 1.5) < TOL And Abs(dVal - 1.5) < TOL Then
        coef = Array(0.00019433, 0.00942158, -0.153361, 0.72345807)
        xMin = 0.504: xMax = 5.974
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 0.5) < TOL Then
        coef = Array(-0.00205685, 0.02941543, -0.1286618, 0.04468809, 1.01812512)
        xMin = 0.635: xMax = 5.932
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 1#) < TOL Then
        coef = Array(-0.00011242, 0.01817626, -0.23493448, 1.08665247)
        xMin = 0.509: xMax = 5.906
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 1.5) < TOL Then
        coef = Array(-0.00034503, 0.01460161, -0.16243576, 0.72637179)
        xMin = 0.498: xMax = 5.918
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 2#) < TOL Then
        coef = Array(-0.00007626, 0.00904423, -0.11626783, 0.54137795)
        xMin = 0.499: xMax = 5.895
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 0.5) < TOL Then
        coef = Array(0.00084181, -0.01549314, 0.1075386, -0.32943443, 0.26444043, 0.9346052)
        xMin = 0.606: xMax = 5.932
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 1#) < TOL Then
        coef = Array(-0.0002993, 0.01969709, -0.23694088, 1.08244593)
        xMin = 0.5: xMax = 5.971
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 1.5) < TOL Then
        coef = Array(-0.00018186, 0.01314575, -0.1593736, 0.72563318)
        xMin = 0.504: xMax = 5.946
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 2#) < TOL Then
        coef = Array(0.00001497, 0.00833845, -0.11518106, 0.54051694)
        xMin = 0.486: xMax = 5.969
    Else
        EffLookup = False
    End If
End Function

Private Function EffYRange(ByVal nVal As Double, ByVal dVal As Double, _
                           ByRef yMin As Double, ByRef yMax As Double) As Boolean
    ' Min/max REALI della curva (campionati), non il valore agli estremi:
    ' piu' robusto per la guardia di GetSuH0 su curve quasi monotone con
    ' lieve rumore in coda.
    EffYRange = True

    If Abs(nVal - 1#) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.264889: yMax = 0.99656
    ElseIf Abs(nVal - 1#) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.21063: yMax = 0.944503
    ElseIf Abs(nVal - 1.5) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.320256: yMax = 1.0057
    ElseIf Abs(nVal - 1.5) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.281273: yMax = 0.968847
    ElseIf Abs(nVal - 1.5) < TOL And Abs(dVal - 1.5) < TOL Then
        yMin = 0.184955: yMax = 0.648582
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.349056: yMax = 1.00182
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.309973: yMax = 0.971765
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 1.5) < TOL Then
        yMin = 0.204953: yMax = 0.649057
    ElseIf Abs(nVal - 2.5) < TOL And Abs(dVal - 2#) < TOL Then
        yMin = 0.154653: yMax = 0.485603
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.357491: yMax = 0.995787
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.306213: yMax = 0.968862
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 1.5) < TOL Then
        yMin = 0.204534: yMax = 0.648625
    ElseIf Abs(nVal - 4#) < TOL And Abs(dVal - 2#) < TOL Then
        yMin = 0.153275: yMax = 0.48651
    Else
        EffYRange = False
    End If
End Function

Private Function TLookup(ByVal tipo As String, ByVal nVal As Double, ByVal dVal As Double, _
                         ByRef knots As Variant, ByRef coef As Variant, _
                         ByRef xMin As Double, ByRef xMax As Double) As Boolean
    ' knots = vettore di nodi COMPLETO (bordi ripetuti k+1=4 volte + nodi interni).
    ' coef  = coefficienti di controllo della B-spline cubica (log10(T)).
    TLookup = True

    If tipo = "T50" And Abs(nVal - 1#) < TOL And Abs(dVal - 0.5) < TOL Then
        xMin = 0.487: xMax = 6.003
        knots = Array(xMin, xMin, xMin, xMin, 1.036103, 3.309614, xMax, xMax, xMax, xMax)
        coef = Array(-2.76089534, -1.81403305, -0.6822056, -0.62888476, -0.662216, -0.65872688)
    ElseIf tipo = "T50" And Abs(nVal - 1#) < TOL And Abs(dVal - 1#) < TOL Then
        xMin = 0.484: xMax = 6#
        knots = Array(xMin, xMin, xMin, xMin, 0.792061, 2.721681, xMax, xMax, xMax, xMax)
        coef = Array(-2.69648223, -1.84144584, -0.64705307, -0.35262756, -0.49464053, -0.46001051)
    ElseIf tipo = "T90" And Abs(nVal - 1#) < TOL And Abs(dVal - 0.5) < TOL Then
        xMin = 0.498: xMax = 6.013
        knots = Array(xMin, xMin, xMin, xMin, 1.553947, 4.272008, xMax, xMax, xMax, xMax)
        coef = Array(-1.2493052, -0.21297843, 0.68045281, 0.60400063, 0.66241861, 0.62568415)
    ElseIf tipo = "T90" And Abs(nVal - 1#) < TOL And Abs(dVal - 1#) < TOL Then
        xMin = 0.492: xMax = 6.008
        knots = Array(xMin, xMin, xMin, xMin, 1.665461, 3.796127, xMax, xMax, xMax, xMax)
        coef = Array(-1.23689244, -0.05869091, 0.59287275, 0.71113093, 0.68233148, 0.68113623)
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 0.5) < TOL Then
        xMin = 0.498: xMax = 5.97
        knots = Array(xMin, xMin, xMin, xMin, 1.14419, 3.144529, xMax, xMax, xMax, xMax)
        coef = Array(-2.76554227, -1.89362487, -1.03867114, -0.71339992, -0.65438117, -0.65676024)
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1#) < TOL Then
        xMin = 0.49: xMax = 5.968
        knots = Array(xMin, xMin, xMin, xMin, 1.398732, 3.593282, xMax, xMax, xMax, xMax)
        coef = Array(-2.73837897, -1.5569313, -0.78725423, -0.49975407, -0.46274246, -0.45514185)
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1.5) < TOL Then
        xMin = 0.504: xMax = 5.981
        knots = Array(xMin, xMin, xMin, xMin, 3.148895, xMax, xMax, xMax, xMax)
        coef = Array(-0.44771107, -0.13870722, 0.08130029, 0.08425058, 0.0909222)
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 2#) < TOL Then
        xMin = 0.513: xMax = 5.984
        knots = Array(xMin, xMin, xMin, xMin, 3.640929, xMax, xMax, xMax, xMax)
        coef = Array(-0.05473919, 0.11828186, 0.235689, 0.24928388, 0.24316345)
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 0.5) < TOL Then
        xMin = 0.494: xMax = 6.013
        knots = Array(xMin, xMin, xMin, xMin, 0.713944, 2.156649, 4.477424, xMax, xMax, xMax, xMax)
        coef = Array(-1.68632268, -1.47736563, -0.44213838, 0.51374517, 0.42034107, 0.60733429, 0.55098422)
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1#) < TOL Then
        xMin = 0.491: xMax = 6.021
        knots = Array(xMin, xMin, xMin, xMin, 0.652741, 1.153957, 3.621675, xMax, xMax, xMax, xMax)
        coef = Array(-1.26261103, -0.91833432, -0.40439888, 0.46076276, 0.49100961, 0.6075961, 0.59869541)
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1.5) < TOL Then
        xMin = 0.507: xMax = 6.021
        knots = Array(xMin, xMin, xMin, xMin, 2.153749, 4.188183, xMax, xMax, xMax, xMax)
        coef = Array(0.32821908, 0.41651276, 0.60581081, 0.6688062, 0.70391206, 0.6980772)
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 2#) < TOL Then
        xMin = 0.514: xMax = 5.992
        knots = Array(xMin, xMin, xMin, xMin, 2.280312, 3.524197, xMax, xMax, xMax, xMax)
        coef = Array(0.44070794, 0.51347597, 0.63117748, 0.7178538, 0.74074361, 0.7450056)
    Else
        TLookup = False
    End If
End Function

Private Function TYRange(ByVal tipo As String, ByVal nVal As Double, ByVal dVal As Double, _
                         ByRef yMin As Double, ByRef yMax As Double) As Boolean
    ' Min/max REALI di T (campionati), usati per messaggi d'errore (GetAbacoYRange).
    TYRange = True

    If tipo = "T50" And Abs(nVal - 1#) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.001734: yMax = 0.224485
    ElseIf tipo = "T50" And Abs(nVal - 1#) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.002011: yMax = 0.354867
    ElseIf tipo = "T90" And Abs(nVal - 1#) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.056324: yMax = 4.428267
    ElseIf tipo = "T90" And Abs(nVal - 1#) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.057957: yMax = 4.87714
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.001716: yMax = 0.220472
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.001827: yMax = 0.350637
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1.5) < TOL Then
        yMin = 0.356688: yMax = 1.232884
    ElseIf tipo = "T50" And Abs(nVal - 2.5) < TOL And Abs(dVal - 2#) < TOL Then
        yMin = 0.881578: yMax = 1.759577
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 0.5) < TOL Then
        yMin = 0.020591: yMax = 3.72751
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1#) < TOL Then
        yMin = 0.054625: yMax = 3.977579
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 1.5) < TOL Then
        yMin = 2.129213: yMax = 5.00337
    ElseIf tipo = "T90" And Abs(nVal - 2.5) < TOL And Abs(dVal - 2#) < TOL Then
        yMin = 2.758722: yMax = 5.559114
    Else
        TYRange = False
    End If
End Function

' =============================================================================
' VALUTATORI NUMERICI
' =============================================================================

Private Function EvalPoly(ByRef coef As Variant, ByVal x As Double) As Double
    ' Horner. coef ordinato da grado massimo a grado 0 (come numpy.polyfit).
    Dim i As Long, acc As Double
    acc = coef(LBound(coef))
    For i = LBound(coef) + 1 To UBound(coef)
        acc = acc * x + coef(i)
    Next i
    EvalPoly = acc
End Function

Private Function EvalBSpline(ByRef knots As Variant, ByRef coef As Variant, _
                             ByVal k As Integer, ByVal x As Double) As Double
    ' Valutazione di una B-spline tramite algoritmo di De Boor.
    ' knots: vettore nodi completo (bordi ripetuti k+1 volte).
    ' coef:  coefficienti di controllo (0-based).
    ' k:     grado (3 = cubica).
    Dim n As Long          ' indice ultimo coefficiente
    Dim m As Long          ' indice ultimo nodo
    n = UBound(coef) - LBound(coef)
    m = UBound(knots) - LBound(knots)

    ' Trova l'intervallo [t(i), t(i+1)) che contiene x (clamp ai bordi)
    Dim i As Long
    Dim kb As Long: kb = LBound(knots)
    Dim cb As Long: cb = LBound(coef)

    If x <= knots(kb + k) Then
        i = k
    ElseIf x >= knots(kb + n) Then
        i = n
    Else
        i = k
        Do While Not (x >= knots(kb + i) And x < knots(kb + i + 1))
            i = i + 1
            If i > n Then Exit Do
        Loop
    End If

    ' Copia locale dei coefficienti coinvolti: d(0..k)
    Dim d() As Double
    ReDim d(0 To k)
    Dim j As Long
    For j = 0 To k
        d(j) = coef(cb + i - k + j)
    Next j

    ' Ricorsione di De Boor
    Dim r As Long, alpha As Double
    Dim tL As Double, tR As Double
    For r = 1 To k
        For j = k To r Step -1
            tL = knots(kb + i - k + j)
            tR = knots(kb + i + 1 + j - r)
            If tR - tL = 0 Then
                alpha = 0
            Else
                alpha = (x - tL) / (tR - tL)
            End If
            d(j) = (1# - alpha) * d(j - 1) + alpha * d(j)
        Next j
    Next r

    EvalBSpline = d(k)
End Function
