import pyvisa

# VISAリソースマネージャーを作成
rm = pyvisa.ResourceManager()

try:
    # 利用可能なVISAリソースをリスト表示
    resources = rm.list_resources()
    print("Available VISA resources:", resources)

    device_address = "TCPIP0::172.22.2.31::hislip200::INSTR"
    print(device_address)

    # デバイス接続
    instrument = rm.open_resource(device_address)
    
    # デバイスが接続されたか確認
    if instrument:
        print(f"Connected to: {instrument.query('*IDN?')}")
    else:
        print("Failed to connect to the device.")

except pyvisa.errors.VisaIOError as e:
    print(f"VISA IO Error: {e}")

finally:
    rm.close()
