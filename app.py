import serial
import argparse
import parse
import logging
 
from waggle.plugin import Plugin, get_timestamp

def parse_values(sample, **kwargs):
    # Note: The AQT ASCII data contains which specific variables are in the string
    # as the second to last comma separated value within the line
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
        ndict = None

    return ndict


def start_publishing(args, plugin, dev, **kwargs):
    """
    start_publishing initializes the Visala WXT530
    Begins sampling and publishing data

    Functions
    ---------


    Modules
    -------
    plugin
    logging
    sched
    parse
    """
    # Note: AQT ASCII interface configuration described in manual
    line = dev.readline()
    # Note: AQT has 1 min data output, need to check if bytes are returned
    if len(line) > 0: 
        # Define the timestamp
        timestamp = get_timestamp()
        logging.debug("Read transmitted data")
        # Check for valid command
        sample = parse_values(line) 
    
        # If valid parsed values, send to publishing
        if sample:
            # setup and publish to the node
            if kwargs['node_interval'] > 0:
                # publish each value in sample
                for name, key in kwargs['names'].items():
                    try:
                        value = sample[key]
                    except KeyError:
                        continue
                    # Update the log
                    if kwargs.get('debug', 'False'):
                        print('node', timestamp, name, value, kwargs['units'][name], type(value))
                    logging.info("node publishing %s %s units %s type %s", name, value, kwargs['units'][name], str(type(value)))
                    plugin.publish(name,
                                   value=value,
                                   meta={"units" : kwargs['units'][name],
                                         "sensor" : "vaisala-aqt530",
                                         "missing" : '-9999.9',
                                         "description" : kwargs['description'][name]
                                         },
                                   scope="node",
                                   timestamp=timestamp
                                   )
            # setup and publish to the beehive                        
            if kwargs['beehive_interval'] > 0:
                # publish each value in sample
                for name, key in kwargs['names'].items():
                    try:
                        value = sample[key]
                    except KeyError:
                        continue
                    # Update the log
                    if kwargs.get('debug', 'False'):
                        print('beehive', timestamp, name, value, kwargs['units'][name], type(value))
                    logging.info("beehive publishing %s %s units %s type %s", name, value, kwargs['units'][name], str(type(value)))
                    plugin.publish(name,
                                   value=value,
                                   meta={"units" : kwargs['units'][name],
                                         "sensor" : "vaisala-aqt530",
                                         "missing" : '-9999.9',
                                         "description" : kwargs['description'][name]
                                        },
                                   scope="beehive",
                                   timestamp=timestamp
                                  )

def main(args):
    publish_names = {"aqt.env.temp" : "T",
                     "aqt.env.pressure" : "P",
                     "aqt.env.humidity" : "H",
                     "aqt.gas.no2" : "NO2",
                     "aqt.gas.co" : "CO",
                     "aqt.gas.ozone" : "O3",
                     "aqt.gas.no" : "NO",
                     "aqt.gas.so2" : "SO2",
                     "aqt.gas.h2s" : "H2S",
                     "aqt.particle.pm1" : "PM1",
                     "aqt.particle.pm2.5" : "PM2.5",
                     "aqt.particle.pm10" : "PM10",
                     "aqt.house.datetime" : "datetime",
                     "aqt.house.uptime" : "uptime",
                    }

    units = {"aqt.env.temp" : "degrees Celsius",
             "aqt.env.pressure" : "hPa",
             "aqt.env.humidity" : "percent relative humidity",
             "aqt.gas.no2" : "ppm",
             "aqt.gas.co" : "ppm",
             "aqt.gas.ozone" : "ppm",
             "aqt.gas.no" : "ppm",
             "aqt.gas.so2" : "ppm",
             "aqt.gas.h2s" : "ppm", 
             "aqt.particle.pm1" : "microgram per cubic meter",
             "aqt.particle.pm2.5" : "microgram per cubic meter",
             "aqt.particle.pm10" : "microgram per cubic meter",
             "aqt.house.datetime" : "UTC time",
             "aqt.house.uptime" : "seconds"
             }
    
    description = {"aqt.env.temp" : "Ambient Temperature",
                   "aqt.env.pressure" : "Ambient Atmospheric Pressure",
                   "aqt.env.humidity" : "Ambient Relative Humidity",
                   "aqt.gas.no2" : "Nitrogen Dioxide Gas Concentration",
                   "aqt.gas.co" : "Carbon Monoxide Gas Concentration",
                   "aqt.gas.ozone" : "Ozone Gas Concentration",
                   "aqt.gas.no" : "Nitric Oxide Gas Concentration",
                   "aqt.gas.so2" : "Sulfur Dioxide Gas Concentration",
                   "aqt.gas.h2s" : "Hydrogen Sulfide Gas Concentration", 
                   "aqt.particle.pm1" : "Particulate Matter less than 1 microns in diameter",
                   "aqt.particle.pm2.5" : "Particulate Matter less than 2.5 microns in diameter",
                   "aqt.particle.pm10" : "Particulate Matter less than 10 microns in diameter",
                   "aqt.house.datetime" : "UTC time in YYYY-MM-DDTHH:MM:SS format",
                   "aqt.house.uptime" : "Time in seconds since instrument startup"
                  }

    with Plugin() as plugin, serial.Serial(args.device, baudrate=args.baud_rate, timeout=1.0) as dev:
        while True:
            try:
                start_publishing(args, 
                                 plugin,
                                 dev,
                                 node_interval=args.node_interval,
                                 beehive_interval=args.beehive_interval,
                                 names=publish_names,
                                 units=units,
                                 description=description
                                 )
            except Exception as e:
                print("keyboard interrupt")
                print(e)
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Plugin for Pushing Viasala WXT 2D anemometer data through WSN")

    parser.add_argument("--debug",
                        action="store_true",
                        dest='debug',
                        help="enable debug logs"
                        )
    parser.add_argument("--device",
                        type=str,
                        dest='device',
                        default="/dev/ttyUSB3",
                        help="serial device to use"
                        )
    parser.add_argument("--baudrate",
                        type=int,
                        dest='baud_rate',
                        default=115200,
                        help="baudrate to use"
                        )
    parser.add_argument("--node-publish-interval",
                        default=1.0,
                        dest='node_interval',
                        type=float,
                        help="interval to publish data to node " +
                             "(negative values disable node publishing)"
                        )
    parser.add_argument("--beehive-publish-interval",
                        default=1.0,
                        dest='beehive_interval',
                        type=float,
                        help="interval to publish data to beehive " +
                             "(negative values disable beehive publishing)"
                        )
    args = parser.parse_args()


    main(args)
