# lock-manager
Home Assistant Zwave Lock Manager package

For more information, please see the topic for this package at the [Home Assistant Community Forum](https://community.home-assistant.io/t/simplified-zwave-lock-manager/126765).

## Installation

Download the files and put into your Home Assistant place them in the `packages` directory.  If it doesn't already exist, you will need to create it.  For more information see [packages](https://www.home-assistant.io/docs/configuration/packages/).  I suggest putting all of these files in a directory called `lockmanager` so your directory structure should look something like: `.../homeassistant/packages/lockmanager`

This package uses a Schlage BE469 Z-Wave Door lock and an (optional) [Monoprice Z-Wave Plus Recessed Door/Window Sensor (Model #15268)](https://www.monoprice.com/product?p_id=15268) door sensor.

**N.B.**  When you add the devices to your Z-Wvave network via the inlusion mode, use the Home Assistant Entity Registry and rename each entity that belongs to the device and append `_frontdoor` to it.  Example

`zwave.vision_security_zd2105us_5_recessed_door_window_sensor` would be renamed to `zwave.vision_security_zd2105us_5_recessed_door_window_sensor_frontdoor` 
`sensor.schlage_allegion_be469_touchscreen_deadbolt_alarm_level` would be renamed to `sensor.schlage_allegion_be469_touchscreen_deadbolt_alarm_level_frontdoor`

The following files are included: 
* lock_manager_common.yaml
* lovelace
* lock_manager_1.yaml - lock_manager_6.yaml
* copy6.sh

Instead of creating six sets of entities, it found it was much easier to create `lock_manager_1.yaml` and copy that file to `lock_manager_2.yaml`, etc. and modify those files.  The script `copy6.sh` will do that for you.  It simply copies `lock_manager_1.yaml` to `lock_manager_2.yaml` through `lock_manager_6.yaml` and then uses `sed` to replace `_1` to `_2` through `_6`.  Anytime `lock_manager_1.yaml` is modified, run the script to ensure the changes are propagated.  The file `lock_manager_common.yaml` as you might suspect, is code that is common to every entity in the package.  The contents of `lovelace` is the yaml code for displaying the six keypad codes.  In the lovelace editor UI, use the `raw config editor` option to display your entire lovelace yaml.  Go to the end of the file and paste the contents of `lovelace`.

#### Adding more user codes

The easiest way to add another user code "slot" is to modify the `copy6.sh` script.  For example, suppose you wish to add a 7th slot.  Open `copy6.sh` in your favorite editor and change the loop variable to specify the number of "slots" to setup.  So to create 8 slots, change `6` to `8`.  Save and then run the script and then restart Home Assistant.  This script will also create a file named `lovelace` which will contain the lovlace code for a "page" of your 8 slots.  If you want to modify the lovelace code, make the changes in `lovelace.code` and that will be used by `copy6.sh` when setting up the lovelace code.

You will also need to register the following "plug-ins" byt pasting the following into the lovelace "resoures" section at the top of your lovelcace file.

    resources:
        - url: /community_plugin/lovelace-card-mod/card-mod.js
          type: module
        - url: /community_plugin/lovelace-fold-entity-row/fold-entity-row.js
          type: module
        - url: /community_plugin/lovelace-card-tools/card-tools.js
          type: js

The easiest way to add these plugins is using the [Home Assistant Community Store](https://community.home-assistant.io/t/custom-component-hacs/121727).  You will need to go to "Settings" and add the following repositories in order to download the plugins:

* https://github.com/thomasloven/lovelace-auto-entities
* https://github.com/thomasloven/lovelace-card-tools

#### Usage

The application makes heavy usage of binary_sensors.  Each code slot in the system has it's own `Status` binary_sensor.  Whenever the status of that sensor changes, the application will either *add* or *remove* the PIN associated with that slot from the lock.  The `Status` sensor takes the results of the following binary_sensors and combines them using the `and` operator.  Note, these sensors are not visible in the UI.

* Enabled
* Access Count
* Date Range
* Sunday
* Monday
* Tuesday
* Thursday
* Friday
* Saturday

**Enabled**  This sensor is turned on and off by using the `Enabled` toggle in the UI.  Anytime you modify the text of a PIN, this boolean toggle is turned off and must be manually turned on again to "activate" the PIN.  By default, all of a slot's other UI elements are in the "always on" setting, so if you enable this boolean the PIN will be automatically added to the lock and remain that way until you turn the turn the toggle on again.

**Access Count**  This sensor is controlled by the `Limit Access Count` toggle and the `Access Count` slider.  If the toggle is turned on *and* the value of the Access Count slider is greater than zero, this sensor will report true.  Anytime this code slot is used to open a lock, the Access Count slider will be decremented by one.  When the Access Count hits zero, this sensor is disabled and the PIN will be removed from the lock and will remain that way until you increase the Access Count slider or turn off the toggle.

**Date Range**  This sensor, if enabled by it's boolean toggle will be enabled only if the current system date is between the dates specified in the date fields.

**Sunday - Saturday**  These sensors are enabled by default.  If you disable any of them, then the PIN won't work on that day.  When enabled, the PIN will only work if the current system time falls between the specified time periods.  If the periods are equal, then the PIN will work for the entire day.

