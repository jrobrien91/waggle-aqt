import serial 
import datetime
import parse

# Set Defaults
DEVICE = "/dev/ttyUSB0"
BAUD_RATE = 115200
TIME_OUT = 1

def parse_values(sample, **kwargs):
    # Note: The AQT ASCII data contains which specific variables are in the string
    # as the second to last comma separated value within the line
    print(sample)
    print(list(sample))
    sample.decode('unicode_escape')
    if sample.startswith(b'20'):
        data = parse.search("{ti}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{.3F}," +
                            "{.3F}," +
                            "{.3F}," +
                            "{.3F}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{.1F}," +
                            "{w}," +
                            "{d}\r\n" ,
                            sample.decode('utf-8')
                            )
        # Parse the variable names from the datastring
        # Captured by the {w} flag
        parms = data['w'].split(':')
        # Convert the variables to floats
        strip = [float(var) for var in data]
        # Create a dictionary to match the parameters and variables
        ndict = dict(zip(parms, strip))
        # Add the AQT datetime to the dictionary
        ndict['datetime'] = data['ti']
        ndict['uptime'] = int(data['d'])

    else:
        print('parse - else', sample)
        ndict = None
                 
    return ndict


with serial.Serial(DEVICE, baudrate=BAUD_RATE, timeout=TIME_OUT) as dev:
    while True:
        try:
            #line = dev.read_until(b'2023')
            line = dev.readline()
            print(line)
            if len(line) > 0: 
                print(datetime.datetime.now())
                sample = parse_values(line)
                print(sample)
        except Exception as e:
            print("keyboard interrupt")
            print(e)
            break

