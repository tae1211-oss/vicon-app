'=============================================================
' 모듈명 : QR_작업지시서
' 용도   : DECK작업지시서 시트 → job_order QR 생성 (J1:K4 위치)
' 삽입처 : 작업지시서 .xlsm 파일의 VBA 모듈
'
' ▶ 읽는 셀 위치 (실제 작업지시서에 맞게 수정하세요)
'   C2  = 업체명
'   C3  = 현장명
'   C4  = 의뢰번호 (req_code)
'   B9~ = 패킹번호 (B열, 9행부터)
'   N열 = 합계수량(장수)
'   O열 = 합계면적(㎡)
'=============================================================

Private Const COL_PACK   As Long = 2    ' B열 = 패킹번호
Private Const COL_SHEETS As Long = 14   ' N열 = 합계수량(장수)
Private Const COL_AREA   As Long = 15   ' O열 = 합계면적(㎡)
Private Const ROW_START  As Long = 9    ' 데이터 시작 행 (8행=헤더, 9행~=데이터)
Private Const CELL_REQ   As String = "C4"  ' 의뢰번호 셀

Sub QR_작업지시서_생성()

    Dim ws As Worksheet

    ' ── 시트 찾기 ──────────────────────────────────────────
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("DECK작업지시서")
    On Error GoTo 0
    If ws Is Nothing Then
        MsgBox "'DECK작업지시서' 시트를 찾을 수 없습니다.", vbExclamation
        Exit Sub
    End If

    ' ── 기본 정보 읽기 ────────────────────────────────────
    Dim company  As String
    Dim site     As String
    Dim reqCode  As String
    company = Trim(CStr(ws.Range("C2").Value))
    site    = Trim(CStr(ws.Range("C3").Value))
    reqCode = Trim(CStr(ws.Range(CELL_REQ).Value))

    If company = "" Or site = "" Then
        MsgBox "C2(업체명) 또는 C3(현장명)이 비어 있습니다.", vbExclamation
        Exit Sub
    End If

    ' ── B열(9행~)에서 패킹번호 수집 ────────────────────────
    Dim minPack  As Long, maxPack As Long
    Dim packCount As Long
    Dim v As Variant, i As Long
    minPack = 999999999 : maxPack = 0 : packCount = 0

    For i = ROW_START To 5000
        v = ws.Cells(i, COL_PACK).Value
        If IsNumeric(v) And v > 0 Then
            packCount = packCount + 1
            If CLng(v) < minPack Then minPack = CLng(v)
            If CLng(v) > maxPack Then maxPack = CLng(v)
        End If
    Next i

    If packCount = 0 Then
        MsgBox "B열(" & ROW_START & "행~)에서 패킹번호를 찾을 수 없습니다.", vbExclamation
        Exit Sub
    End If

    ' ── pack_from~pack_to 장수·면적 배열 구성 ────────────
    Dim totalPacks As Long
    totalPacks = maxPack - minPack + 1

    Dim sheets() As Variant
    Dim areas()  As Variant
    ReDim sheets(0 To totalPacks - 1)
    ReDim areas(0 To totalPacks - 1)

    Dim hasDetail As Boolean
    hasDetail = False

    For i = ROW_START To 5000
        v = ws.Cells(i, COL_PACK).Value
        If IsNumeric(v) And v >= minPack And v <= maxPack Then
            Dim idx As Long
            idx = CLng(v) - minPack

            Dim sv As Variant, av As Variant
            sv = ws.Cells(i, COL_SHEETS).Value
            av = ws.Cells(i, COL_AREA).Value

            If IsNumeric(sv) And sv > 0 Then
                sheets(idx) = CLng(sv)
                hasDetail = True
            End If
            If IsNumeric(av) And av > 0 Then
                areas(idx) = Round(CDbl(av), 2)
                hasDetail = True
            End If
        End If
    Next i

    ' ── JSON 생성 ─────────────────────────────────────────
    Dim jsonStr As String
    jsonStr = "{" & _
        """type"":""job_order""," & _
        """company"":""" & company & """," & _
        """site"":""" & site & """," & _
        """req_code"":""" & reqCode & """," & _
        """pack_from"":" & minPack & "," & _
        """pack_to"":" & maxPack

    If hasDetail Then
        Dim dArr As String
        Dim j As Long
        For j = 0 To totalPacks - 1
            Dim sVal As String, aVal As String
            sVal = IIf(IsEmpty(sheets(j)) Or IsNull(sheets(j)), "0", CStr(sheets(j)))
            aVal = IIf(IsEmpty(areas(j))  Or IsNull(areas(j)),  "0", CStr(areas(j)))
            dArr = dArr & IIf(j = 0, "", ",") & "[" & sVal & "," & aVal & "]"
        Next j
        jsonStr = jsonStr & ",""d"":[" & dArr & "]"
    End If

    jsonStr = jsonStr & "}"

    ' ── J1:K4 범위에 QR 삽입 ─────────────────────────────
    Dim qrRange As Range
    Set qrRange = ws.Range("J1:K4")
    Dim qrW As Double, qrH As Double
    qrW = qrRange.Width
    qrH = qrRange.Height

    Application.StatusBar = "QR 코드 생성 중... (인터넷 필요)"
    Application.ScreenUpdating = False

    Call QR_삽입_영구저장(ws, jsonStr, ws.Range("J1"), qrW, qrH, "QR_작업지시서")

    Application.ScreenUpdating = True
    Application.StatusBar = False

    Dim detailMsg As String
    If hasDetail Then
        detailMsg = Chr(10) & "장수·면적 데이터 포함됨"
    Else
        detailMsg = Chr(10) & "※ 장수·면적 없음 (N·O열 확인)"
    End If

    MsgBox "✅ QR 코드 생성 완료!" & Chr(10) & Chr(10) & _
           "업체명  : " & company & Chr(10) & _
           "현장명  : " & site & Chr(10) & _
           "의뢰번호: " & IIf(reqCode = "", "(없음)", reqCode) & Chr(10) & _
           "패킹    : " & minPack & " ~ " & maxPack & " (" & packCount & "개)" & _
           detailMsg & Chr(10) & Chr(10) & _
           "J1:K4 위치에 삽입되었습니다.", vbInformation
End Sub

'=============================================================
' 공통: QR 이미지 생성 + 영구저장
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
        MsgBox "QR 서버 오류 (HTTP " & req.Status & ")" & Chr(10) & _
               "인터넷 연결을 확인하세요.", vbExclamation
        Exit Sub
    End If

    ' 임시 파일 저장
    Dim tmpFile As String
    tmpFile = Environ("TEMP") & "\vicon_qr_" & Format(Now, "HHmmss") & ".png"

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

    ' 영구 삽입 (파일 저장 후 재오픈해도 유지)
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
' 공통: 한글 포함 UTF-8 URL 인코딩
'=============================================================
Function UTF8_URLEncode(sText As String) As String
    Dim oStm As Object
    Set oStm = CreateObject("ADODB.Stream")
    oStm.Type = 2 : oStm.Charset = "utf-8" : oStm.Open
    oStm.WriteText sText
    oStm.Position = 0
    oStm.Type = 1
    oStm.Position = 3  ' UTF-8 BOM 건너뜀

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
