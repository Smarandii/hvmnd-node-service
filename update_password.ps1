echo $newPassword | anydesk --set-password;
>> Start-Sleep -Seconds 1;
>> $serviceName="AnyDesk";
>> if((Get-Service -Name $serviceName).Status -eq "Running")
>> {Restart-Service -Name $serviceName;}