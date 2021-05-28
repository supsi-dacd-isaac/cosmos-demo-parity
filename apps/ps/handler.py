# --------------------------------------------------------------------------- #
# Modules
# --------------------------------------------------------------------------- #
import argparse
import json
import logging
import time
import pytz
from datetime import datetime

from classes.cosmos_interface import CosmosInterface
import ps_utils as pu

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
DT_FRMT = '%Y-%m-%dT%H:%M:%SZ'


# --------------------------------------------------------------------------- #
# Functions
# --------------------------------------------------------------------------- #
def get_dt(str_dt):
    tz_local = pytz.timezone(cfg['utils']['timeZone'])

    if str_dt == 'now':
        dt = datetime.now()
    elif str_dt == 'now_s00':
        dt = datetime.now()
        dt = dt.replace(second=0, microsecond=0)
    else:
        dt = datetime.strptime(str_dt, DT_FRMT)
    dt = tz_local.localize(dt)
    dt_utc = dt.astimezone(pytz.utc)

    return dt_utc


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # --------------------------------------------------------------------------- #
    # Arguments
    # --------------------------------------------------------------------------- #
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', help='configuration file')
    arg_parser.add_argument('-c', help='command')
    arg_parser.add_argument('-s', help='signal')
    arg_parser.add_argument('-v', help='value')
    arg_parser.add_argument('-t', help='time (optional)')
    arg_parser.add_argument('-l', help='log file (optional)')

    args = arg_parser.parse_args()
    cfg = json.loads(open(args.f).read())

    # Get configuration about sidechains info
    tmp_config = json.loads(open(cfg['sidechainFile']).read())
    cfg.update(tmp_config)

    # set logging object
    if not args.l:
        log_file = None
    else:
        log_file = args.l

    # define logger
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=log_file)

    # starting program
    logger.info('Starting program')

    app_cli = '%scli' % cfg['tendermint']['app']

    ci = CosmosInterface(app='ps', cfg=cfg, logger=logger)

    if args.c == 'set_measure':
        signal = args.s

        end_dt_utc = get_dt('now_s00')

        value = float(args.v)

        timestamp = '%s' % int(end_dt_utc.timestamp())

        str_value = '%.2f' % value

        # Do the transaction
        transaction_params = {
                        "signal": signal,
                        "timestamp": timestamp,
                        "value": str_value
                   }
        ci.do_transaction(cmd='setMeasure', params=transaction_params)

        # Wait enough time
        time.sleep(6)

        # Do a query
        query_params = {
                        "signal": signal,
                        "timestamp": timestamp
                       }
        data = ci.do_query(cmd='getMeasure', params=query_params)
        logger.info(data)

    elif args.c == 'get_measure':
        # Do a query
        signal = args.s
        dt = datetime.strptime(args.t, '%Y-%m-%dT%H:%M:%SZ')
        query_params = {
                        "signal": signal,
                        "timestamp": int(dt.timestamp())
                       }
        data = ci.do_query(cmd='getMeasure', params=query_params)
        if len(data['result']['meterId']) > 0 and len(data['result']['account']) > 0:
            logger.info('MeterId: %s' % data['result']['meterId'])
            logger.info('Account: %s' % data['result']['account'])
            logger.info('Signal: %s; DT: %s; TS: %s; Value: %s' % (signal, args.t,
                                                                   data['result']['timestamp'],
                                                                   data['result']['value']))
        else:
            logger.info('Signal: %s; DT: %s; TS: N/A; Value: N/A' % (signal, args.t))

    elif args.c == 'set_market_parameters':
        ci.do_transaction(cmd='parameters', params=cfg['defaultMarketParameters'])

        # Wait enough time
        time.sleep(6)

    elif args.c == 'add_allowed_meters':

        for node in cfg["nodes"].keys():
            transaction_params = pu.add_meter(node, cfg, app_cli)
            ci.do_transaction(cmd='meterAccount', params=transaction_params)
            time.sleep(6)

    elif args.c == 'set_admin':
        host = cfg['nodes'][cfg["admin"]][2]
        user = cfg['nodes'][cfg["admin"]][3]
        remote_goroot = cfg['nodes'][cfg["admin"]][4]
        account = cfg['nodes'][cfg["admin"]][5]

        real_cmd = '%s/bin/%s keys show %s' % (remote_goroot, app_cli, pu.get_real_account(host, user, account))
        key_str = pu.exec_real_cmd(host, user, real_cmd, False)

        # Build the dataset
        res = ''
        for elem in key_str:
            res = '%s%s' % (res, elem)
        data_key = json.loads(res)
        ci.do_transaction(cmd='setAdmin', params={'address': data_key['name']})

    elif args.c == 'list_allowed_meters':
        data = ci.do_query(cmd='meterAccount', params={})
        logger.info(data)

    elif args.c == 'show_admin':
        data = ci.do_query(cmd='getAdmin', params={})
        logger.info(data)

    # ending program
    logger.info('Ending program')
