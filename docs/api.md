# API

This section describes the HTTP API for interaction with nodes.

## Kill
Only kill node process.

```console
root@pc:~$ curl -X POST localhost:8080 -d 'action=kill'
```
#### Return
none.

## Reset
Kill and after $time seconds reopen node process.

```console
root@pc:~$ curl -X POST localhost:8080 -d 'action=reset&time=2'
```
#### Return
none.

## Suspend
Suspend and after $time seconds resume node process. In this mode, the volatile memory of the node is kept intact.

```console
root@pc:~$ curl -X POST localhost:8080 -d 'action=suspend&time=2'
```
#### Success
{"status": "success"}
#### Failure
none.

## Add Author
Add an Author on the blockchain. Returns the author's private key which must be kept secret and will be requested for publish updates.

```console
root@pc:~$ curl -X POST localhost:8080 -d 'action=add_author&json={"org":"G3PD","email":"admin@g3pd.com.br","password":"db3fef373cb224f4f66da38e4001401af969c629171f4f7fbdeb457fe4a94001"}'
```

#### Success
{"private_key": "350af17a370a3367f3c2d215c164e66432a1ef0740163c26205e3dacb4ede00f", "status": "success"}
#### Failure
{"status": "error", "msg": "network not available."}
