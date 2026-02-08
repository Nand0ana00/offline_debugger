# Offline AI Debugger

An offline, lightweight AI-powered code debugger designed for low-spec devices.

## Features
- Detects undefined variables
- Detects unused variables
- Detects unreachable code
- Works fully offline
- Memory efficient

## Installation
Clone the repository:

git clone https://github.com/Nand0ana00/offline_debugger.git
cd offline_debugger

## Usage

Run the debugger on the sample tests:

python -m core.engine tests

## Sample Output

[HIGH] UndefinedVariable
File: tests/test2.py
Line: 1
Message: Variable 'a' used before assignment
