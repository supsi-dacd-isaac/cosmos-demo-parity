import json
import subprocess
import hashlib


# Functions
DT_FRMT = '%Y-%m-%dT%H:%M:%SZ'


def send_cmd_over_ssh(host, user, command, print_flag):
    result = subprocess.check_output('ssh %s@%s %s' % (user, host, command), shell=True)
    decoded_ret = result.decode('UTF-8')
    if print_flag:
        print(decoded_ret)
    return decoded_ret.split('\n')


def exec_real_cmd(host, user, real_cmd, print_flag):
    try:
        if print_flag:
            print('Remote command: %s' % real_cmd)
            print('Result:')
        res = send_cmd_over_ssh(host=host, user=user, command=real_cmd, print_flag=print_flag)
        if print_flag:
            print('****')
        return res
    except Exception as e:
        print('EXCEPTION: %s' % str(e))
        return None


# Get the first MAC address
def get_eth_mac(host, user):
    # I apologize for the following code, if you try something better please send a PR

    # Run the remote command
    if user == 'pi':
        ret = exec_real_cmd(host, user, 'sudo ifconfig', False)
    else:
        ret = exec_real_cmd(host, user, 'ifconfig', False)

    # The classical way (ETH0)
    idx_eth0 = -1
    for idx in range(0, len(ret)):
        if 'eth0' in ret[idx]:
            idx_eth0 = idx

    if idx_eth0 != -1:
        for idx in range(idx_eth0, len(ret)):
            if 'ether' in ret[idx]:
                break
    else:
        # it works on Ubuntu>=18.04
        idx_dev_int = -1
        for idx in range(0, len(ret)):
            if 'device' in ret[idx] and 'interrupt' in ret[idx]:
                idx_dev_int = idx

        for idx in range(idx_dev_int, 0, -1):
            if 'ether' in ret[idx]:
                break

    res = ret[idx].replace('  ', ' ').replace(' ', ';').replace(';;', '').split(';')
    return res[1]


def get_real_account(host, user, account):
    if account == 'hashed_mac':
        # Get the remote first MAC address
        eth_mac = get_eth_mac(host, user)

        # Encode the MAC address
        h = hashlib.new('sha512')
        h.update(str.encode(eth_mac))
        real_account = h.hexdigest()
    else:
        real_account = account
    return real_account

def add_meter(node, cfg, app_cli):
    host = cfg['nodes'][node][2]
    user = cfg['nodes'][node][3]
    remote_goroot = cfg['nodes'][node][4]
    account = cfg['nodes'][node][5]

    real_cmd = '%s/bin/%s keys show %s' % (remote_goroot, app_cli, get_real_account(host, user, account))
    key_str = exec_real_cmd(host, user, real_cmd, False)

    # Build the dataset
    res = ''
    for elem in key_str:
        res = '%s%s' % (res, elem)
    data_key = json.loads(res)

    # Do the transaction
    transaction_params = {
        "meter": data_key["name"],
        "account": data_key["address"]
    }
    return transaction_params
