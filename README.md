# Parental Monitoring System

A simple parental monitoring application that allows parents to view what their children are typing on their devices. This project is intended for parents to ensure their children's online safety.

## Project Overview

This project provides a real-time keystroke monitoring system with two main components:
1.  **Parental Control Server (The Parent's Device)**: Receives and logs keystrokes from the child's device for review.
2.  **Child Monitoring Client (The Child's Device)**: Monitors keyboard activity and securely transmits it to the parent's server.

Both the client and server have CLI and GUI versions to suit different technical preferences.

## Features

- **Real-time Monitoring**: Parents can see what's being typed as it happens.
- **Activity Logging**: Keystrokes are logged with timestamps and device names for later review.
- **GUI for Easy Use**: Simple graphical interfaces for parents to manage connections and view logs.
- **Reliable Connection**: The client automatically attempts to reconnect if the connection to the parent's device is interrupted.
- **Multi-Device Support**: A single parent server can monitor multiple children's devices simultaneously.

## Files

- [keylog_server.py](file:///c:/Users/salta/OneDrive/Desktop/Coding/keylogger/keylog_server.py): Command-line version of the parent server.
- [keylogger_server_gui.py](file:///c:/Users/salta/OneDrive/Desktop/Coding/keylogger/keylogger_server_gui.py): GUI version of the parent server.
- [keylogger_client.py](file:///c:/Users/salta/OneDrive/Desktop/Coding/keylogger/keylogger_client.py): Command-line version of the child monitoring client.
- [keylogger_client_gui.py](file:///c:/Users/salta/OneDrive/Desktop/Coding/keylogger/keylogger_client_gui.py): GUI version of the child monitoring client.
- [server_keylog.txt](file:///c:/Users/salta/OneDrive/Desktop/Coding/keylogger/server_keylog.txt): Log file on the parent's device where monitored activity is stored.

## Prerequisites

- Python 3.x
- `keyboard` library: `pip install keyboard`
- `tkinter` library (usually comes pre-installed with Python)

## Usage

### 1. Set up the Parent's Device (Server)

Run the server on the parent's computer to receive data.

**Using GUI (Recommended):**
```bash
python keylogger_server_gui.py
```
**Using CLI:**
```bash
python keylog_server.py
```

The server listens on port `5555` by default. Note the IP address of the parent's device.

### 2. Set up the Child's Device (Client)

Run the monitoring client on the child's computer/device.

**Using GUI:**
```bash
python keylogger_client_gui.py
```
Enter the parent's device IP address and port, then click "Connect" and "Start Monitoring".

**Using CLI:**
```bash
python keylogger_client.py [parent_ip] [port]
```
Example: `python keylogger_client.py 192.168.1.10 5555`

## Legal and Ethical Use

**IMPORTANT: THIS SOFTWARE IS DESIGNED FOR PARENTAL MONITORING ONLY.**

The use of this software must comply with local laws and regulations regarding privacy and monitoring. It is intended for parents to supervise their minor children for safety reasons. Unauthorized monitoring of adults or any illegal use is strictly prohibited. The author(s) assume no liability for misuse of this program.
