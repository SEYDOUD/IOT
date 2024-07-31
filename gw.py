from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import time
import serial

from random import randint




# ThingsBoard client configuration
TB_SERVER = "thingsboard.cloud"
TB_PORT = 1883
DEVICE_TOKEN = "t19v9MCQILdTBjklr6er"

# Location parameters
LATITUDE = 14.683860
LONGITUDE = -17.462075


def config_serial(serial_port, baud_rate=9600):
    return serial.Serial(serial_port, baudrate=baud_rate)


def read_serial(ser):
    return ser.readline().strip().decode()


def get_sensor_data(ser):
    raw_sensor = read_serial(ser)
    if raw_sensor[0] == "#":
        sensors_data = raw_sensor.split("#")[1]
        humidity = sensors_data.split(",")[0]
        temperature = sensors_data.split(",")[1]
        water_level = sensors_data.split(",")[2]
        if isinstance(humidity, (int, float)) and isinstance(temperature, (int, float)) and isinstance(water_level, (int, float)):
            return float(humidity), float(temperature) , float(water_level)
        else :
            print("ERROR: sensor data value NaN")
            return None, None
    else:
        print('ERROR: getting Arduino sensor values over serial')
        return None, None


def read_file():
    with open("device_data.txt", "r") as fd:
        lines = [line.rstrip() for line in fd]
        return lines


def get_sensor_data_from_file(line):
    if line[0] == "#":
        sensors_data = line.split("#")[1]
        humidity = sensors_data.split(",")[0]
        temperature = sensors_data.split(",")[1]
        water_level = sensors_data.split(",")[2]
        return float(humidity), float(temperature) , float(water_level)
    else:
        print('ERROR: getting Arduino sensor values over serial')
        return None, None


def tb_connect(addr, port, device_token):
    return TBDeviceMqttClient(addr, port, device_token)


def send_location(client, latitude, longitude):
    gps_coord = {"latitude": latitude, "longitude": longitude}
    print(f"Sending location {gps_coord}")
    result = client.send_attributes(gps_coord)
    if result.get() == 0:
        print("OK")
    else:
        print(f"ERROR --> {result.get()}")


def send_sensor_data(client, timestamp, humidity, temperature , water_level):
    telemetry_with_ts = {"ts": timestamp, "values": {"humidity": humidity, "temperature": temperature ,"water_level":water_level}}
    print(f"Sending telemetries {telemetry_with_ts}")
    result = client.send_telemetry(telemetry_with_ts)
    if result.get() == 0:
        print("OK")
    else :
        print(f"ERROR --> {result.get()}")


def main():
  
    sensor_data_from_file = read_file()
    number = 0

    # Setup ThingsBoard Server
    print(f"Connecting to {TB_SERVER}...")
    tb_client = tb_connect(TB_SERVER, TB_PORT, DEVICE_TOKEN)
    tb_client.max_inflight_messages_set(100)
    tb_client.connect()
    time.sleep(5)

    # Set attributes
    send_location(tb_client, LATITUDE, LONGITUDE)

    # Read sensor data and send it to thingsboard
    while True:
        timestamp = int(round(time.time() * 1000))

        # Data from file (from simulated sensor)
        humidity, temperature , water_level = get_sensor_data_from_file(sensor_data_from_file[number])
        number = number + 1
        if number >= len(sensor_data_from_file):
            number = 0

        if humidity and temperature and water_level:
            send_sensor_data(tb_client, timestamp, humidity, temperature , water_level)

        # Pause à des fin de test (à supprimer plus tard)
        time.sleep(10)


if __name__ == "__main__":
    main()

