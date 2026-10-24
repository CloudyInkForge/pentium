$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime] | Out-Null
$methods = [System.WindowsRuntimeSystemExtensions].GetMethods()
$asTaskOp = ($methods | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function AwaitOp($WinRtTask, $ResultType) {
  $asTask = $asTaskOp.MakeGenericMethod($ResultType)
  $netTask = $asTask.Invoke($null, @($WinRtTask))
  try { $netTask.Wait(-1) | Out-Null } catch {
    Write-Host ("WAIT FAIL: " + $netTask.Exception.InnerException.GetType().FullName + ": " + $netTask.Exception.InnerException.Message)
    throw
  }
  $netTask.Result
}
$file = AwaitOp ([Windows.Storage.StorageFile]::GetFileFromPathAsync("D:\CloudyInkForge\pentium\2611\2611.pdf")) ([Windows.Storage.StorageFile])
Write-Host ("file ok: " + $file.Name)
$pdf = AwaitOp ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
Write-Host ("pdf ok: " + $pdf.PageCount)
