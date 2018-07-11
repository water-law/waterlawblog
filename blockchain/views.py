from uuid import uuid4
from django.conf.urls import url
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from blockchain.block_chain import BlockChain

node_identifier = str(uuid4()).replace('-', '')
blockchain = BlockChain()


class NewTransactionsAPIView(APIView):

    permission_classes = ()

    def post(self, request):
        values = request.data
        # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return Response(data={"message": "Missing values"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Transaction
        index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

        response = {'message': 'Transaction will be added to Block {}'.format(index)}
        return Response(response)


class MineAPIView(APIView):

    permission_classes = ()

    def get(self, request):
        # We run the proof of work algorithm to get the next proof...
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        # 给工作量证明的节点提供奖励.
        # 发送者为 "0" 表明是新挖出的币
        blockchain.new_transaction(
            sender="0",
            recipient=node_identifier,
            amount=1,
        )

        # Forge the new Block by adding it to the chain
        block = blockchain.new_block(proof)

        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return Response(response)


class ChainAPIView(APIView):

    permission_classes = ()

    def get(self, request):
        return Response({
            "chain": blockchain.chain,
            "length": len(blockchain.chain)
        })


class RegisterNodesAPIView(APIView):

    permission_classes = ()

    def get(self, request):
        d = list()
        nodes = blockchain.nodes
        for node in nodes:
            d.append(node)
        return Response({"total_nodes": d})

    def post(self, request):
        values = request.data
        nodes = values['nodes']
        if nodes is None:
            return Response(data={"message": "Error: Please supply a valid list of nodes"}, status=status.HTTP_400_BAD_REQUEST)
        for node in nodes:
            blockchain.register_node(node)
        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes),
        }
        return Response(response)


class ResolveNodesAPIView(APIView):

    permission_classes = ()

    def get(self, request):
        replaced = blockchain.resolve_conflicts()
        if replaced:
            response = {
                "message": "Our chain was replaced",
                "new_chain": blockchain.chain
            }
        else:
            response = {
                "message": "Our chain is authoritative",
                "new_chain": blockchain.chain
            }
        return Response(response)


urlpatterns = [
    url(r'^transactions/new$', NewTransactionsAPIView.as_view()),
    url(r'^mine$', MineAPIView.as_view()),
    url(r'^chain$', ChainAPIView.as_view()),
    url(r'^nodes/register$', RegisterNodesAPIView.as_view()),
    url(r'^nodes/resolve$', ResolveNodesAPIView.as_view()),
]