$DefaultIndex=Get-NetRoute -DestinationPrefix 0.0.0.0/0|Sort-Object {$_.RouteMetric+(Get-NetIPInterface -AssociatedRoute $_).InterfaceMetric}|Select-Object -First 1 -ExpandProperty InterfaceIndex
(Get-NetConnectionProfile -InterfaceIndex $DefaultIndex).Name
