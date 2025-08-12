# Etekcity Smart Blood Pressure Monitor Integration for Home Assistant

![GitHub Release](https://img.shields.io/github/v/release/EdLeckert/ha_etekcity_blood_pressure_monitor)

The `etekcitybp_ble` implementation allows you to integrate your Etekcity Smart Blood Pressure Monitor data into Home Assistant.

## Features

- Provides Systolic, Diastolic, and Pulse data.
- Provides measurement data in both mmHg and kPa units.
- Provides Irregular Heartbeat, Motion, and other measurement errors.
- Supports two users.
- Provides the current Display Units setting in the device.
- Records measurement data automatically without the need for a mobile device or app.

## Disclaimer
This is an unofficial integration of Etekcity Smart Blood Pressure Monitor Integration for Home Assistant. 
The developer and the contributors are not in any way affiliated with Etekcity Corporation or Guangdong Transtek Medical Electronics Co., Ltd.

## Requirements
- Etekcity Smart Blood Pressure Monitor (only the TMB-1583-BS has been tested, but other models may work)
- A Bluetooth Low Energy (BLE) capable device configured with Home Assistant (tested with ESPHome Bluetooth Proxy)

## Installation
1. Install manually by copying the `custom_components/etekcitybp_ble` folder into `<config_dir>/custom_components`.
2. Restart Home Assistant.
3. Power on the Etekcity Smart Blood Pressure Monitor by pressing the `MEM` button. The device should be discovered automatically by Home Assistant.
4. In the Home Assistant UI, navigate to `Settings` then `Devices & services`. In the `Integrations` tab, you should see the Etekcity Smart Blood Pressure integration listed under `Discovered`. Click `ADD` and fill in the forms.
5. Optionally, you may click on the `ADD INTEGRATION` button at the bottom right and select `Etekcity Blood Pressure Monitor`. Fill in the forms.

## Usage

### Sensors

| Friendly Name                | Example State | Description
| -------------                | ------------- | -----------
| `Systolic Pressure User 1`   | 102 mmHg      | Latest Systolic Pressure measurement for the first user in mmHg.
| `Systolic (kPa) User 1`      | 13.6 kPa      | Latest Systolic Pressure measurement for the first user in kPa.
| `Diastolic Pressure User 1`  | 70 mmHg       | Latest Diastolic Pressure measurement for the first user in mmHg.
| `Diastolic (kPa) User 1`     | 9.3 kPa       | Latest Diastolic Pressure measurement for the first user in kPa.
| `Pulse User 1`               | 72 bpm        | Latest Pulse measurement for the first user.
| `Systolic Pressure User 2`   | 102 mmHg      | Latest Systolic Pressure measurement for the second user in mmHg.
| `Systolic (kPa) User 2`      | 13.6 kPa      | Latest Systolic Pressure measurement for the second user in kPa.
| `Diastolic Pressure User 2`  | 70 mmHg       | Latest Diastolic Pressure measurement for the second user in mmHg.
| `Diastolic (kPa) User 2`     | 9.3 kPa       | Latest Diastolic Pressure measurement for the second user in kPa.
| `Pulse User 2`               | 75 bpm        | Latest Pulse measurement for the second user.
| `Irregular Heartbeat User 1` | OK, Problem   | Indicates if an irregular heartbeat was detected during the last measurement for the first user.
| `Irregular Heartbeat User 2` | OK, Problem   | Indicates if an irregular heartbeat was detected during the last measurement for the second user.
| `Motion User 1`              | OK, Problem   | Indicates if arm motion was detected during the last measurement for the first user.
| `Motion User 2`              | OK, Problem   | Indicates if arm motion was detected during the last measurement for the second user.
| `Display Units`              | mmHg          | Current display units setting of the device (mmHg or kPa).
| `Error Code`                 | OK, E01,...   | Indicates the last error code received from the device. Consult the User Manual for error code meanings.

### Measuring Blood Pressure

Follow the directons in the User Manual to measure blood pressure. The device will automatically send the latest measurement data to Home Assistant 
within five seconds after the measurement is complete. You can then turn off the device. The new data will appear in Home Assistant in about 30 seconds.

The new data will appear under the user (User 1 or User 2) set in the device at the time of measurement.

The date and time of the device is not used to record the time of measurment.

The Bluetooth icon on the device display will blink during the measurement as a connection is repeatedly made and dropped by the integration.
If you don't see the Bluetooth icon blinking, the device is not connected to Home Assistant.

The device can only connect to one `Central` at a time. If you are using the device with a mobile app such as `VeSync` or `nRF Connect`, 
you will need to disconnect the app before taking your blood pressure so Home Assistant can connect to the device.

The `Display Units` sensor will show the current display units setting of the device. This could be used in a `Conditional Card` to display the 
Systolic and Diastolic sensors with units that match the display on the device.


## Contribute
Feel free to contribute by opening a PR or issue on this project.