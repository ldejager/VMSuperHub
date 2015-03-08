VMSuperHub Statistics
=====================

To get up and running, install the required additional modules through pip.

pip install -r requirements.txt

The script will grab power levels and SNR information from your Virgin Media SuperHub and write it out to disk as well
as a carbon (graphite) instance from which you can create graphs.

The process can be monitored using supervisor and the relevant configuration file is also attached to the project.


```
root@graphite:/opt/scripts/VMSuperHub# supervisorctl
vmsuperhub                       RUNNING    pid 14914, uptime 0:00:12
```

![alt text](https://raw.githubusercontent.com/ldejager/VMSuperHub/master/VMSuperHub.png "VMSuperHub")
