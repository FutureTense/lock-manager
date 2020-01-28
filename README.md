# lock-manager
Home Assistant Zwave Lock Manager package

For more information, please see the topic for this package at the [Home Assistant Community Forum](https://community.home-assistant.io/t/simplified-zwave-lock-manager/126765).

## Installation

Download the files and put into your Home Assistant place them in the `packages\lockmanager` directory.  If `packages` doesn't already exist, you will need to create it.  For more information see [packages](https://www.home-assistant.io/docs/configuration/packages/).  When finished your directory structure should look something like: `.../homeassistant/packages/lockmanager`

This package uses a Schlage BE469 Z-Wave Door lock and an (optional) [Monoprice Z-Wave Plus Recessed Door/Window Sensor (Model #15268)](https://www.monoprice.com/product?p_id=15268) door sensor, and accepts a `cover` for a garage. If you aren't using the Monoprice or similar open/closed door sensor, you can just hide the assoicated entities in the generated lovelace file.  Likewise you can remove the garage cover. In fact, if wish to modify the lovelace used for all locks, you can edit the `lovelace.head` and `lovelace.code` files which are used to generate a lovelace view for your lock.

**N.B.**  After you add your devices (Zwave lock, door sensor) to your Z-Wvave network via the inlusion mode, use the Home Assistant Entity Registry and rename each entity that belongs to the device and append `_LOCKNAME` to it.  For example, if you are calling your lock `FrontDoor`, you will want to append _FrontDoor to each entity of the device.

`sensor.schlage_allegion_be469_touchscreen_deadbolt_alarm_level` 
would become 
`sensor.schlage_allegion_be469_touchscreen_deadbolt_alarm_level_frontdoor`

While you are appending each entity, examine the entities of your new devices carefully.  You need to identify the "lowest common demominator" of the device.  This would be the text that is part of *every* entity that exists in the entity registry.  You need to do this for the lock, and door sensor if you have one.  Save these "base" names in a notepad file for later.  So for the Schlage BE469, that would be **schlage_allegion_be469zp_connect_smart_deadbolt**, and for the Monoprice door sensor, it is **vision_security_zd2105us_5_recessed_door_window_sensor**.  The Schlage base names can and do change when they release versions.  So it is not only possible, but likley the base name shown here is different than yours, so pay attention.

Make sure you rename *every* associated entity in the entity registry.  The easiest way to do this is take the base name you found, and put it in the search bar of the entity registry.  This will show all of the entities you need to rename.  Just go down the list and append `_FrontDoor` (assuming that's the name you chose) at the end of each entity.

Open `FrontDoor.ini` in a text editor.  

* Change the value of `numcodes` to the number of PIN slots you want for this lock.  Don't go crazy and set this value too high as it could slow your browser down.  You can always add more codes later so you might want to keep the default value of (6).
* Set `lockname`.  I suggest using the name of the door the lock is in, such as "FrontDoor" (no spaces or special characters)
* Set `lockfactoryname`.  This is the "base" name you saved above
* Set `sensorname` and `sensorfactoryname` just as you did for the lock.  If you don't have a sensor, just put some dummy values in.  You can remove the sensors from the GUI later.
* Set `garageentityid`.  If you have a garage door opener in your network and you want it to appear on your lock page, put it's entity_id here.  Like the sensor, don't leave this value blank.  This too can be removed from the GUI.

Save the file.  If you have multiple locks, make a copy of the ini file and set the values as you just did for your first lock.  Make sure you append this door's name (eg _BackDoor) to this lock's entities using the entity register.

Make the setup.sh script executable by typing:

> chmod +x script.sh

Now execute the script by typing:

> ./script.sh

If all goes well, you will see a success message for each `ini` file you have in that directory.  You will also see a new directory for each lock.  So if you had two ini files, one with FrontDoor and the other with BackDoor, you should see two directories with those names.  Inside of each of those directories will be a file called `<lockname>_lovelace`.  Open that file in a text editor and select the entire contents and copy to the clipboard.

> (Open file) Ctrl-A (select all) Ctrl-C (copy)

Open Home Assistant and open the LoveLace editor by clicking the elipses on the top right of the screen, and then select "Configure UI".  Click the elipses again and click "Raw config editor".  Scroll down to the bottom of the screen and then paste your clipboard.  This will paste a new View for your lock.  Click the Save button then click the X to exit.


You will also need to register the following plug-ins by pasting the following into the lovelace "resoures" section at the top of your lovelcace file.

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


#### Additional Setup (Optional, but strongly reccomened)

Before your lock will respond to automations, you will need to add a couple of things to your existing configuration.  The first is you need to add the following `input_booleans`:

```
allow_automation_execution:
  name: 'Allow Automation'
  initial: off

input_boolean.system_ready:
  name: 'System Ready'
  initial: off
  
```

and you will also need to add this `binary_sensor`


```
    allow_automation:
      friendly_name: "Allow Automation"
      value_template: "{{ is_state('input_boolean.allow_automation_execution', 'on') }}"

    system_ready:
      friendly_name: "System ready"
      value_template: "{{ is_state('input_boolean.system_ready', 'on') }}"
      device_class: moving
```

`binary_sensor.allow_automation` is used *extensivly* throught the project.  If you examine the code, you see it will refert to the `input_boolean.allow_automation_execution`.  The reasons for a seperate input_boolean and binary_sensor are beyond the scope of this document.  But the reason they exist is worth a discussion.

When Home Assistant starts up, several of this project's automations will be called, which if you have notificatins on will send unnecessary notifications.  The allow_automations boolean will prevent those automations from firing.  However, in order for this to work you stil need to add a few more things.

Add the following to you Home Asssistant Automations (not in this project!)

```
- alias: homeassistant start-up
  initial_state: true
  trigger:
    platform: homeassistant
    event: start
  action:
    - service: script.turn_on
      entity_id: script.customstartup
      
- alias: Zwave_loaded_Start_System
  initial_state: true
  trigger:
    - platform: event
      event_type: zwave.network_ready
    - platform: event
      event_type: zwave.network_complete
    - platform: event
      event_type: zwave.network_complete_some_dead
  action:
    - service: script.turn_on
      entity_id: script.system_cleanup
```

and likewise, add the following to your scripts:


```
system_cleanup:
  sequence:
    #- service: homekit.start If you use homekit, uncomment this statement
    - service: input_boolean.turn_on
      entity_id: input_boolean.system_ready
    - service: input_boolean.turn_on
      data:
        entity_id: 'input_boolean.allow_automation_execution'

customstartup:
  sequence:
    - service: input_boolean.turn_off
      data:
        entity_id: 'input_boolean.allow_automation_execution'
      # You can add other "startup" code here if you wish
```

This ensures that your input_boolean.allow_automation_exectuion is turned off at startup.  After your Zwave devices have been loaded, script.system_cleanup is called, which will enable this boolean and allow your automations to execute.  As it takes some time for your Zwave devices to actually load, use binary_sensor.system_ready sensor on the GUI so the end user knows when everything is ready to go.

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
