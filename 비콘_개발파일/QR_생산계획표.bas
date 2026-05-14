'=============================================================
' 모듈명 : QR_생산계획표
' 용도   : "QR이미지" 시트 D열(의뢰번호) 기준으로
'          네트워크 작업지시서 파일명에서 패킹번호·업체명·현장명 파싱
'          → E열(5열)에 QR 영구 삽입
'
' 동작 방식
'   1) 시작 시 네트워크 폴더를 한 번만 재귀 스캔
'      → 의뢰번호(#뒤)를 키로 하는 파일목록 딕셔너리 생성
'   2) 같은 의뢰번호가 여럿이면 수정일자 최신 파일 선택
'   3) 각 행: 딕셔너리 조회 → 파일명 파싱 → API QR 생성
'   4) 해당 의뢰번호 파일 없으면 해당 행 건너뜀 (QR 미생성)
'   ※ 파일을 열지 않으므로 빠름
'
' 파일명 형식:
'   {pack_from}-{pack_to}#{req_code}, {site}({company}).xlsm
'   예) 1148-1150#0421-41-GGM, 가양동 CJ부지 업무복합시설(현대건설).xlsm
'=============================================================

Const WORK_ORDER_PATH As String = "\\192.168.0.17\모두의폴더\"
Const SEARCH_DEPTH    As Long   = 5     ' 최대 탐색 깊이

Sub QR_생산계획표_생성()

    ' ── QR이미지 시트 ─────────────────────────────────────
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets("QR이미지")
    On Error GoTo 0
    If ws Is Nothing Then
        MsgBox "'QR이미지' 시트를 찾을 수 없습니다.", vbExclamation
        Exit Sub
    End If

    ' ── 데이터 마지막 행 (D열 기준) ───────────────────────
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 4).End(xlUp).Row
    If lastRow < 5 Then
        MsgBox "QR이미지 시트에 데이터가 없습니다. (5행부터 입력)", vbExclamation
        Exit Sub
    End If

    ' ── 네트워크 접근 확인 ────────────────────────────────
    On Error Resume Next
    Dim testAttr As Long
    testAttr = GetAttr(WORK_ORDER_PATH)
    Dim networkOK As Boolean
    networkOK = (Err.Number = 0)
    Err.Clear
    On Error GoTo 0

    If Not networkOK Then
        MsgBox "⚠️ 네트워크 경로에 접근할 수 없습니다." & Chr(10) & _
               WORK_ORDER_PATH, vbExclamation
        Exit Sub
    End If

    Dim ans As VbMsgBoxResult
    ans = MsgBox((lastRow - 4) & "개 행의 QR을 생성합니다." & Chr(10) & Chr(10) & _
                 "• 네트워크 폴더를 스캔해 작업지시서 파일명에서 패킹번호를 읽습니다." & Chr(10) & _
                 "• 작업지시서 파일이 없는 행은 건너뜁니다." & Chr(10) & Chr(10) & _
                 "계속하시겠습니까?", vbYesNo + vbQuestion, "QR 생성 확인")
    If ans = vbNo Then Exit Sub

    Application.ScreenUpdating = False

    ' ── 네트워크 폴더 한 번만 스캔 (파일 목록 수집) ────────
    Application.StatusBar = "네트워크 폴더 스캔 중... (최초 1회)"

    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")

    ' allFiles: "전체경로|수정일시" 형식 문자열 모음
    Dim allFiles As New Collection
    If fso.FolderExists(WORK_ORDER_PATH) Then
        Call 폴더_파일수집(fso.GetFolder(WORK_ORDER_PATH), allFiles, SEARCH_DEPTH)
    End If

    ' ── 행별 처리 ─────────────────────────────────────────
    Dim successCount As Long, skipCount As Long
    Dim i As Long

    For i = 5 To lastRow   ' 5행부터 (1~4행은 헤더)
        Dim reqCode As String
        reqCode = Trim(CStr(ws.Cells(i, 4).Value))   ' D열 = 의뢰번호
        If reqCode = "" Then GoTo 다음행

        Application.StatusBar = "QR 생성 중... " & (i - 4) & "/" & (lastRow - 4) & _
                                 " [" & reqCode & "]"

        ' ── 파일 목록에서 reqCode 포함 파일 조회 (대소문자 무시) ─
        Dim workOrderFile As String
        workOrderFile = 최신파일_검색(allFiles, reqCode)
        If workOrderFile = "" Then GoTo 다음행

        ' ── 파일명 파싱 ─────────────────────────────────────
        Dim parsedCompany As String, parsedSite As String
        Dim packFrom As Long, packTo As Long
        Call 파일명_전체파싱(fso.GetFileName(workOrderFile), _
                            parsedCompany, parsedSite, packFrom, packTo)

        If packFrom = 0 Or packTo = 0 Then GoTo 다음행
        If packTo < packFrom Or (packTo - packFrom) > 5000 Then GoTo 다음행

        ' ── 패킹 배열 문자열 생성 ───────────────────────────
        Dim packsArr As String
        Dim p As Long
        For p = packFrom To packTo
            packsArr = packsArr & IIf(p = packFrom, "", ",") & p
        Next p

        ' ── JSON 생성 ────────────────────────────────────────
        Dim jsonStr As String
        jsonStr = "{" & _
            """type"":""plan""," & _
            """company"":""" & parsedCompany & """," & _
            """site"":""" & parsedSite & """," & _
            """packs"":[" & packsArr & "]" & _
            "}"

        ' ── E열 셀 크기 확보 ─────────────────────────────────
        Dim qrCell As Range
        Set qrCell = ws.Cells(i, 5)

        If ws.Rows(i).RowHeight < 80 Then ws.Rows(i).RowHeight = 80
        If ws.Columns(5).Width < 12  Then ws.Columns(5).Width = 12

        Dim qrSize As Double
        qrSize = Application.Min(ws.Rows(i).RowHeight, _
                                 ws.Columns(5).Width * 0.75 * 4)
        If qrSize < 60 Then qrSize = 70

        ' ── QR 삽입 ──────────────────────────────────────────
        Dim shapeName As String
        shapeName = "QR_plan_" & i

        On Error Resume Next
        Call QR_삽입_영구저장(ws, jsonStr, qrCell, qrSize, qrSize, shapeName)
        If Err.Number = 0 Then successCount = successCount + 1
        Err.Clear
        On Error GoTo 0

        packsArr = ""

다음행:
    Next i

    Application.ScreenUpdating = True
    Application.StatusBar = False

    MsgBox "✅ QR 생성 완료!" & Chr(10) & Chr(10) & _
           "• 생성: " & successCount & "개" & Chr(10) & _
           "• 파일 없음(건너뜀): " & (lastRow - 4 - successCount) & "개" & Chr(10) & Chr(10) & _
           "(E열에서 확인하세요)", vbInformation
End Sub

'=============================================================
' 네트워크 폴더 재귀 스캔 → 파일 목록 수집
' # 가 포함된 모든 Excel 파일을 "경로|수정일시" 형식으로 수집
'=============================================================
Sub 폴더_파일수집(folder As Object, fileList As Collection, depth As Long)
    On Error Resume Next
    Dim f As Object
    For Each f In folder.Files
        Dim ext As String
        ext = LCase(Right(f.Name, 4))
        If (ext = "xlsm" Or ext = "xlsx" Or ext = ".xls") Then
            If InStr(f.Name, "#") > 0 Then
                fileList.Add f.Path & "|" & CStr(f.DateLastModified)
            End If
        End If
    Next f
    If depth <= 1 Then Exit Sub
    Dim subFolder As Object
    For Each subFolder In folder.SubFolders
        Call 폴더_파일수집(subFolder, fileList, depth - 1)
    Next subFolder
End Sub

'=============================================================
' 파일 목록에서 reqCode 포함 파일 중 가장 최신 경로 반환
' 대소문자 구분 없이 검색 (LCase 비교)
'=============================================================
Function 최신파일_검색(fileList As Collection, reqCode As String) As String
    Dim bestPath As String
    Dim bestDate As Date
    Dim lowerCode As String
    lowerCode = LCase(reqCode)

    Dim item As Variant
    For Each item In fileList
        Dim parts() As String
        parts = Split(item, "|")
        If UBound(parts) < 1 Then GoTo 다음
        Dim fname As String
        fname = Mid(parts(0), InStrRev(parts(0), "\") + 1)
        If InStr(LCase(fname), lowerCode) > 0 Then
            Dim fDate As Date
            fDate = CDate(parts(1))
            If bestPath = "" Or fDate > bestDate Then
                bestPath = parts(0)
                bestDate = fDate
            End If
        End If
다음:
    Next item
    최신파일_검색 = bestPath
End Function

'=============================================================
' 파일명 전체 파싱
' 형식: {pack_from}-{pack_to}#{req_code}, {site}({company}).xlsm
'=============================================================
Sub 파일명_전체파싱(fname As String, _
                    ByRef company As String, ByRef site As String, _
                    ByRef packFrom As Long, ByRef packTo As Long)
    company = "" : site = "" : packFrom = 0 : packTo = 0
    On Error GoTo 파싱실패

    ' 확장자 제거
    Dim name As String
    name = fname
    Dim dotPos As Long
    dotPos = InStrRev(name, ".")
    If dotPos > 0 Then name = Left(name, dotPos - 1)
    ' 예: "1148-1150#0421-41-GGM, 가양동 CJ부지 업무복합시설(현대건설)"

    ' # 위치
    Dim hashPos As Long
    hashPos = InStr(name, "#")
    If hashPos = 0 Then Exit Sub

    ' 패킹 범위 (# 앞)
    Dim packRange As String
    packRange = Left(name, hashPos - 1)
    Dim dashPos As Long
    dashPos = InStr(packRange, "-")
    If dashPos = 0 Then Exit Sub

    On Error Resume Next
    packFrom = CLng(Left(packRange, dashPos - 1))
    packTo   = CLng(Mid(packRange, dashPos + 1))
    On Error GoTo 파싱실패
    If packFrom = 0 Or packTo = 0 Then Exit Sub

    ' # 뒤: "0421-41-GGM, 가양동 CJ부지 업무복합시설(현대건설)"
    Dim afterHash As String
    afterHash = Mid(name, hashPos + 1)

    Dim commaPos As Long
    commaPos = InStr(afterHash, ",")
    If commaPos = 0 Then Exit Sub

    ' 쉼표 뒤: " 가양동 CJ부지 업무복합시설(현대건설)"
    Dim siteCompany As String
    siteCompany = Trim(Mid(afterHash, commaPos + 1))

    ' 업체명: 마지막 ( ) 안
    Dim openP As Long, closeP As Long
    closeP = InStrRev(siteCompany, ")")
    openP  = InStrRev(siteCompany, "(")
    If openP > 0 And closeP > openP Then
        company = Trim(Mid(siteCompany, openP + 1, closeP - openP - 1))
        site    = Trim(Left(siteCompany, openP - 1))
    Else
        site = siteCompany
    End If

    Exit Sub
파싱실패:
    packFrom = 0 : packTo = 0
End Sub

'=============================================================
' 공통: QR API 생성 + 영구저장
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

    Dim shp As Shape
    For Each shp In ws.Shapes
        If shp.Name = shapeName Then shp.Delete : Exit For
    Next shp

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
