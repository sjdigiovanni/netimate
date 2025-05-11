# SPDX-License-Identifier: MPL-2.0
SHOW_VERSION_RAW = """Cisco IOS XE Software, Version 16.09.01
Cisco IOS Software [Fuji], ASR1000 Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.9.1, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2018 by Cisco Systems, Inc.
Compiled Tue 17-Jul-18 07:01 by mcpre

R1 uptime is 3 weeks, 2 days, 1 hour, 5 minutes
System returned to ROM by reload at 15:45:12 UTC Mon Jan 1 2018
System image file is "bootflash:asr1000-universalk9.16.09.01.SPA.bin"
"""

SHOW_VERSION_PARSED = [
    {
        "SOFTWARE_IMAGE": "X86_64BI_LINUX-ADVENTERPRISEK9-M",
        "VERSION": "17.12.1",
        "RELEASE": "fc5",
        "ROMMON": "Bootstrap",
        "HOSTNAME": "R1",
        "UPTIME": "1 day, 17 hours, 17 minutes",
        "UPTIME_YEARS": "",
        "UPTIME_WEEKS": "",
        "UPTIME_DAYS": "1",
        "UPTIME_HOURS": "17",
        "UPTIME_MINUTES": "17",
        "RELOAD_REASON": "Unknown reason",
        "RUNNING_IMAGE": "/x86_64_crb_linux-adventerprisek9-ms",
        "HARDWARE": [],
        "SERIAL": ["131184643"],
        "CONFIG_REGISTER": "0x0",
        "MAC_ADDRESS": [],
        "RESTARTED": "",
    }
]

SHOW_ENVIRONMENT_RAW = """
Switch 1 FAN is OK
Switch 1: SYSTEM TEMPERATURE is OK
"""

SHOW_ENVIRONMENT_PARSED = {"summary": ["FAN is OK", "SYSTEM TEMPERATURE is OK"]}

SHOW_IP_INTERFACE_BRIEF_RAW = """
Interface              IP-Address      OK? Method Status                Protocol
Ethernet0/0           192.168.1.1     YES manual up                    up
Ethernet0/1           unassigned      YES unset  administratively down down
"""

SHOW_IP_INTERFACE_BRIEF_PARSED = [
    {"INTERFACE": "Ethernet0/0", "IP_ADDRESS": "192.168.1.1", "STATUS": "up", "PROTO": "up"},
    {
        "INTERFACE": "Ethernet0/1",
        "IP_ADDRESS": "unassigned",
        "STATUS": "administratively down",
        "PROTO": "down",
    },
]

SHOW_LOGGING_RAW = """
*Apr 24 02:28:38.781: %SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: cisco]
*Apr 24 02:28:38.781: %SSH-5-SSH2_USERAUTH: User 'cisco' authentication for SSH2 Session
*Apr 24 02:28:41.766: %SSH-5-SSH2_CLOSE: SSH2 Session from 192.168.254.11 (tty = 0) for user 
"""

SHOW_LOGGING_PARSED = [
    {
        "NUMBER": "",
        "MONTH": "Apr",
        "DAY": "25",
        "TIME": "01:43:11.816",
        "TIMEZONE": "",
        "FACILITY": "SSH",
        "SEVERITY": "5",
        "MNEMONIC": "SSH2_SESSION",
        "MESSAGE": [
            "SSH2 Session request from 192.168.254.11 (tty = 0) using crypto cipher 'chacha20-poly1305@openssh.com', hmac 'hmac-sha2-256-etm@openssh.com' Succeeded"
        ],
    },
    {
        "NUMBER": "",
        "MONTH": "Apr",
        "DAY": "25",
        "TIME": "01:43:12.160",
        "TIMEZONE": "",
        "FACILITY": "SEC_LOGIN",
        "SEVERITY": "5",
        "MNEMONIC": "LOGIN_SUCCESS",
        "MESSAGE": [
            "Login Success [user: cisco] [Source: 192.168.254.11] [localport: 22] at 01:43:12 UTC Fri Apr 25 2025"
        ],
    },
]

SHOW_MEMORY_STATS_RAW = """
Processor  7FBE37EC7010   831753672   131607768   700145904   699951928   699608260
"""

SHOW_MEMORY_STATS_PARSED = [
    {
        "USED_BYTES": 131607768,
        "TOTAL_BYTES": 831753672,
    }
]

SHOW_PROCESS_CPU_RAW = """
CPU utilization for five seconds: 2%/0%; one minute: 1%; five minutes: 0%
"""

SHOW_PROCESS_CPU_PARSED = [
    {
        "cpu_5s": 2,
        "cpu_1m": 1,
        "cpu_5m": 0,
    }
]
