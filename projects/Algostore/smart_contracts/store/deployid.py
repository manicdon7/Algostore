import base64
from algosdk.v2client.algod import AlgodClient
from algosdk.transaction import ApplicationCreateTxn, OnComplete, StateSchema
from algosdk import mnemonic, account

# Replace these with your actual values
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
mnemonic_phrase = "frown scatter young voyage token smooth own mango category lounge improve phrase metal mystery glide zone leisure valve hurt bus end educate together ability enough"
private_key = mnemonic.to_private_key(mnemonic_phrase)
public_address = account.address_from_private_key(private_key)

# Initialize the Algod client
algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Function to compile TEAL code to bytecode with detailed error handling
def compile_teal(client, teal_source):
    compile_response = client.compile(teal_source)
    print(f"Compile Response: {compile_response}")  # Debug print to inspect the response
    if "result" in compile_response:
        # Decode the base64 result to bytes
        return base64.b64decode(compile_response['result'])
    else:
        raise Exception(f"TEAL compilation failed: {compile_response}")

# Load and compile the TEAL programs
with open("Store.approval.teal", "r") as f:
    approval_program_source = f.read()

try:
    approval_program = compile_teal(algod_client, approval_program_source)
except Exception as e:
    print(f"Failed to compile approval program: {e}")
    exit(1)

with open("Store.clear.teal", "r") as f:
    clear_program_source = f.read()

try:
    clear_program = compile_teal(algod_client, clear_program_source)
except Exception as e:
    print(f"Failed to compile clear program: {e}")
    exit(1)

# Define the application's schema
global_schema = StateSchema(num_uints=0, num_byte_slices=1)
local_schema = StateSchema(num_uints=0, num_byte_slices=0)

# Get network params for transactions
params = algod_client.suggested_params()

# Create the application
txn = ApplicationCreateTxn(
    sender=public_address,
    sp=params,
    on_complete=OnComplete.NoOpOC.real,
    approval_program=approval_program,
    clear_program=clear_program,
    global_schema=global_schema,
    local_schema=local_schema,
)

# Sign the transaction
signed_txn = txn.sign(private_key)

# Send the transaction
tx_id = algod_client.send_transaction(signed_txn)

# Wait for the transaction to be confirmed
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    while True:
        txinfo = client.pending_transaction_info(txid)
        if txinfo.get('confirmed-round', 0) > 0:
            return txinfo
        print(f'Waiting for confirmation... Last round: {last_round}')
        client.status_after_block(last_round + 1)
        last_round += 1

confirmed_txn = wait_for_confirmation(algod_client, tx_id)

# Extract the application ID from the confirmed transaction
app_id = confirmed_txn["application-index"]
print(f"Deployed app with ID: {app_id}")
