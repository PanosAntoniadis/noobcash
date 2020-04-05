<p align="center">
    <br>
    <img src="webapp/noobcash/static/noobcash/images/logo.png" width="400"/>
    <br>
<p>

<h3 align="center">
A simple blockchain system
</h3>


## About the project

Noobcash is a simple cryptocurrency system. It is a completely decentralized digital currency, without any need for central authority. The transactions made in the system are verified by a network of nodes and recorded in a public distributed ledger, the Noobcash Blockchain. The nodes in our system communicate via a peer-to-peer network using cryptography for the verification processes. 

## Demo

The project is hosted in [https://snf-12208.ok-kno.grnetcloud.net/](https://snf-12208.ok-kno.grnetcloud.net/)/

## Deliverables

1. A rest api that implements the functionality of noobcash and is placed in `src` directory.
2. A cli client placed in `src/tester.py`.
3. A web app in `webapp` directory.

## Setup/Usage

- Install all necessary requirements

    `pip install -r requirements.txt`

- Setup noobcash backend by running the rest api of n nodes.

    ```
    $ python src/rest.py --help
    usage: rest.py [-h] -p P -n N -capacity CAPACITY [-bootstrap]

    Rest api of noobcash.

    optional arguments:
      -h, --help          show this help message and exit

    required arguments:
      -p P                port to listen on
      -n N                number of nodes in the blockchain
      -capacity CAPACITY  capacity of a block

    optional_arguments:
      -bootstrap          set if the current node is the bootstrap
    ```
    
    Note: The file `src/config.py` should contain the ip address of the bootstrap node and the variable LOCAL should change in case of running in a remote server. 

- Run a client client:

     ```
     $ python src/client.py --help

    usage: client.py [-h] -p P

    CLI client of noobcash.

    optional arguments:
      -h, --help  show this help message and exit

    required arguments:
      -p P        port to listen on
    ```


- Run the webapp:


## Technologies used

1. The rest api is written in Python 3.x using the following libraries: Flask, Flask-Cors, pycryptodome, requests and urllib3.
2. The webapp

## Evaluation of the system

We evaluate the performance and the scalability of noobcash by running the system in [okeanos](https://okeanos-knossos.grnet.gr/home/) and perform from each node 100 transcations to the system. The transactions are placed in `/test/transactions` and the scipt for sending them in `test/tester.py`. 


- Performance of the system

 <p float="left">  
    <img src="test/plots/throughput_n5_c.png" width="420"/>
  <img src="test/plots/block_n5_c.png" width="420"/>
 </p>
 
 - Scalability of the system
 
  <p float="left">  
    <img src="test/plots/scalability_t.png" width="420"/>
  <img src="test/plots/scalability_b.png" width="420"/>
 </p>





## Project Structure

- `src/`: Source code of the rest backend and cli client.
- `test/`: Files regarding the evaluation of the system.
- `webapp/`: Files about the web app.

## Contributors

Developed by

<p align="center">
    <a href="https://github.com/PanosAntoniadis"> <img src="webapp/noobcash/static/noobcash/images/antoniadis.png" width="10%"></a>  <a href="https://github.com/Nick-Buzz"><img src="webapp/noobcash/static/noobcash/images/bazotis.png" width="10%"></a>  <a href="https://github.com/ThanosM97"><img src="webapp/noobcash/static/noobcash/images/masouris.png" width="10%"></a>
<p>
    
as a semester project for the Distributed Systems course of NTUA ECE.
