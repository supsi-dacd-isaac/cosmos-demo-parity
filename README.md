# cosmos-demo-parity

## Commands:

Check if `$PYTHONPATH` environment variable contains the `cosmos-demo-parity` root (in the following `$ROOT`). 

### Set a measure:

#### Syntax:
<pre>
cd $ROOT/app/ps
../../venv/bin/python handler.py -f $CONF_FILE -c set_measure -s $SIGNAL -v $VALUE
</pre>

N.B. The time is always approximated to 0 seconds. Thus, if a transaction is performed at 2021-05-28T10:46:25Z, then
the timestamp saved will be related to 2021-05-28T10:46:00Z. 

#### Example:
<pre>
cd $ROOT/app/ps
../../venv/bin/python handler.py -f conf/raspberry_demo_parity.json -c set_measure -s T1 -v 13.4
</pre>

### Read a measure:

#### Syntax:
<pre>
cd $ROOT/app/ps
../../venv/bin/python handler.py -f $CONF_FILE -c get_measure -s $SIGNAL -t $DATE_TIME
</pre>

#### Example:
<pre>
cd $ROOT/app/ps
../../venv/bin/python handler.py -f conf/raspberry_demo_parity.json -c get_measure -s T1 -t 2021-05-28T13:22:00Z
</pre>