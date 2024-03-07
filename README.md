pydp: a demo python data provider for NSO
=========================================

This NSO package is a functional implementation of the demo code found in the following posts:

* https://community.cisco.com/t5/nso-developer-hub-discussions/callback-python-code/td-p/3510805
* https://community.cisco.com/t5/nso-developer-hub-discussions/python-datacallback-daemon/td-p/3951222
* https://community.cisco.com/t5/nso-developer-hub-discussions/python-data-provider-example/td-p/3572722

I created this package while digging through the example code from the posts above and the [NSO Python API reference](https://developer.cisco.com/docs/nso/api/#!ncs). Here, the [Datacallbacks class doc](https://developer.cisco.com/docs/nso/api/#!ncs-experimental/ncs.experimental.DataCallbacks) and its [register method](https://developer.cisco.com/docs/nso/api/#!ncs-experimental/ncs.experimental.DataCallbacks.register) docs were particularly enlightening. 

As someone in one of the posts above mentions that "_'experimental.DataCallbacks' is, eh.. experimental(!) and far from complete and shouldn't be used in production._," and "_It's still fairly easy to create a DP in Python without the help you get from experimental.DataCallbacks_," I examined the [Java DpDataCallback interface](https://pubhub.devnetcloud.com/media/nso-api-6.2/docs/java/com/tailf/dp/DpDataCallback.html) used in the NSO 6.2.1 example `getting-started/developing-with-nso/6-extern-db` and the [\_ncs.dp.register\_data\_cb method API doc](https://developer.cisco.com/docs/nso/api/#!_ncs-dp/_ncs.dp.register_data_cb). This last one seems to indicate that a user-implemented callback class implementing all the methods listed there would be good enough for production[^1] (but don't quote me on that!).

[^1]: Note that [ncs.DataCallbacks](https://developer.cisco.com/docs/nso/api/#!ncs-experimental/ncs.experimental.DataCallbacks) does not implement all of these!

Building
--------
1. Deploy this repo to `$NCS_DIR/packages/pydp`
2. Source your `ncsrc`
3. `make -C src packages/pydp/src`       ## builds the fxs from the yang
4. Start NSO if necessary (`ncs`)
5. `echo 'request packages reload' | ncs_cli -u admin`

Watching it Work
----------------
1. In one window, start `tail -F $NCSDIR/logs/ncs-python-vm-pydp.log`  ## assuming you haven't mucked w/ the logfile prefix settings
   - Verify that you get the `ComponentThread:main: - Main RUNNING` log message
2. In another window, start ncs_cli (`ncs_cli -u admin`)
3. In ncs_cli, create an instance of the `instance GigabitEthernet` from the yang model in `config` mode:

	admin@ncs> configure 
	Entering configuration mode private
	[ok][2024-03-07 15:38:16]
	
	[edit]
	admin@ncs% set interface GigabitEthernet foo
	[ok][2024-03-07 15:42:34]
	
	[edit]
	admin@ncs% commit
	Commit complete.
	[ok][2024-03-07 15:42:37]
	
	[edit]
	admin@ncs% exit
	[ok][2024-03-07 15:43:19]
	admin@ncs>show interface GigabitEthernet foo stats 
	stats sent 12345
	stats received 67890
	[ok][2024-03-07 15:43:35]
	admin@ncs>

4. Notice the log message in `$NCSDIR/logs/ncs-python-vm-pydp.log` shows the log message from `InterfaceStatscallbackhandler.get_object` (in main.py in this repo)

Reflections
-----------
This example is a little odd in that it puts its content under a top-level containter, `interface`, and a `GigabitEthernet` list in the NSO config tree. Additionally, to see it work, you have to create an instance of the `interface/GigabitEthernet` list to access the `stats` child container where the callpoint is (as this is what kicks off the data provider callback handler). 

I'll now move on to building a more useful example for my purposes, but I hope the presence of this repo can help someone else who's trying to piece this all together and save them some time :)
