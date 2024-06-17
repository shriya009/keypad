import serial
import time
print('Please check the connections before start')
print(input('press enter to start'))
time.sleep(1)
def read_config():
    try:
        with open('config.txt', 'r') as config_file:
            for line in config_file:
                if line.startswith('attport:'):
                    port_name = line.split(':')[-1].strip()
                    return port_name
            print('Error: Port not found in config file.')
            return None
    except Exception as e:
        print(f'Error reading config file: {e}')
        return None

def initialize_serial(port, baudrate=9600, timeout=1):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f'Serial connection established on {port}')
        return ser
    except Exception as e:
        print(f'Error: Check the COM port in Device Manager and change in the config file. Error: {e}')
        return None

def close_serial(ser):
    if ser:
        ser.close()
        print('Serial connection closed')

def led(ser):    
    try:
        # Test: RGB LED check
        user_in=''
        for i in range(4):
            cmd = f'AT+TLED={i+1}\r\n'
            time.sleep(0.25)
            ser.write(cmd.encode('utf-8'))
            time.sleep(0.25)
        
        while user_in not in ['y', 'n']:
            user_in = input("Did Red, Green, and Blue LEDs on the keypad turn on? (y/n): ")
            
            if user_in == 'y':
                led_test = 'PASS'
                print('Keypad LED test ' + led_test)
                cmd_off = "AT+TLED=0\r\n"
                ser.write(cmd_off.encode('utf-8'))
                time.sleep(0.25)
            elif user_in == 'n':
                led_test = 'FAIL'
                print('Keypad LED test ' + led_test)
            else:
                print('Wrong input')

        ser.reset_input_buffer()
        return led_test
    except Exception as e:
        print(f'Test command execution error during keypad LED test: {e}')
        led_test = 'FAIL'
        return led_test

def keypad(ser):
        # Test: Keypad check
    try:
        keys = ['0','1','2','3','4','5','6','7','8','9','# or <-']
        cmd = "AT+TKEYPAD=1"
        cmd = cmd +'\r\n'
        ser.write(cmd.encode('utf-8'))
        time.sleep(0.5)
        ser.reset_input_buffer() 
        keyp_test = 'PASS'
        keyp_res = {
        }
        for i in keys:
            print('Press button '+i+' on keypad')
            timeout = time.time() + 20*1   # 30 second timeout
            while True:
                if ser.in_waiting>0:
                    key = ser.read(1024)
                    key = key.split()
                    key = key[0]                
                    i = i.split()
                    i = i[0]
                    #print(i)
                    if key.decode('utf-8')!='+TKEYPAD:\"'+i+'\"':
                        print('Wrong button pressed. Try pressing '+i+' button again!')
                    else:
                        keyp_res["Key "+i]=key.decode('utf-8')
                        print('Key_'+ i+' PASS')
                        ser.reset_input_buffer()
                        break
                elif time.time()>timeout:
                    keyp_res["Key_"+str(i)] = 'TIMEOUT'
                    keyp_test = 'FAIL'
                    print('Key '+ str(i)+' Fail')
                    break               
                        
        cmd = "AT+TKEYPAD=0"
        cmd = cmd +'\r\n'
        ser.write(cmd.encode('utf-8'))
        time.sleep(0.1)
        ser.reset_input_buffer()
        time.sleep(0.1)
        
        # Paygo/ Enter button check
        cmd = "AT+TBUTT=1"
        cmd = cmd +'\r\n'
        ser.write(cmd.encode('utf-8'))
        time.sleep(0.5)
        ser.reset_input_buffer()
        print('Press PAYGO/ Enter button on keypad')
        timeout = time.time() + 20*1   # 20 second timeout
        while True:
            if ser.in_waiting>0:
                key = ser.read(1024)
                key = key.split()
                key = key[0]
                if key.decode('utf-8')!='+TBUTT:3':
                    print('Wrong button pressed. Try pressing Paygo/ Enter button again!')
                else:
                    payg_key='PASS'
                    keyp_res['Key PAYGO'] = key.decode('utf-8')
                    print('Key PAYGO PASS')
                    ser.reset_input_buffer()
                    break
            elif time.time()>timeout:
                keyp_res["Key_"+str(i)] = 'TIMEOUT'
                payg_key = 'FAIL'
                keyp_test = 'FAIL'
                print('Key '+ str(i)+' Fail')
                break
        keyp_res=','.join(keyp_res.values())
        return keyp_res, keyp_test
    except:
        keyp_test = 'FAIL'
        print('Unknown keypad error')
        keyp_test = 'FAIL'
        keyp_res = ''
        return keyp_res, keyp_test


if __name__ == "__main__":
    # Read port name from the config file
    port_name = read_config()

    if port_name:
        ser = initialize_serial(port_name)

        if ser:
            try:
                led_test_result = led(ser)
                print(f'LED Test Result: {led_test_result}')
                
                keypad_result, keypad_test_status = keypad(ser)
                print(f'Keypad Test Result: {keypad_result}, Status: {keypad_test_status}')
            finally:
                close_serial(ser)
    else:
        print('Config file not found or invalid. Please check the config file.')
