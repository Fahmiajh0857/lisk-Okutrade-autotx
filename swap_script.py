import requests
import time
from web3 import Web3
from eth_account import Account

# === Configuration ===
OKU_API_URL = "https://api.oku.trade/v1"
LISK_RPC = "https://rpc.lisk.com"  # Update if needed
PRIVATE_KEY = "your_private_key_here"  # Replace with your private key
web3 = Web3(Web3.HTTPProvider(LISK_RPC))
account = Account.from_key(PRIVATE_KEY)
WALLET_ADDRESS = account.address

# Replace with actual contract addresses
USDC_CONTRACT = "0xF242275d3a6527d877f2c927a82D9b057609cc71"
USDT_CONTRACT = "0x05D032ac25d322df992303dCa074EE7392C117b9"

# === User Input ===
amount_in_usd = float(input("Enter the amount per swap ($): "))  # User sets swap amount
amount = int(amount_in_usd * (10**6))  # Assuming USDC/USDT have 6 decimals
num_cycles = int(input("Enter the number of swaps: "))  # User sets swap count

# === Function to Get Best Swap Quote ===
def get_best_swap(token_in, token_out, amount):
    url = f"{OKU_API_URL}/swap/v1/quote?sellToken={token_in}&buyToken={token_out}&sellAmount={amount}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# === Function to Execute Swap ===
def execute_swap(token_in, token_out, amount):
    quote = get_best_swap(token_in, token_out, amount)
    if not quote:
        print(f"Failed to get quote for {token_in} → {token_out}")
        return False

    tx = {
        "from": WALLET_ADDRESS,
        "to": quote["to"],
        "data": quote["data"],
        "gas": int(quote["gas"]),
        "gasPrice": web3.to_wei(quote["gasPrice"], "gwei"),
        "value": int(quote["value"]),
        "nonce": web3.eth.get_transaction_count(WALLET_ADDRESS),
        "chainId": web3.eth.chain_id
    }

    # Sign & Send Transaction
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Transaction sent: {web3.to_hex(tx_hash)}")

    # Wait for confirmation
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print(f"Swap {token_in} → {token_out} successful!")
        return True
    else:
        print(f"Swap {token_in} → {token_out} failed!")
        return False

# === Loop for Automated Swaps ===
for i in range(num_cycles):
    print(f"\n=== Swap Cycle {i+1}/{num_cycles} ===")

    # USDC → USDT
    if execute_swap(USDC_CONTRACT, USDT_CONTRACT, amount):
        time.sleep(10)  # Short delay to prevent spamming the network

        # USDT → USDC
        if execute_swap(USDT_CONTRACT, USDC_CONTRACT, amount):
            print(f"Cycle {i+1} completed successfully!")
        else:
            print(f"Cycle {i+1} failed on USDT → USDC swap!")
            break  # Stop the loop if a swap fails
    else:
        print(f"Cycle {i+1} failed on USDC → USDT swap!")
        break

print("\nAll swap cycles completed!")
          
