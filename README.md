# lock-manager

Home Assistant Lock Manager integration for Z-Wave enabled locks. This integration allows you to control one (or more) Z-Wave enabled locks that have been added to your Z-Wave network.  Besides being able to control your lock with lock/unlock commands, you can also control who may lock/unlock the device using the lock's front facing keypad.  With the integration you may create multiple users or slots and each slot (the number depends upon the lock model) has its own PIN code.

Setting up a lock for the entire family can be accomplished in a matter of seconds.  Did you just leave town and forgot to turn the stove off?  through the Home Assistant interface you can create a new PIN instantly and give it to a neighbor and delete it later.  Do you have house cleaners that come at specifc times?  With the advanced PIN settings you can create a slot that only unlocks on specific date and time ranges. You may also create slots that allow a number of entries, after which the lock won't respond to the PIN.

For more information, please see the topic for this package at the [Home Assistant Community Forum](https://community.home-assistant.io/t/simplified-zwave-lock-manager/126765).

## Before installing

This package works with several Z-Wave Door locks, but only has been tested by the developers for Kwikset and Schlage.  It also supports an optional door sensor, and accepts a `cover` for a garage. If you aren't using the open/closed door sensor or garage cover, you can just hide or ignore the assoicated entities in the generated lovelace files. Likewise you can remove the garage cover. In fact, if wish to modify the lovelace used for all locks, you can edit the `lovelace.head` and `lovelace.code` files in the /config/packages/DOOR directory which are used to build the lovelace code for your lock.

### Each lock requires its own integration
Each physical lock requires its own integration.  When you create an integration, you give the lock a name, (such as *frontdoor*) and a directory will be created in /config/packages/ that holds the code for that lock.  So if you have a second physical lock, you will create a second integration (such as *backdoor*).  When you are finished, you will have the following directories:

    /config/packages/frontdoor
    /config/packages/backdoor


<details>
  <summary>If you're using multiple locks, please click here!</summary>
  
After you add your devices (Zwave lock, door sensor) to your Z-Wvave network via the inlusion mode, you should consider using the Home Assistant Entity Registry and rename each entity that belongs to the lock device and append `_LOCKNAME` to it. For example, if you are calling your lock `FrontDoor`, you will want to append \_FrontDoor to each entity of the lock device.  This isn't necessary, but it will make it easier to understand which entities belong to which locks.  This is especially true if you are using multiple locks.

`sensor.schlage_allegion_be469_touchscreen_deadbolt_alarm_level`
would become
`sensor.schlage_allegion_be469_touchscreen_deadbolt_alarm_level_frontdoor`

AND

`lock.schlage_allegion_be469_touchscreen_deadbolt_locked`
would become
`lock.schlage_allegion_be469_touchscreen_deadbolt_frontdoor`
</details>

## Installation

This integration can be installed manually, but the *supported* method requires you to use The [Home Assistant Community Store](https://community.home-assistant.io/t/custom-component-hacs/121727).  If you dont't already have HACS, it is [simple to install](https://hacs.xyz/docs/installation/prerequisites).

Follow [these instructions](https://hacs.xyz/docs/faq/custom_repositories) to add a custom repository to your HACS integration.  The repository you want to use is: https://github.com/FutureTense/lock-manager and you will want to install it as an `Integration`.

Open HACS and select the Integrations tab.  Click the + icon at the bottom right and search for `lock-manager`.  If you are using the OpenZwave implemtation, make sure you choose the latest version that ends in **ozw**.  Otherwise, for the native HA Zwave implementation select a version *without* ozw.  You will then get a message that the integration requires Home Assistant to be restarted.  Please do so.

You need to create an integration for each lock you want to control.  Select Configuration | Integrations.  Click the + icon at the bottom right and search for **Lock Manager** and select it.  The integration UI will prompt you for several values.  Below we are using the default entity names that are created for a Schlage BE469 lock.

1.  Z-wave lock
    
    Use the dropdown and select your Z-Wave lock.  The default for Schlage looks like `lock.be469zp_connect_smart_deadbolt_locked`
2.  Code slots

    The number of code slots or PINS you want to manage.  The maxinum number is depedant upon your lock.  Don't create more slots than you will actually need, because too many can slow your lovelace UI down.
3.  Start from code slot #

    explanation here
4.  Lock Name
    Give your lock a name that will be used in notifications, e.g. *FrontDoor*
5.  Door Sensor

    If your lock has a sensor that determines if the door is opened/closed, select it here.  The Schlage doesn't have one but you can use a third party sensor or specify any sensor here.
6.  User Code Sensor

    This sensor returns the slot number for a user that just entered their lock PIN.  Schlage value: `sensor.be469zp_connect_smart_deadbolt_user_code`
7.  Access Control Sensor

    This sensor returns the command number just executed by the lock.  Schlage value: `sensor.be469zp_connect_smart_deadbolt_access_control`    
8.  Path to packages directory

    The default `/config/packages/lock-manager` should suffice.

If all goes well, you will also see a new directory (by default `<your config directory/packages/lock-manager/>`) for each lock with `yaml` and a lovelace files. So if you add two integrations, one with FrontDoor and the other with BackDoor, you should see two directories with those names. Inside of each of those directories will be a file called `<lockname>_lovelace`. Open that file in a text editor and select the entire contents and copy to the clipboard.

> (Open file) Ctrl-A (select all) Ctrl-C (copy)

Open Home Assistant and open the LoveLace editor by clicking the elipses on the top right of the screen, and then select "Configure UI". Click the elipses again and click "Raw config editor". Scroll down to the bottom of the screen and then paste your clipboard. This will paste a new View for your lock. Click the Save button then click the X to exit.
#### Additional Setup

Before your lock will respond to automations, you will need to add a couple of things to your existing configuration. The first is you need to add the following `input_booleans`:

```
allow_automation_execution:
  name: 'Allow Automation'
  initial: off

system_ready:
  name: 'System Ready'
  initial: off

```

and you will also need to create these `binary_sensor`

```
    allow_automation:
      friendly_name: "Allow Automation"
      value_template: "{{ is_state('input_boolean.allow_automation_execution', 'on') }}"

    system_ready:
      friendly_name: "System ready"
      value_template: "{{ is_state('input_boolean.system_ready', 'on') }}"
      device_class: moving
```

`binary_sensor.allow_automation` is used _extensivly_ throught the project. If you examine the code, you see it will refered to the `input_boolean.allow_automation_execution`. The reasons for a seperate input_boolean and binary_sensor are beyond the scope of this document.

When Home Assistant starts up, several of this project's automations will be called, which if you have notificatins on will send unnecessary notifications. The allow_automations boolean will prevent those automations from firing. However, in order for this to work you stil need to add a few more things.

Add the following to you Home Asssistant Automations (not in this project!)

```
- alias: homeassistant start-up
  initial_state: true
  trigger:
    platform: homeassistant
    event: start
  action:
    - service: input_boolean.turn_off
      entity_id: input_boolean.system_ready
    - service: input_boolean.turn_off
      entity_id: 'input_boolean.allow_automation_execution'

- alias: open_zwave_network_down
  initial_state: true
  trigger:
    - platform: state
      entity_id: binary_sensor.ozw_network_status
      to: "off"
  action:
    - service: homeassistant.turn_off
      entity_id: input_boolean.allow_automation_execution

- alias: open_zwave_network_up
  initial_state: true
  trigger:
    - platform: homeassistant
      event: start
    - platform: state
      entity_id: binary_sensor.ozw_network_status
      to: "on"
  condition:
    - condition: state
      entity_id: binary_sensor.ozw_network_status
      state: "on"
  action:
    - service: script.system_startup_cleanup
```

and likewise, add the following to your scripts:

```
# feel free to add post startup calls here
system_startup_cleanup:
  sequence:
    - condition: state
      entity_id: 'input_boolean.system_ready'
      state: 'off' 
    - service: homekit.start
    - service: input_boolean.turn_on
      entity_id: 'input_boolean.allow_automation_execution'
    - service: input_boolean.turn_on
      entity_id: input_boolean.system_ready
        
```

This ensures that your input_boolean.allow_automation_exectuion is turned off at startup. After your Zwave devices have been loaded, script.system_cleanup is called, which will enable this boolean and allow your automations to execute. As it takes some time for your Zwave devices to actually load, use binary_sensor.system_ready sensor on the GUI so the end user knows when everything is ready to go.

#### Usage

The application makes heavy usage of binary*sensors. Each code slot in the system has it's own `Status` binary_sensor. Whenever the status of that sensor changes, the application will either \_add* or _remove_ the PIN associated with that slot from the lock. The `Status` sensor takes the results of the following binary_sensors and combines them using the `and` operator. Note, these sensors are not visible in the UI.

- Enabled
- Access Count
- Date Range
- Sunday
- Monday
- Tuesday
- Thursday
- Friday
- Saturday

**Enabled** This sensor is turned on and off by using the `Enabled` toggle in the UI. Anytime you modify the text of a PIN, this boolean toggle is turned off and must be manually turned on again to "activate" the PIN. By default, all of a slot's other UI elements are in the "always on" setting, so if you enable this boolean the PIN will be automatically added to the lock and remain that way until you turn the turn the toggle on again.

**Access Count** This sensor is controlled by the `Limit Access Count` toggle and the `Access Count` slider. If the toggle is turned on _and_ the value of the Access Count slider is greater than zero, this sensor will report true. Anytime this code slot is used to open a lock, the Access Count slider will be decremented by one. When the Access Count hits zero, this sensor is disabled and the PIN will be removed from the lock and will remain that way until you increase the Access Count slider or turn off the toggle.

**Date Range** This sensor, if enabled by it's boolean toggle will be enabled only if the current system date is between the dates specified in the date fields.

**Sunday - Saturday** These sensors are enabled by default. If you disable any of them, then the PIN won't work on that day. When enabled, the PIN will only work if the current system time falls between the specified time periods. If the periods are equal, then the PIN will work for the entire day.
