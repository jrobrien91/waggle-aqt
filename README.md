# Vaisala AQT530 Waggle Plugin
Waggle Sensor Plug-In for the [Vaisala AQT530 Series Air Quality Transmitter](https://www.vaisala.com/en/products/weather-environmental-sensors/air-quality-transmitter-aqt530-urban-industrial-systems)

Depending on the configuration of the instrument, the AQT530 provides observations on meteorological conditions, including particulate matter (PM2.5, PM10) and gas species concentrations(NO, NO2, O3, CO). 

[Waggle Sensor Information](https://github.com/waggle-sensor)

## Determine the Serial Port
The AQT530 utilzies an RS-485 serial connection to transmit data (RS-232 serial connection for instrument maintenance).

Therefore, to determine which port the instrument is plugged into, PySerial offers a handy toollist to list all serial ports currnetly in use.
```bash
python -m serial.tools.list_ports
```

The default serial settings for the RS-485 interface are:
1. Baud Rate = 115200
1. Data Bits = 8
1. Parity = None
1. Stop Bits = 1

## Testing 

Similar to the [Vaisala WXT536 plugin](https://portal.sagecontinuum.org/apps/app/jrobrien/waggle-wxt536) a docker container will be setup via Makefile 

### 1) Build the Container
```bash
make build
```

### 2) Deploy the Container in Background
```bash
make deploy
```

### 3) Test the plugin
```bash
make run
