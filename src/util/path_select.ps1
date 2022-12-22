[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null

 $OFD = New-Object System.Windows.Forms.OpenFileDialog
 $OFD.initialDirectory = [Environment]::GetFolderPath('Desktop')
 $OFD.filter = "All files (*.*)| *.*"
 $OFD.ShowDialog() | Out-Null
 return $OFD.filename