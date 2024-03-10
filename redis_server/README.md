# Build My Own Memcached Server

In this piece of code, I've built a simple memcached server using Python. Memcache is a in-memory cache system. In this system data is stored in key-value structure.

This piece of code is based on this coding challenge: [Building Your Own Memcached Server](https://codingchallenges.fyi/challenges/challenge-memcached).

### Installation
##### step 1
Clone the project:
```commandline
git clone https://github.com/sarah-amiri/BuildingMyOwnTools.git
```
##### step 2
To run *memcached server* app go to its directory:
```commandline
cd memcached
```
##### step 3
Make a virtual environment and activate it:
```commandline
python3 -m venv venv
source venv/bin/activate
```
##### step 4
Install the app package through *setup.py* and run it using *memcached* command:
```commandline
pip install .
memcached
```

### Arguments
Memcached is run on port `11211` but you can change the port number using `-p` argument.

### Commands
This app already support these commands. You can test these commands using **telnet** command tool.<br><br>
fields in syntax are:
- `key-value` key and value of data to store.
- `flags` a 32-bit unsigned integer stored with data
- `exptime` expiration time of data. If this field equals to *0*, there is no time limit. if it is negative, data expires immediately. Otherwise, expiration time will be calculated in seconds.
- `bytes` value length in byte.
- `cas_id` cas_id assigned to key every time storing or updating a key.
- `[noreply]` It is an optional field. If it is set, no data will be returned in response.

Different outputs are:
- `STORED` key/value are stored or updated successfully.
- `NOT_STORED` key/value not stored or not updated but there was not any errors either.
- `NOT_FOUND` key does not found
- `DELETED` key is deleted successfully
- `ERROR` an error occurred while settings or updating key/value.
- `SIZE_LIMIT` memcached server has a size limit in bytes. it is now set to *100000 bytes*. This output means this limit has reached so key/value cannot set or updated successfully.

##### set
This command set a value to a new or existing key. If key exists, new value is substitute. This command syntax is as follows:
```
set <key> <flags> <exptime> <bytes> [noreply]
<value>
```
This command outputs can be: `STORED`, `ERROR`, `SIZE_LIMIT`.
##### add
This command adds a new key to system. If key already exists, it is not stored. This command syntax is as follows:
```
add <key> <flags> <exptime> <bytes>
<value>
```
This command outputs can be: `STORED`, `NOT_STORED`, `ERROR`, `SIZE_LIMIT`.
##### replace
This command replaces an existing value with a new one. If key doesn't exist, it is not stored. This command syntax is as follows:
```
replace <key> <flags> <exptime> <bytes>
<value>
```
This command outputs can be: `STORED`, `NOT_STORED`, `ERROR`, `SIZE_LIMIT`.
##### append
This command appends new value to an existing value. If key doesn't exist, it is not stored. This command syntax is as follows:
```
append <key> <flags> <exptime> <bytes>
<value>
```
This command outputs can be: `STORED`, `NOT_STORED`, `ERROR`, `SIZE_LIMIT`.
##### prepend
This command prepends new value to an existing value. If key doesn't exist, it is not stored. This command syntax is as follows:
```
prepend <key> <flags> <exptime> <bytes>
<value>
```
This command outputs can be: `STORED`, `NOT_STORED`, `ERROR`, `SIZE_LIMIT`.
##### cas
cas stands for *Check-And-Set* or *Compare-And-Swap*. This command uses *cas_id* to know data value has been changes since last time we fetch it. If it has been changed, value won't be updated. It is useful especially for cases when more than one client is connected to memcached server (and so there is more than one thread). If key does not exist, it is not stored. This command syntax is as follows:
```
cas <key> <flags> <exptime> <bytes> <cas_id> [noreply]
<value>
```
This command outputs can be: 
- `STORED` key/value is updated successfully
- `NOT_FOUND` key does not exists
- `EXISTS` key exists but its value has been changed since last fetch, so its value is not updated
- `ERROR` an error occurred
##### get
This command fetches key data. This command syntax as follows:
```
get <key>
```
If key exists output will be:
```
VALUE <key> <flags> <bytes>
<value>
END
```
if key does not exist, output will be `END`.
##### gets
This command fetches key data including cas_id. This command syntax is as follows:
```
gets <key>
```
If key exists output will be:
```
VALUE <key> <flags> <bytes> <cas_id>
<value>
END
```
if key does not exist, output will be `END`.
##### delete
This command deletes a key from system. Syntax is as follows:
```
delete <key>
```
This command outputs can be: `NOT_FOUND`, `DELETED`, `ERROR`.
##### flush_all
This command clears all data in the system and returns `OK` as output.
##### incr/decr
These two commands increment/decrement numeric value of a key. Commands syntax is as follows:
```
incr <key> <numeric_value>
decr <key> <numeric_value>
```
These commands outputs can be: 
- `NOT_FOUND` key does not exist
- `CLIENT_ERROR` value of key is not numeric
- `<NEW_NUMERIC_VALUE>` if increment/decrement operation is done successfully, new value will be returned.