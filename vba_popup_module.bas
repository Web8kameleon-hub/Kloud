' ============================================================================
' 🔷 KLOUD VBA POP-UP MODULE
' ============================================================================
' Excel ∞ Notification System
' 
' Purpose: Auto pop-up when Status changes to READY/APPROVED/BAKED
' 
' INSTALLATION:
' 1. Open Excel file → Press Alt+F11 (VBA Editor)
' 2. Double-click "Sheet1" (or your data sheet) in Project Explorer
' 3. Paste this entire code
' 4. Close VBA Editor (Ctrl+Q)
' 5. Save as .xlsm (macro-enabled workbook)
'
' REQUIREMENTS:
' - Status column must be Column I (9th column)
' - Macros must be enabled
' ============================================================================

Option Explicit

' ============================================================================
' CONFIGURATION - Adjust these as needed
' ============================================================================

Const STATUS_COLUMN As Integer = 9          ' Column I = Status
Const ENDPOINT_COLUMN As Integer = 4        ' Column D = Endpoint
Const DESCRIPTION_COLUMN As Integer = 5     ' Column E = Description
Const FOLDER_COLUMN As Integer = 2          ' Column B = Folder
Const METHOD_COLUMN As Integer = 3          ' Column C = Method

' Status values that trigger notification
Const READY_STATUSES As String = "READY,APPROVED,BAKED"

' ============================================================================
' MAIN EVENT HANDLER - Triggers when any cell changes
' ============================================================================

Private Sub Worksheet_Change(ByVal Target As Range)
    Dim StatusCell As Range
    Dim NewStatus As String
    Dim Endpoint As String
    Dim Description As String
    Dim Folder As String
    Dim Method As String
    Dim Row As Long
    Dim Message As String
    
    ' Only process if change is in Status column
    If Target.Column <> STATUS_COLUMN Then Exit Sub
    
    ' Only process single cell changes
    If Target.Cells.Count > 1 Then Exit Sub
    
    ' Get the new status value
    NewStatus = UCase(Trim(Target.Value))
    
    ' Check if it's a READY status
    If InStr(1, READY_STATUSES, NewStatus, vbTextCompare) > 0 Then
        ' Get row details
        Row = Target.Row
        Endpoint = Cells(Row, ENDPOINT_COLUMN).Value
        Description = Cells(Row, DESCRIPTION_COLUMN).Value
        Folder = Cells(Row, FOLDER_COLUMN).Value
        Method = Cells(Row, METHOD_COLUMN).Value
        
        ' Build notification message
        Message = "🎉 API READY FOR DEPLOYMENT" & vbCrLf & vbCrLf
        Message = Message & "━━━━━━━━━━━━━━━━━━━━━━━━━━━" & vbCrLf
        Message = Message & "📁 Folder: " & Folder & vbCrLf
        Message = Message & "🔸 Method: " & Method & vbCrLf
        Message = Message & "🔗 Endpoint: " & Endpoint & vbCrLf
        Message = Message & "📝 Description: " & Description & vbCrLf
        Message = Message & "✅ Status: " & NewStatus & vbCrLf
        Message = Message & "━━━━━━━━━━━━━━━━━━━━━━━━━━━" & vbCrLf & vbCrLf
        Message = Message & "This API is now ready for production!"
        
        ' Show pop-up
        MsgBox Message, vbInformation + vbOKOnly, "Kloud API Ready"
        
        ' Optional: Add visual formatting
        Call HighlightReadyRow(Row)
        
        ' Optional: Log to separate sheet
        Call LogNotification(Row, NewStatus, Endpoint)
    End If
End Sub

' ============================================================================
' VISUAL FEEDBACK - Highlights the ready row
' ============================================================================

Private Sub HighlightReadyRow(Row As Long)
    Dim LastCol As Integer
    LastCol = Cells(1, Columns.Count).End(xlToLeft).Column
    
    ' Add green background to entire row
    Range(Cells(Row, 1), Cells(Row, LastCol)).Interior.Color = RGB(198, 239, 206)
    
    ' Make status cell bold with dark green
    Cells(Row, STATUS_COLUMN).Font.Bold = True
    Cells(Row, STATUS_COLUMN).Font.Color = RGB(0, 97, 0)
End Sub

' ============================================================================
' NOTIFICATION LOG - Logs all READY notifications to separate sheet
' ============================================================================

Private Sub LogNotification(Row As Long, Status As String, Endpoint As String)
    Dim LogSheet As Worksheet
    Dim NextRow As Long
    
    On Error Resume Next
    Set LogSheet = Worksheets("Notification_Log")
    On Error GoTo 0
    
    ' Create log sheet if it doesn't exist
    If LogSheet Is Nothing Then
        Set LogSheet = Worksheets.Add(After:=Worksheets(Worksheets.Count))
        LogSheet.Name = "Notification_Log"
        
        ' Add headers
        LogSheet.Cells(1, 1).Value = "Timestamp"
        LogSheet.Cells(1, 2).Value = "Row"
        LogSheet.Cells(1, 3).Value = "Endpoint"
        LogSheet.Cells(1, 4).Value = "Status"
        LogSheet.Cells(1, 5).Value = "User"
        
        ' Format headers
        LogSheet.Range("A1:E1").Font.Bold = True
        LogSheet.Range("A1:E1").Interior.Color = RGB(68, 114, 196)
        LogSheet.Range("A1:E1").Font.Color = RGB(255, 255, 255)
    End If
    
    ' Find next empty row
    NextRow = LogSheet.Cells(LogSheet.Rows.Count, 1).End(xlUp).Row + 1
    
    ' Add log entry
    LogSheet.Cells(NextRow, 1).Value = Now
    LogSheet.Cells(NextRow, 2).Value = Row
    LogSheet.Cells(NextRow, 3).Value = Endpoint
    LogSheet.Cells(NextRow, 4).Value = Status
    LogSheet.Cells(NextRow, 5).Value = Environ("USERNAME")
End Sub

' ============================================================================
' MANUAL NOTIFICATION - Call this to show notification for selected cell
' ============================================================================

Public Sub ShowNotificationForSelected()
    Dim Cell As Range
    Set Cell = Selection
    
    If Cell.Column = STATUS_COLUMN Then
        ' Trigger the change event manually
        Call Worksheet_Change(Cell)
    Else
        MsgBox "Please select a cell in the Status column (Column I)", vbExclamation
    End If
End Sub

' ============================================================================
' BATCH CHECK - Check all rows for READY status and notify
' ============================================================================

Public Sub CheckAllReadyStatuses()
    Dim LastRow As Long
    Dim Row As Long
    Dim ReadyCount As Integer
    Dim StatusValue As String
    
    LastRow = Cells(Rows.Count, STATUS_COLUMN).End(xlUp).Row
    ReadyCount = 0
    
    For Row = 2 To LastRow
        StatusValue = UCase(Trim(Cells(Row, STATUS_COLUMN).Value))
        If InStr(1, READY_STATUSES, StatusValue, vbTextCompare) > 0 Then
            Call HighlightReadyRow(Row)
            ReadyCount = ReadyCount + 1
        End If
    Next Row
    
    MsgBox "Found " & ReadyCount & " APIs with READY status!", vbInformation
End Sub

' ============================================================================
' STATISTICS - Quick summary of all statuses
' ============================================================================

Public Sub ShowStatusSummary()
    Dim LastRow As Long
    Dim Row As Long
    Dim StatusDict As Object
    Dim StatusValue As String
    Dim Key As Variant
    Dim Message As String
    
    Set StatusDict = CreateObject("Scripting.Dictionary")
    LastRow = Cells(Rows.Count, STATUS_COLUMN).End(xlUp).Row
    
    For Row = 2 To LastRow
        StatusValue = UCase(Trim(Cells(Row, STATUS_COLUMN).Value))
        If StatusValue <> "" Then
            If StatusDict.Exists(StatusValue) Then
                StatusDict(StatusValue) = StatusDict(StatusValue) + 1
            Else
                StatusDict.Add StatusValue, 1
            End If
        End If
    Next Row
    
    Message = "📊 API STATUS SUMMARY" & vbCrLf & vbCrLf
    Message = Message & "━━━━━━━━━━━━━━━━━━━━" & vbCrLf
    
    For Each Key In StatusDict.Keys
        Message = Message & Key & ": " & StatusDict(Key) & vbCrLf
    Next Key
    
    Message = Message & "━━━━━━━━━━━━━━━━━━━━" & vbCrLf
    Message = Message & "Total APIs: " & (LastRow - 1)
    
    MsgBox Message, vbInformation, "Kloud API Summary"
End Sub

' ============================================================================
' QUICK ACTIONS - Helper functions for common tasks
' ============================================================================

Public Sub MarkSelectedAsReady()
    Dim Cell As Range
    Set Cell = Cells(Selection.Row, STATUS_COLUMN)
    Cell.Value = "READY"
End Sub

Public Sub MarkSelectedAsPending()
    Dim Cell As Range
    Set Cell = Cells(Selection.Row, STATUS_COLUMN)
    Cell.Value = "PENDING"
End Sub

Public Sub MarkSelectedAsError()
    Dim Cell As Range
    Set Cell = Cells(Selection.Row, STATUS_COLUMN)
    Cell.Value = "ERROR"
End Sub

