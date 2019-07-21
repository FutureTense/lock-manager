# lock-manager
Home Assistant Zwave Lock Manager package

For more information, please see the topic for this package at the [Home Assistant Community Forum](https://community.home-assistant.io/t/simplified-zwave-lock-manager/126765).

## Installation

This package uses a Schlage BE469 Z-Wave Door lock and an (optional) [Monoprice Z-Wave Plus Recessed Door/Window Sensor (Model #15268)](https://www.monoprice.com/product?p_id=15268) door sensor.

When you add the devices to your Z-Wvave network via the inlusion mode, you will need to rename the following in Home Assistant's Entity Registry:

**Schlage (Allegion) BE469 Touchscreen Deadbolt Locked**

Rename `lock.schlage_allegion_be469_touchscreen_deadbolt_locked` to `lock.schlage_allegion_be469_touchscreen_deadbolt_locked_frontdoor`

**Schlage (Allegion) BE469 Touchscreen Deadbolt**

Rename `zwave.schlage_allegion_be469_touchscreen_deadbolt` to `zwave.schlage_allegion_be469_touchscreen_deadbolt_frontdoor`
		
**Vision Security ZD2105US-5 Recessed Door/Window Sensor Access Control** 

Rename `sensor.vision_security_zd2105us_5_recessed_door_window_sensor_access_control` to `sensor.vision_security_zd2105us_5_recessed_frontdoor_sensor_access_control`

**Vision Security ZD2105US-5 Recessed Door/Window Sensor Burglar**

Rename `sensor.vision_security_zd2105us_5_recessed_door_window_sensor_burglar` to `sensor.vision_security_zd2105us_5_recessed_frontdoor_sensor_burglar`

**Vision Security ZD2105US-5 Recessed Door/Window Sensor**

Rename `zwave.vision_security_zd2105us_5_recessed_door_window_sensor` to `zwave.vision_security_zd2105us_5_recessed_frontdoor_sensor`

Download the files and put into your Home Assistant place them in the `packages` directory.  If it doesn't already exist, you will need to create it.  For more information see [packages](https://www.home-assistant.io/docs/configuration/packages/).  I suggest putting all of these files in a directory called `lockmanager` so your directory structure should look something like: `.../homeassistant/packages/lockmanager`

**N.B.**  This package expects your lock to have the entity_id of `lock.front_door_lock` so you can either rename the entity_id of your lock in Home Assistant or do a global replace in the package files. 

The following files are included: 
* lock_manager_common.yaml
* lovelace
* lock_manager_1.yaml - lock_manager_6.yaml
* copy6.sh

Instead of creating six sets of entities, it found it was much easier to create `lock_manager_1.yaml` and copy that file to `lock_manager_2.yaml`, etc. and modify those files.  The script `copy6.sh` will do that for you.  It simply copies `lock_manager_1.yaml` to `lock_manager_2.yaml` through `lock_manager_6.yaml` and then uses `sed` to replace `_1` to `_2` through `_6`.  Anytime `lock_manager_1.yaml` is modified, run the script to ensure the changes are propagated.  The file `lock_manager_common.yaml` as you might suspect, is code that is common to every entity in the package.  The contents of `lovelace` is the yaml code for displaying the six keypad codes.  In the lovelace editor UI, use the `raw config editor` option to display your entire lovelace yaml.  Go to the end of the file and paste the contents of `lovelace`.

#### Adding more user codes

The easiest way to add another user code "slot" is to modify the `copy6.sh` script.  For example, suppose you wish to add a 7th slot.  Open `copy6.sh` in your favorite editor and add the following:

    cp lock_manager_1.yaml lock_manager_7.yaml
    sed -i 's/_1/_7/g' lock_manager_7.yaml
 
Save and then run the script and then restart Home Assistant.  Now you will have entities for the 7th slot.  To add the UI elements, open the first slot with the UI editor and copy the contents and paste into an editor.  Replace `_1` with `_7`.  Click the `+` icon in the UI and add a "manual card".  Paste the contents of your code, save and you're done.

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
