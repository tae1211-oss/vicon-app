'=============================================================
' 모듈명 : QR_출고송장
' 용도   : 출고송장 갑지 시트 D7:L59 패킹번호 수집 → shipment QR
' 삽입처 : 출고송장 .xlsx 파일의 VBA 모듈
' 변경   : req_code 제거 / X4(업체명)·X5(현장명) 자동읽기
'          N1:O5 크기로 N1에 영구 삽입
'=============================================================

Sub QR_출고송장_생성()

    ' ── 첫 번째 非갑지 시트에서 업체명·현장명 읽기 ───────
    Dim company As String, site As String
    Dim refWs As Worksheet

    Dim sh As Worksheet
    For Each sh In ThisWorkbook.Sheets
        If InStr(sh.Name, "갑지") = 0 Then
            Set refWs = sh
            Exit For
        End If
    Next sh

    If refWs Is Nothing Then
        MsgBox "갑지가 아닌 시트를 찾을 수 없습니다.", vbExclamation
        Exit Sub
    End If

    company = Trim(CStr(refWs.Range("X4").Value))
    site    = Trim(CStr(refWs.Range("X5").Value))

    If company = "" Or site = "" Then
        company = InputBox("X4 셀에서 업체명을 읽지 못했습니다." & Chr(10) & "업체명을 직접 입력하세요.", "업체명", company)
        If company = "" Then Exit Sub
        site = InputBox("X5 셀에서 현장명을 읽지 못했습니다." & Chr(10) & "현장명을 직접 입력하세요.", "현장명", site)
        If site = "" Then Exit Sub
    End If

    ' ── 갑지 시트 전체에서 D7:L59 패킹번호 수집 ──────────
    Dim packDict As Object
    Set packDict = CreateObject("Scripting.Dictionary")

    Dim galjiCount As Long
    galjiCount = 0

    For Each sh In ThisWorkbook.Sheets
        If InStr(sh.Name, "갑지") > 0 Then
            galjiCount = galjiCount + 1
            Dim cell As Range
            For Each cell In sh.Range("D7:L59")
                Dim v As Variant
                v = cell.Value
                If IsNumeric(v) And v > 0 And Int(v) = v Then
                    Dim pn As Long
                    pn = CLng(v)
                    If Not packDict.Exists(pn) Then packDict.Add pn, pn
                End If
            Next cell
        End If
    Next sh

    If galjiCount = 0 Then
        MsgBox "시트명에 '갑지'가 포함된 시트가 없습니다.", vbExclamation
        Exit Sub
    End If
    If packDict.Count = 0 Then
        MsgBox "D7:L59 범위에서 유효한 패킹번호를 찾을 수 없습니다.", vbExclamation
        Exit Sub
    End If

    ' ── 패킹번호 정렬 ─────────────────────────────────────
    Dim keys() As Variant
    keys = packDict.Keys
    Dim ii As Long, jj As Long, tmp As Variant
    For ii = 0 To UBound(keys) - 1
        For jj = ii + 1 To UBound(keys)
            If keys(ii) > keys(jj) Then
                tmp = keys(ii) : keys(ii) = keys(jj) : keys(jj) = tmp
            End If
        Next jj
    Next ii

    ' ── JSON 배열 생성 (req_code 없음) ────────────────────
    Dim packArr As String
    Dim k As Long
    For k = 0 To UBound(keys)
        packArr = packArr & IIf(k = 0, "", ",") & CStr(keys(k))
    Next k

    Dim jsonStr As String
    jsonStr = "{" & _
        """type"":""shipment""," & _
        """company"":""" & company & """," & _
        """site"":""" & site & """," & _
        """packs"":[" & packArr & "]" & _
        "}"

    ' ── 확인 메시지 ───────────────────────────────────────
    Dim ans As VbMsgBoxResult
    ans = MsgBox("수집 결과:" & Chr(10) & _
                 "  업체명  : " & company & Chr(10) & _
                 "  현장명  : " & site & Chr(10) & _
                 "  갑지 시트: " & galjiCount & "개" & Chr(10) & _
                 "  패킹번호: " & packDict.Count & "개 (" & keys(0) & "~" & keys(UBound(keys)) & ")" & Chr(10) & Chr(10) & _
                 "N1에 QR 코드를 생성하시겠습니까?", _
                 vbYesNo + vbQuestion, "출고 QR 생성")
    If ans = vbNo Then Exit Sub

    ' ── 첫 번째 갑지 시트의 N1:O5 크기로 QR 삽입 ────────
    Dim targetWs As Worksheet
    For Each sh In ThisWorkbook.Sheets
        If InStr(sh.Name, "갑지") > 0 Then
            Set targetWs = sh
            Exit For
        End If
    Next sh

    Dim qrRange As Range
    Set qrRange = targetWs.Range("N1:O5")
    Dim qrW As Double, qrH As Double
    qrW = qrRange.Width
    qrH = qrRange.Height

    Application.ScreenUpdating = False
    Application.StatusBar = "출고 QR 생성 중..."

    Call QR_삽입_영구저장(targetWs, jsonStr, targetWs.Range("N1"), qrW, qrH, "QR_출고송장")

    Application.ScreenUpdating = True
    Application.StatusBar = False

    MsgBox "✅ 출고 QR 생성 완료!" & Chr(10) & Chr(10) & _
           "업체명 : " & company & Chr(10) & _
           "현장명 : " & site & Chr(10) & _
           "패킹 수: " & packDict.Count & "개" & Chr(10) & Chr(10) & _
           targetWs.Name & " 시트 N1에 삽입되었습니다.", vbInformation
End Sub

'=============================================================
' 공통: QR 이미지 영구 삽입
'=============================================================
Sub QR_삽입_영구저장(ws As Worksheet, jsonData As String, _
                     anchorCell As Range, qrW As Double, qrH As Double, _
                     shapeName As String)

    Dim encoded As String
    encoded = UTF8_URLEncode(jsonData)

    Dim apiURL As String
    apiURL = "https://api.qrserver.com/v1/create-qr-code/?size=400x400&ecc=M&data=" & encoded

    Dim req As Object
    Set req = CreateObject("MSXML2.XMLHTTP.6.0")
    On Error GoTo HTTP_오류
    req.Open "GET", apiURL, False
    req.Send

    If req.Status <> 200 Then
        MsgBox "QR 서버 오류 (HTTP " & req.Status & ")", vbExclamation
        Exit Sub
    End If

    Dim tmpFile As String
    tmpFile = Environ("TEMP") & "\beacon_qr_" & Format(Now, "HHmmss") & ".png"

    Dim stm As Object
    Set stm = CreateObject("ADODB.Stream")
    stm.Type = 1 : stm.Open
    stm.Write req.responseBody
    stm.SaveToFile tmpFile, 2
    stm.Close

    ' 기존 동일 이름 도형 삭제
    Dim shp As Shape
    For Each shp In ws.Shapes
        If shp.Name = shapeName Then shp.Delete : Exit For
    Next shp

    ' 영구 삽입 (저장 후 재오픈해도 유지)
    Dim inserted As Shape
    Set inserted = ws.Shapes.AddPicture( _
        Filename:=tmpFile, _
        LinkToFile:=False, _
        SaveWithDocument:=True, _
        Left:=anchorCell.Left + 2, _
        Top:=anchorCell.Top + 2, _
        Width:=qrW - 4, _
        Height:=qrH - 4)
    inserted.Name = shapeName

    On Error Resume Next : Kill tmpFile : On Error GoTo 0
    Exit Sub

HTTP_오류:
    MsgBox "인터넷 오류: " & Err.Description, vbExclamation
End Sub

'=============================================================
' 공통: UTF-8 URL 인코딩
'=============================================================
Function UTF8_URLEncode(sText As String) As String
    Dim oStm As Object
    Set oStm = CreateObject("ADODB.Stream")
    oStm.Type = 2 : oStm.Charset = "utf-8" : oStm.Open
    oStm.WriteText sText
    oStm.Position = 0
    oStm.Type = 1
    oStm.Position = 3

    Dim bData() As Byte
    bData = oStm.Read
    oStm.Close

    Dim result As String, b As Byte, j As Long
    For j = 0 To UBound(bData)
        b = bData(j)
        If (b >= 48 And b <= 57) Or (b >= 65 And b <= 90) Or _
           (b >= 97 And b <= 122) Or b = 45 Or b = 46 Or b = 95 Or b = 126 Then
            result = result & Chr(b)
        Else
            result = result & "%" & UCase(Right("0" & Hex(b), 2))
        End If
    Next j
    UTF8_URLEncode = result
End Function
