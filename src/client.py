import requests
from argparse import ArgumentParser
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import rest

# All nodes are aware of the ip and the port of the bootstrap
# node, in order to communicate with it when entering the network.
BOOTSTRAP_IP = '127.0.0.1'
BOOTSTRAP_PORT = '5000'

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)


# Run it once fore every node
if __name__ == '__main__':
    # Define the argument parser.
    parser = ArgumentParser(description='A client of noobcash.')
    parser.add_argument('-p', default=5000,
                        type=int, help='port to listen on')
    parser.add_argument('-bootstrap', action='store_true',
                        help='set if the current node is the bootstrap')

    # Parse the given arguments.
    args = parser.parse_args()
    port = args.p
    is_bootstrap = args.bootstrap
