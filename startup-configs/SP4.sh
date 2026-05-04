#!/bin/sh
ip addr flush dev eth1 2>/dev/null; ip addr add 10.1.1.2/30 dev eth1; ip link set eth1 up
ip addr flush dev eth2 2>/dev/null; ip addr add 10.2.1.2/30 dev eth2; ip link set eth2 up
ip addr flush dev eth3 2>/dev/null; ip addr add 10.3.1.2/30 dev eth3; ip link set eth3 up
ip addr flush dev eth4 2>/dev/null; ip addr add 10.4.1.1/30 dev eth4; ip link set eth4 up
sleep 2
bird -c /etc/bird.conf
