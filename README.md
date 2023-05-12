# Intro

Start/stop systemd user service based on USB bind/unbind event.

Or more precisely:

Monitor dbus for USB events and if a device matching pre-selected VID/PID
is connected/disconnected, start/stop a systemd user service respectively.

# Setup

Using pipx:

> pipx install systemudev-usb-monitor

Once installed, just run:

> systemudev-usb-monitor

# Configuration

You'll find an example config file under:

> config/config_example.toml

Modify it, to fit your needs and place it under:

> $XDG_CONFIG_HOME/systemudev-usb-monitor/config.toml

Note: Usually, $XDG_CONFIG_HOME resolves to ~/.config
