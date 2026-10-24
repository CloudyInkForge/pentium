$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFolder,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
[Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime] | Out-Null
$methods = [System.WindowsRuntimeSystemExtensions].GetMethods()
$asTaskOp = ($methods | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
$asTaskAction = ($methods | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]
function AwaitOp($WinRtTask, $ResultType) {
  $asTask = $asTaskOp.MakeGenericMethod($ResultType)
  $netTask = $asTask.Invoke($null, @($WinRtTask))
  try { $netTask.Wait(-1) | Out-Null } catch {
    Write-Host ("WAIT FAIL: " + $netTask.Exception.InnerException.GetType().FullName + ": " + $netTask.Exception.InnerException.Message); throw }
  $netTask.Result
}
$pdfPath = 'D:\CloudyInkForge\pentium\2611\2611.pdf'
$outDir = 'D:\CloudyInkForge\pentium\_tmp\pdfpng'
$pdf = $null
$file = AwaitOp ([Windows.Storage.StorageFile]::GetFileFromPathAsync($pdfPath)) ([Windows.Storage.StorageFile])
$pdf = AwaitOp ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
try {
  $folder = AwaitOp ([Windows.Storage.StorageFolder]::GetFolderFromPathAsync($outDir)) ([Windows.Storage.StorageFolder])
  Write-Host ("folder ok: " + $folder.Name)
} catch { Write-Host ("FOLDER FAIL: " + $_.Exception.Message) }
$folder = AwaitOp ([Windows.Storage.StorageFolder]::GetFolderFromPathAsync($outDir.Replace('/','\'))) ([Windows.Storage.StorageFolder])
$page = $pdf.GetPage([uint32]0)
$outFile = AwaitOp ($folder.CreateFileAsync('p00.png', [Windows.Storage.CreationCollisionOption]::ReplaceExisting)) ([Windows.Storage.StorageFile])
Write-Host ("outfile ok: " + $outFile.Name)
$stream = AwaitOp ($outFile.OpenAsync([Windows.Storage.FileAccessMode]::ReadWrite)) ([Windows.Storage.Streams.IRandomAccessStream])
Write-Host "stream ok"
$opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions
$opts.DestinationWidth = [uint32]([double]$page.Size.Width * 2.0)
$asTask = $asTaskAction.Invoke($null, @($page.RenderToStreamAsync($stream, $opts)))
$asTask.Wait(-1) | Out-Null
$stream.Dispose(); $page.Dispose()
Write-Host "render ok"
