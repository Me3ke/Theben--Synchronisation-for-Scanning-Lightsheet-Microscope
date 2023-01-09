Param(
    [string]$hc1,
    [string]$hc2
)
$foundFirst = $false
$foundSecond = $false
$ports = (Get-WMIObject Win32_SerialPort).DeviceID
$ports.GetType()

if ($ports.GetType() -eq [System.Object[]]) {
    forEach ($port in $ports) {
        if ($port -eq $hc1) {
            $foundFirst = $true
        }
        if ($port -eq $hc2) {
            $foundSecond = $true
        }
    }
} else {
    return $false
}
if ($foundFirst -and $foundSecond) {
    return $true
} else {
    return $false
}