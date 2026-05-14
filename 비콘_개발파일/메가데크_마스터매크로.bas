Attribute VB_Name = "Module1"
'=============================================================
' 모듈명 : 메가데크_마스터매크로 (Module1)
' 용도   : 발주서 → DECK작업지시서 자동 생성 (패킹마크 시스템)
' 삽입처 : 메가데크 작업지시서 .xlsm 파일의 VBA 모듈
'
' ▶ 연관 파일
'   - QR_작업지시서.bas : QR 코드 생성 모듈 (별도 삽입)
'     * QR JSON 형식이 변경될 경우 해당 파일도 함께 확인/수정할 것
'     * QR 데이터 구조: {"type":"job_order","company":"...","site":"...",
'                        "req_code":"...","pack_from":N,"pack_to":N,
'                        "d":[[장수,면적],...]}
'     * d[i] = [N열 합계수량, O열 합계면적] (pack_from+i 번째 패킹)
'
' ▶ 처리 순서
'   1. Step1_OrganizeOrderData  : 발주서 길이보정·정렬·중복병합
'   2. Step2_GenerateWorkOrder  : DECK작업지시서 생성 + 패킹번호 부여
'   3. Step3_SyncAndHideRows    : 성형작업지시서 동기화 + 빈행 숨김
'   4. Step4_SetPrintAreas      : 덱/스티커 라벨 인쇄영역 설정
'   5. Step5_SaveAsFile         : 파일명 자동 제안 후 저장
'=============================================================

' ==================================================================================
' [메인] 버튼 하나로 모든 작업 처리
' ==================================================================================
Sub Run_All_Process()
    Dim answer As Integer
    answer = MsgBox("새로운 패킹마크 자동화 시스템을 시작합니다." & vbCrLf & vbCrLf & _
                    "1. 발주서 정렬 자동 및 길이 보정 (길이 A값 기준 정렬 일부 포함)" & vbCrLf & _
                    "2. 작업 지시서 생성 및 패킹 번호 자동 부여" & vbCrLf & _
                    "3. 성형작업지시서 동기화 및 텍스트 '날짜 형식' 설정" & vbCrLf & _
                    "4. 인쇄 영역 자동화 및 [태그/스티커 코드 설정]" & vbCrLf & vbCrLf & _
                    "시작하시겠습니까?", vbYesNo + vbQuestion, "패킹마크 시스템")

    If answer = vbYes Then
        Call Step1_OrganizeOrderData

        If Step2_GenerateWorkOrder() = False Then
            MsgBox "작업이 취소되었습니다.", vbExclamation
            Exit Sub
        End If

        Call Step3_SyncAndHideRows
        Call Step4_SetPrintAreas

        MsgBox "모든 작업이 완료되었습니다!" & vbCrLf & "이어서 [다른 이름으로 저장] 창이 열립니다.", vbInformation, "작업 완료"

        Call Step5_SaveAsFile
    End If
End Sub

' ==================================================================================
' [함수] 저장 폴더 스캔 → 다음 패킹 일련번호 반환
' ==================================================================================
Function GetNextPackingNumber() As Long
    Dim folderPath As String, fileName As String
    Dim maxNo As Long, currentMax As Long
    Dim i As Integer, ch As String, prefix As String
    Dim splitArr() As String

    folderPath = ThisWorkbook.Path
    If folderPath = "" Then GoTo ExitFunc

    fileName = Dir(folderPath & "\*.xls*")
    maxNo = 0

    Do While fileName <> ""
        prefix = ""
        For i = 1 To Len(fileName)
            ch = Mid(fileName, i, 1)
            If ch Like "[0-9]" Or ch = "-" Then
                prefix = prefix & ch
            Else
                Exit For
            End If
        Next i

        If prefix <> "" Then
            If InStr(prefix, "-") > 0 Then
                splitArr = Split(prefix, "-")
                currentMax = Val(splitArr(UBound(splitArr)))
            Else
                currentMax = Val(prefix)
            End If
            If currentMax > maxNo Then maxNo = currentMax
        End If
        fileName = Dir()
    Loop

ExitFunc:
    If maxNo = 0 Then
        GetNextPackingNumber = 1
    Else
        GetNextPackingNumber = maxNo + 1
    End If
End Function

' ==================================================================================
' [STEP 1] 길이 보정 + 자연정렬 + 동일 행 병합 삭제
' ==================================================================================
Sub Step1_OrganizeOrderData()
    Dim wsOrder As Worksheet
    Dim lastRow As Long, i As Long, k As Integer
    Dim currentL As Double, nVal As Long, pVal As Double
    Dim strVal As String, sortKey As String, numStr As String, ch As String
    Dim key1 As String, key2 As String
    Dim darkPurple As Long: darkPurple = RGB(112, 48, 160)

    On Error Resume Next
    Set wsOrder = ThisWorkbook.Sheets("발주서")
    On Error GoTo 0
    If wsOrder Is Nothing Then Exit Sub

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    lastRow = wsOrder.Cells(wsOrder.Rows.Count, "J").End(xlUp).Row
    If lastRow < 2 Then Exit Sub

    ' [1] 길이(J열) 보정
    For i = 2 To lastRow
        currentL = Val(Replace(wsOrder.Cells(i, "J").Value, ",", ""))
        If currentL > 0 Then
            nVal = Round(currentL / 200, 0): If nVal = 0 Then nVal = 1
            pVal = currentL / nVal
            If pVal < 190 Or pVal > 210 Then
                If pVal < 190 Then wsOrder.Cells(i, "J").Value = 190 * nVal Else wsOrder.Cells(i, "J").Value = 190 * (nVal + 1)
                With wsOrder.Cells(i, "J")
                    .Interior.Color = darkPurple: .Font.Color = RGB(255, 255, 255): .Font.Bold = True
                End With
            Else
                wsOrder.Cells(i, "J").Interior.ColorIndex = xlNone
                wsOrder.Cells(i, "J").Font.ColorIndex = xlAutomatic
                wsOrder.Cells(i, "J").Font.Bold = False
            End If
        End If
    Next i

    ' [2] 자연정렬 키 생성 (A열 기준)
    For i = 2 To lastRow
        strVal = Trim(wsOrder.Cells(i, "A").Value)
        sortKey = "": numStr = ""
        For k = 1 To Len(strVal)
            ch = Mid(strVal, k, 1)
            If ch Like "[0-9]" Then
                numStr = numStr & ch
            Else
                If numStr <> "" Then sortKey = sortKey & Format(Val(numStr), "0000"): numStr = ""
                sortKey = sortKey & ch
            End If
        Next k
        If numStr <> "" Then sortKey = sortKey & Format(Val(numStr), "0000")
        wsOrder.Cells(i, "Q").Value = sortKey
    Next i

    ' [3] 정렬 (1순위: A열 자연정렬, 2순위: J열 길이 내림차순)
    With wsOrder.Sort
        .SortFields.Clear
        .SortFields.Add Key:=wsOrder.Range("Q2:Q" & lastRow), Order:=xlAscending
        .SortFields.Add Key:=wsOrder.Range("J2:J" & lastRow), Order:=xlDescending
        .SetRange wsOrder.Range("A1:Q" & lastRow)
        .Header = xlYes: .Apply
    End With
    wsOrder.Columns("Q").Delete

    ' [4] 동일 행 병합 삭제 (K~O열 수량 합산 후 행 삭제)
    For i = lastRow To 3 Step -1
        key1 = Trim(wsOrder.Cells(i, "A").Value) & "|" & Trim(wsOrder.Cells(i, "C").Value) & "|" & _
               Trim(wsOrder.Cells(i, "D").Value) & "|" & Trim(wsOrder.Cells(i, "E").Value) & "|" & _
               Trim(wsOrder.Cells(i, "F").Value) & "|" & Trim(wsOrder.Cells(i, "G").Value) & "|" & _
               Trim(wsOrder.Cells(i, "H").Value) & "|" & Trim(wsOrder.Cells(i, "I").Value) & "|" & _
               Trim(wsOrder.Cells(i, "J").Value)
        key2 = Trim(wsOrder.Cells(i - 1, "A").Value) & "|" & Trim(wsOrder.Cells(i - 1, "C").Value) & "|" & _
               Trim(wsOrder.Cells(i - 1, "D").Value) & "|" & Trim(wsOrder.Cells(i - 1, "E").Value) & "|" & _
               Trim(wsOrder.Cells(i - 1, "F").Value) & "|" & Trim(wsOrder.Cells(i - 1, "G").Value) & "|" & _
               Trim(wsOrder.Cells(i - 1, "H").Value) & "|" & Trim(wsOrder.Cells(i - 1, "I").Value) & "|" & _
               Trim(wsOrder.Cells(i - 1, "J").Value)

        If key1 = key2 Then
            wsOrder.Cells(i - 1, "K").Value = Val(wsOrder.Cells(i - 1, "K").Value) + Val(wsOrder.Cells(i, "K").Value)
            wsOrder.Cells(i - 1, "L").Value = Val(wsOrder.Cells(i - 1, "L").Value) + Val(wsOrder.Cells(i, "L").Value)
            wsOrder.Cells(i - 1, "M").Value = Val(wsOrder.Cells(i - 1, "M").Value) + Val(wsOrder.Cells(i, "M").Value)
            wsOrder.Cells(i - 1, "N").Value = Val(wsOrder.Cells(i - 1, "N").Value) + Val(wsOrder.Cells(i, "N").Value)
            wsOrder.Cells(i - 1, "O").Value = Val(wsOrder.Cells(i - 1, "O").Value) + Val(wsOrder.Cells(i, "O").Value)
            If wsOrder.Cells(i, "J").Interior.Color = darkPurple Then
                With wsOrder.Cells(i - 1, "J")
                    .Interior.Color = darkPurple: .Font.Color = RGB(255, 255, 255): .Font.Bold = True
                End With
            End If
            wsOrder.Rows(i).Delete
        End If
    Next i
    Application.ScreenUpdating = True
End Sub

' ==================================================================================
' [STEP 2] 작업지시서 생성 + 패킹번호 부여
'          → N열(합계수량), O열(합계면적) 자동 기입
'          → QR_작업지시서.bas의 COL_SHEETS=14(N), COL_AREA=15(O) 와 일치
' ==================================================================================
Function Step2_GenerateWorkOrder() As Boolean
    Dim wsOrder As Worksheet, wsWork As Worksheet
    Dim i As Long, j As Long, targetRow As Long, mergeStartRow As Long
    Dim currentNo As Long, packingLimit As Integer, currentPalletQty As Integer
    Dim hVal As Double, divisor As Double
    Dim currentZone As String, prevZone As String
    Dim qty0 As Long, qty1 As Long, qty2 As Long, qtyM2 As Long, qty3 As Long
    Dim totalRowQty As Long, sectionTotalQty As Long
    Dim space As Long, batchTotal As Long
    Dim use0 As Long, use1 As Long, use2 As Long, useM2 As Long, use3 As Long, remBatch As Long
    Dim lenVal As Double, t As Integer, qVal As Long
    Dim packPlan() As Long, planIdx As Integer, packCount As Integer
    Dim checkZone As String
    Dim steelType As String

    Dim suggestNo As Long
    suggestNo = GetNextPackingNumber()

    Dim userInput As String
    userInput = InputBox("현재 저장폴더에서 스캔한 결과, 권장 패킹 번호는 [" & suggestNo & "]입니다." & vbCrLf & vbCrLf & _
                         "그대로 [확인]을 누르시거나, 다르게 원하는 시작 번호를 입력하세요.", "시작 패킹 번호 설정", CStr(suggestNo))

    If userInput = "" Then
        Step2_GenerateWorkOrder = False
        Exit Function
    End If

    currentNo = Val(userInput)
    If currentNo <= 0 Then currentNo = 1

    Set wsOrder = ThisWorkbook.Sheets("발주서")
    Set wsWork = ThisWorkbook.Sheets("DECK작업지시서")

    Application.ScreenUpdating = False

    steelType = UCase(Trim(wsOrder.Cells(2, "D").Value))
    If steelType = "B" Then
        wsWork.Range("X6").Value = -10
    Else
        wsWork.Range("X6").Value = 0
        wsWork.Range("J9:K193").Interior.Color = vbYellow
    End If

    With wsWork.Range("A9:O193")
        .UnMerge: .ClearContents
        .Font.ColorIndex = xlAutomatic: .Font.Bold = False
        .Font.Name = "맑은 고딕": .Font.Size = 11
        .WrapText = False: .ShrinkToFit = True
        .VerticalAlignment = xlCenter: .HorizontalAlignment = xlCenter
    End With
    wsWork.Range("J9:J193").HorizontalAlignment = xlRight
    wsWork.Range("L9:M193").NumberFormat = "@"

    targetRow = 9: currentPalletQty = 0
    prevZone = "": mergeStartRow = 9

    Dim lastRow As Long
    lastRow = wsOrder.Cells(wsOrder.Rows.Count, "J").End(xlUp).Row

    i = 2
    Do While i <= lastRow
        currentZone = Trim(wsOrder.Cells(i, "A").Value)

        If currentZone <> prevZone Then
            If currentPalletQty > 0 Then
                GoSub FinalizePacking
                currentNo = currentNo + 1
                currentPalletQty = 0
                mergeStartRow = targetRow
            End If

            sectionTotalQty = 0
            hVal = Val(Trim(wsOrder.Cells(i, "G").Value))
            Select Case hVal
                Case Is <= 90:    packingLimit = 66
                Case 91 To 110:   packingLimit = 60
                Case 111 To 120:  packingLimit = 54
                Case 121 To 140:  packingLimit = 48
                Case 141 To 160:  packingLimit = 42
                Case 161 To 190:  packingLimit = 36
                Case 191 To 230:  packingLimit = 30
                Case 231 To 290:  packingLimit = 24
                Case Is >= 291:   packingLimit = 18
                Case Else:        packingLimit = 54
            End Select

            For j = i To lastRow
                checkZone = Trim(wsOrder.Cells(j, "A").Value)
                If checkZone <> currentZone Then Exit For
                sectionTotalQty = sectionTotalQty + _
                    Val(Replace(wsOrder.Cells(j, "L").Value, ",", "")) + _
                    Val(Replace(wsOrder.Cells(j, "M").Value, ",", "")) + _
                    Val(Replace(wsOrder.Cells(j, "N").Value, ",", "")) + _
                    Val(Replace(wsOrder.Cells(j, "O").Value, ",", ""))
            Next j

            packCount = 0: ReDim packPlan(1 To 200)
            Dim tempTotal As Long: tempTotal = sectionTotalQty
            Do While tempTotal > 0
                packCount = packCount + 1
                If tempTotal > packingLimit Then
                    packPlan(packCount) = packingLimit: tempTotal = tempTotal - packingLimit
                Else
                    packPlan(packCount) = tempTotal: tempTotal = 0
                End If
            Loop

            If packCount > 1 Then
                Dim lastP As Long: lastP = packPlan(packCount)
                Dim prevP As Long: prevP = packPlan(packCount - 1)
                Dim borrow As Long: borrow = 0
                If lastP < 6 Then borrow = 6 - lastP Else If lastP Mod 6 = 1 Then borrow = 2 Else If lastP Mod 6 = 2 Then borrow = 1
                If borrow > 0 And (prevP - borrow) >= 6 Then
                    packPlan(packCount - 1) = prevP - borrow
                    packPlan(packCount) = lastP + borrow
                End If
            End If
            planIdx = 1
        End If

        prevZone = currentZone

        qty0  = Val(Replace(wsOrder.Cells(i, "K").Value, ",", ""))
        qty1  = Val(Replace(wsOrder.Cells(i, "L").Value, ",", ""))
        qty2  = Val(Replace(wsOrder.Cells(i, "M").Value, ",", ""))
        qtyM2 = Val(Replace(wsOrder.Cells(i, "N").Value, ",", ""))
        qty3  = Val(Replace(wsOrder.Cells(i, "O").Value, ",", ""))
        totalRowQty = qty1 + qty2 + qtyM2 + qty3

        Do While totalRowQty > 0 Or qty0 > 0
            space = packPlan(planIdx) - currentPalletQty

            If space <= 0 And totalRowQty > 0 Then
                GoSub FinalizePacking
                currentNo = currentNo + 1
                currentPalletQty = 0
                planIdx = planIdx + 1
                space = packPlan(planIdx)
                mergeStartRow = targetRow
            End If

            If totalRowQty > 0 Then
                batchTotal = IIf(totalRowQty <= space, totalRowQty, space)

                use3 = Application.WorksheetFunction.Round(batchTotal * (qty3 / totalRowQty), 0)
                If use3 > qty3 Then use3 = qty3
                remBatch = batchTotal - use3

                If (qty2 + qty1 + qtyM2) > 0 Then
                    useM2 = Application.WorksheetFunction.Round(remBatch * (qtyM2 / (qtyM2 + qty2 + qty1)), 0)
                Else
                    useM2 = 0
                End If
                If useM2 > qtyM2 Then useM2 = qtyM2
                remBatch = remBatch - useM2

                If (qty2 + qty1) > 0 Then
                    use2 = Application.WorksheetFunction.Round(remBatch * (qty2 / (qty2 + qty1)), 0)
                Else
                    use2 = 0
                End If
                If use2 > qty2 Then use2 = qty2
                use1 = remBatch - use2
            Else
                batchTotal = 0: use3 = 0: useM2 = 0: use2 = 0: use1 = 0
            End If

            use0 = qty0: qty0 = 0

            Dim tArr As Variant, qArr As Variant
            tArr = Array("3", "2", "-2", "1", "0")
            qArr = Array(use3, use2, useM2, use1, use0)

            For t = 0 To 4
                If qArr(t) > 0 Then
                    If targetRow <= 193 Then
                        With wsWork
                            .Cells(targetRow, "A").Value = wsOrder.Cells(i, "E").Value
                            .Cells(targetRow, "C").Value = wsOrder.Cells(i, "F").Value
                            .Cells(targetRow, "D").Value = wsOrder.Cells(i, "G").Value
                            .Cells(targetRow, "E").Value = wsOrder.Cells(i, "H").Value
                            .Cells(targetRow, "F").Value = wsOrder.Cells(i, "I").Value
                            .Cells(targetRow, "G").Value = IIf(tArr(t) = "-2", "2", tArr(t))
                            .Cells(targetRow, "H").Value = Val(wsOrder.Cells(i, "J").Value)
                            .Cells(targetRow, "I").Value = qArr(t)
                            If tArr(t) = "0" Then
                                .Cells(targetRow, "J").Value = ""
                            Else
                                .Cells(targetRow, "J").Value = (Val(wsOrder.Cells(i, "J").Value) * qArr(t) * 0.6) / 1000
                            End If
                            divisor = Application.WorksheetFunction.Round(Val(wsOrder.Cells(i, "J").Value) / 200, 0)
                            If divisor = 0 Then divisor = 1
                            .Cells(targetRow, "K").Value = Val(wsOrder.Cells(i, "J").Value) / divisor
                            .Cells(targetRow, "L").Value = "'" & currentZone
                            .Cells(targetRow, "M").Value = "'" & wsOrder.Cells(i, "C").Value
                            If tArr(t) = "0" Or tArr(t) = "-2" Then
                                With .Range(.Cells(targetRow, "G"), .Cells(targetRow, "I"))
                                    .Interior.Color = vbRed: .Font.Color = vbWhite: .Font.Bold = True
                                End With
                            Else
                                With .Range(.Cells(targetRow, "G"), .Cells(targetRow, "I"))
                                    .Interior.ColorIndex = xlNone
                                    .Font.ColorIndex = xlAutomatic: .Font.Bold = False
                                End With
                            End If
                        End With
                    End If
                    targetRow = targetRow + 1
                End If
            Next t

            qty3 = qty3 - use3: qtyM2 = qtyM2 - useM2
            qty2 = qty2 - use2: qty1 = qty1 - use1
            totalRowQty = qty3 + qtyM2 + qty2 + qty1
            currentPalletQty = currentPalletQty + batchTotal
        Loop
        i = i + 1
    Loop

    If targetRow > mergeStartRow Then GoSub FinalizePacking
    Step2_GenerateWorkOrder = True
    Exit Function

FinalizePacking:
    ' N열(합계수량)·O열(합계면적) 기입 — QR_작업지시서.bas COL_SHEETS=14(N), COL_AREA=15(O) 와 일치
    If mergeStartRow <= targetRow - 1 Then
        Dim sumQty As Long, sumArea As Double
        Dim rngTG As Range, rngQty As Range, rngGroup As Range

        Set rngTG  = wsWork.Range(wsWork.Cells(mergeStartRow, "G"), wsWork.Cells(targetRow - 1, "G"))
        Set rngQty = wsWork.Range(wsWork.Cells(mergeStartRow, "I"), wsWork.Cells(targetRow - 1, "I"))
        sumQty  = Application.WorksheetFunction.SumIf(rngTG, "<>0", rngQty)
        sumArea = Application.WorksheetFunction.Sum(wsWork.Range(wsWork.Cells(mergeStartRow, "J"), wsWork.Cells(targetRow - 1, "J")))

        With wsWork.Range(wsWork.Cells(mergeStartRow, "B"), wsWork.Cells(targetRow - 1, "B"))
            .Merge: .HorizontalAlignment = xlCenter: .VerticalAlignment = xlCenter
        End With
        wsWork.Cells(mergeStartRow, "B").Value = currentNo
        wsWork.Cells(mergeStartRow, "N").Value = sumQty                                ' ← N열 합계수량
        wsWork.Cells(mergeStartRow, "O").Value = Application.WorksheetFunction.Round(sumArea, 2) ' ← O열 합계면적
        wsWork.Cells(mergeStartRow, "O").NumberFormat = "0.00"

        Set rngGroup = wsWork.Range(wsWork.Cells(mergeStartRow, 1), wsWork.Cells(targetRow - 1, 15))
        With rngGroup
            .Borders(xlEdgeTop).LineStyle = xlContinuous:    .Borders(xlEdgeTop).Weight = xlThin
            .Borders(xlEdgeBottom).LineStyle = xlContinuous: .Borders(xlEdgeBottom).Weight = xlThin
            If (targetRow - 1) > mergeStartRow Then
                .Borders(xlInsideHorizontal).LineStyle = xlDot: .Borders(xlInsideHorizontal).Weight = xlThin
            End If
        End With
    End If
    Return
End Function

' ==================================================================================
' [STEP 3] 성형작업지시서 동기화 + 빈 행 숨김
' ==================================================================================
Sub Step3_SyncAndHideRows()
    Dim wsWork As Worksheet, wsForming As Worksheet
    Dim lastRowWork As Long, lastRowForming As Long, r As Long
    Dim formingLastCol As Long

    On Error Resume Next
    Set wsWork   = ThisWorkbook.Sheets("DECK작업지시서")
    Set wsForming = ThisWorkbook.Sheets("성형작업지시서")
    On Error GoTo 0
    If wsWork Is Nothing Then Exit Sub

    Application.ScreenUpdating = False
    wsWork.Rows("9:193").Hidden = False
    If Not wsForming Is Nothing Then wsForming.Rows("6:190").Hidden = False

    lastRowWork = wsWork.Cells(193, "C").End(xlUp).Row
    If lastRowWork < 9 Then lastRowWork = 8

    If Not wsForming Is Nothing Then
        On Error GoTo SyncError
        wsForming.Range("C6:C190").UnMerge: wsForming.Range("C6:C190").ClearContents
        If lastRowWork >= 9 Then wsWork.Range("B9:B" & lastRowWork).Copy Destination:=wsForming.Range("C6")

        lastRowForming = lastRowWork - 3
        formingLastCol = wsForming.Cells(5, wsForming.Columns.Count).End(xlToLeft).Column
        If formingLastCol < 5 Then formingLastCol = 14

        For r = 6 To lastRowForming
            If wsForming.Cells(r, "C").MergeArea.Row + wsForming.Cells(r, "C").MergeArea.Rows.Count - 1 = r Then
                With wsForming.Range(wsForming.Cells(r, 1), wsForming.Cells(r, formingLastCol)).Borders(xlEdgeBottom)
                    .LineStyle = xlContinuous: .Weight = xlThin
                End With
            Else
                With wsForming.Range(wsForming.Cells(r, 1), wsForming.Cells(r, formingLastCol)).Borders(xlEdgeBottom)
                    .LineStyle = xlDot: .Weight = xlThin
                End With
            End If
        Next r
        If lastRowForming >= 6 Then
            wsForming.Range(wsForming.Cells(6, 1), wsForming.Cells(6, formingLastCol)).Borders(xlEdgeTop).LineStyle = xlContinuous
        End If

        If lastRowForming <= 42 Then
            wsForming.Rows("43:190").Hidden = True
        Else
            If (lastRowForming + 1) <= 190 Then wsForming.Rows((lastRowForming + 1) & ":190").Hidden = True
        End If
        On Error GoTo 0
    End If

    If lastRowWork <= 45 Then
        wsWork.Rows("46:193").Hidden = True
    Else
        If (lastRowWork + 1) <= 193 Then wsWork.Rows((lastRowWork + 1) & ":193").Hidden = True
    End If
    Application.ScreenUpdating = True
    Exit Sub
SyncError:
    MsgBox "성형 시트 동기화 중 오류가 발생했습니다." & vbCrLf & Err.Description, vbCritical, "오류"
End Sub

' ==================================================================================
' [STEP 4] 덱/스티커 라벨표 인쇄 영역 설정
' ==================================================================================
Sub Step4_SetPrintAreas()
    Dim wsWork As Worksheet, wsDeckTag As Worksheet, wsStickerTag As Worksheet
    Dim lastRowWork As Long, i As Long
    Dim minPackingNo As Long, maxPackingNo As Long, packingCount As Long
    Dim deckEndRow As Long, stickerEndRow As Long

    On Error Resume Next
    Set wsWork      = ThisWorkbook.Sheets("DECK작업지시서")
    Set wsDeckTag   = ThisWorkbook.Sheets("덱라벨표")
    Set wsStickerTag = ThisWorkbook.Sheets("스티커라벨표")
    On Error GoTo 0
    If wsWork Is Nothing Or wsDeckTag Is Nothing Or wsStickerTag Is Nothing Then Exit Sub

    lastRowWork = wsWork.Cells(wsWork.Rows.Count, "C").End(xlUp).Row
    minPackingNo = 999999: maxPackingNo = 0

    For i = 9 To lastRowWork
        If IsNumeric(wsWork.Cells(i, "B").Value) And wsWork.Cells(i, "B").Value > 0 Then
            If wsWork.Cells(i, "B").Value > maxPackingNo Then maxPackingNo = wsWork.Cells(i, "B").Value
            If wsWork.Cells(i, "B").Value < minPackingNo Then minPackingNo = wsWork.Cells(i, "B").Value
        End If
    Next i
    If maxPackingNo = 0 Then Exit Sub

    packingCount = (maxPackingNo - minPackingNo) + 1
    deckEndRow    = packingCount * 28: wsDeckTag.PageSetup.PrintArea    = "$A$3:$E$" & deckEndRow
    stickerEndRow = packingCount * 40: wsStickerTag.PageSetup.PrintArea = "$A$1:$V$" & stickerEndRow
End Sub

' ==================================================================================
' [STEP 5] 파일명 자동 제안 저장
'          파일명 형식: {패킹시작}-{패킹끝}#{의뢰번호}, {현장명}({업체명}).xlsm
'          셀 참조: C2=업체명, C3=현장명, C4=의뢰번호 (QR_작업지시서.bas CELL_REQ="C4" 와 일치)
' ==================================================================================
Sub Step5_SaveAsFile()
    Dim wsWork As Worksheet
    Dim lastRow As Long, i As Long
    Dim startNo As Long, endNo As Long
    Dim orderNo As String, siteName As String, compName As String
    Dim suggestedFileName As String
    Dim savePath As Variant
    Dim invalidChars As Variant
    Dim c As Integer

    On Error Resume Next
    Set wsWork = ThisWorkbook.Sheets("DECK작업지시서")
    On Error GoTo 0
    If wsWork Is Nothing Then Exit Sub

    startNo = 999999: endNo = 0
    lastRow = wsWork.Cells(wsWork.Rows.Count, "C").End(xlUp).Row

    For i = 9 To lastRow
        If IsNumeric(wsWork.Cells(i, "B").Value) And wsWork.Cells(i, "B").Value > 0 Then
            If wsWork.Cells(i, "B").Value < startNo Then startNo = wsWork.Cells(i, "B").Value
            If wsWork.Cells(i, "B").Value > endNo   Then endNo   = wsWork.Cells(i, "B").Value
        End If
    Next i
    If startNo = 999999 Then startNo = 1
    If endNo = 0 Then endNo = 1

    orderNo  = Trim(wsWork.Range("C4").Value)   ' ← QR_작업지시서.bas CELL_REQ="C4" 와 동일
    siteName = Trim(wsWork.Range("C3").Value)
    compName = Trim(wsWork.Range("C2").Value)

    If orderNo  = "" Then orderNo  = "수주번호없음"
    If siteName = "" Then siteName = "현장명없음"
    If compName = "" Then compName = "업체명없음"

    invalidChars = Array("\", "/", ":", "*", "?", """", "<", ">", "|")
    For c = LBound(invalidChars) To UBound(invalidChars)
        orderNo  = Replace(orderNo,  invalidChars(c), "")
        siteName = Replace(siteName, invalidChars(c), "")
        compName = Replace(compName, invalidChars(c), "")
    Next c

    If Left(compName, 1) <> "(" Then compName = "(" & compName
    If Right(compName, 1) <> ")" Then compName = compName & ")"

    If startNo = endNo Then
        suggestedFileName = startNo & "#" & orderNo & ", " & siteName & compName & ".xlsm"
    Else
        suggestedFileName = startNo & "-" & endNo & "#" & orderNo & ", " & siteName & compName & ".xlsm"
    End If

    savePath = Application.GetSaveAsFilename( _
        InitialFileName:=ThisWorkbook.Path & "\" & suggestedFileName, _
        FileFilter:="Excel Macro-Enabled Workbook (*.xlsm), *.xlsm", _
        Title:="작업지시서 저장 (파일명을 확인하세요)")

    If savePath <> False Then
        Application.DisplayAlerts = False
        ThisWorkbook.SaveAs FileName:=savePath, FileFormat:=xlOpenXMLWorkbookMacroEnabled
        Application.DisplayAlerts = True
        MsgBox "작업지시서가 저장되었습니다." & vbCrLf & savePath, vbInformation, "저장 완료"
    End If
End Sub
