# -*- mode: python; python-indent: 4 -*-
import ncs
import _ncs
from ncs.dp import Daemon
from ncs.application import Service
from ncs.experimental import DataCallbacks

# Data callback handler class
# an instance of this class is registered to handle reads on the "stats" callpoint
class InterfaceStatsCallbackHandler(object):
    def __init__(self, log):
        self.log = log

    # See the DataCallbacks.register method doc:
    # https://developer.cisco.com/docs/nso/api/#!ncs-experimental/ncs.experimental.DataCallbacks.register
    def get_object(self, tctx, keypath, _args):

        self.log.info(f"InterfaceStatscallbackhandler.get_object called. keypath={keypath}, _args={_args}")

        # This is where the fancy stuff goes.
        # Talking to a database, IPAM system, etc.

        # these are from the other examples. I leave them here for reference and
        # for people searching the web for them :)
        #if_name = str(keypath[2][0])
        # (sent, recv) = get_counters(if_name)

        return {
            "stats": {
                "sent": 12345,
                "received": 67890
            }
        }

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # instantiate the handler
        interface_stats_handler = InterfaceStatsCallbackHandler(self.log)

        # instantiate the DataCallbacks helper class
        dcb = DataCallbacks(self.log)

        # register the handler with the DataCallbacks instance
        dcb.register('/pydp:interface/pydp:GigabitEthernet', interface_stats_handler)

        # create a daemon to manage the connection between our data provder & NCS
        pydp_daemon = Daemon('pydp-daemon', log=self.log)

        # register the dcb helper instance as a data callback
        # https://developer.cisco.com/docs/nso/api/#!_ncs-dp/_ncs.dp.register_data_cb
        _ncs.dp.register_data_cb(pydp_daemon.ctx(), 'stats', dcb)

        # start the daemon
        pydp_daemon.start()

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).
        ##### Except this is not accurate for data provider callbacks :) #####
        ##### Which is why we do it manually in this example. #####

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
