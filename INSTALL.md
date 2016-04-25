# Installation and configuration

Here are some useful config fragments for starting and displaying the dashboard
automatically on a Linux box. It assumes the distro is using GNOME and systemd
but should hopefully be useful, if only as a reference.

## Starting the container at boot time

Create a systemd service in `/etc/systemd/system/xs-dev-dash.service` with the
following contents:

```systemd
[Unit]
Description=Dev Dashboard using Grafana
Requires=docker.service
After=docker.service
ConditionPathExists=<PATH_TO_REPO>
ConditionPathIsDirectory=<PATH_TO_REPO>

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/usr/bin/make -C <PATH_TO_REPO> run
ExecStop=/usr/bin/make -C <PATH_TO_REPO> stop

[Install]
WantedBy=multi-user.target
```

and enable it with `systemctl enable xs-dev-dash.service`.

If you want to start Firefox at boot time under a GNOME desktop environment
then you can create `~/.config/autostart/firefox.desktop` with the following:

```
[Desktop Entry]
Encoding=UTF-8
Name=Firefox dashboard

Name[pt]=Firefox

TryExec=firefox
Exec=firefox localhost/dashboard/file/dash.json
X-Gnome-Vfs-System=gio
Terminal=false
StartupNotify=true
Type=Application
OnlyShowIn=GNOME;
```

It may also be worth installing `unclutter` to auto-hide the mouse cursor when
idle which is available for most platforms. An autostart `.desktop` file can be
created similar to the above `firefox.desktop`.
