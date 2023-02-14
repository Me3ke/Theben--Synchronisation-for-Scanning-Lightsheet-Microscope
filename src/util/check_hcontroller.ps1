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

<#
in python
    def verify_hcontroller_connected(self):
        # TODO vielleicht check nach allen serialports (auch laser, kamera)
        process = subprocess.Popen(["powershell.exe", ".\\src\\util\\check_hcontroller.ps1",
                                    self.setup.serial_port_hc_1, self.setup.serial_port_hc_2], stdout=subprocess.PIPE)
        p_out, p_err = process.communicate()
        return_value = p_out.decode().strip()
        print(return_value)
        return return_value
#>