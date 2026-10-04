Voice-Controlled Arduino Lights

This project uses OpenAI Whisper Base from Hugging Face to recognize voice commands and control lights connected to an Arduino.

The user can say commands to:

Turn the red light on
Turn the green light on
Turn the blue light on
Turn all lights on
Turn all lights off
How It Works

The microphone records the user's voice, Whisper converts the speech into text, and the Python program sends the appropriate command to the Arduino through a serial connection.

Requirements
Python
Arduino
Microphone
openai/whisper-base
Hugging Face Transformers
PyTorch
PySerial
SoundDevice
Example

"Turn on the blue light"

The program recognizes the command and tells the Arduino to turn on the blue LED.
