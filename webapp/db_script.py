import json

from node.models import Node

with open('nodes.json') as f:
    nodes_json = json.load(f)

for n in nodes_json:
    node = Node(node_id=n["node_id"], IP=n["IP"], PORT=n["PORT"])
    node.save()
