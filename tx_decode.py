#!/usr/bin/env python3

"""
"""

import argparse
import binascii

import web3
from web3.exceptions import InvalidAddress


def is_ethereum_address(address):
    # print('Testing', address)
    try:
        web3.Web3.to_checksum_address(address)
        return True
    except (InvalidAddress, ValueError, binascii.Error):
        return False


def hex_to_possible_types(hex_string):
    try:
        decoded_hex = binascii.unhexlify(hex_string)
    except binascii.Error:
        return []

    int_value = int(hex_string, 16)
    uint256_value = int_value
    # Interpret large values (> 2^255) as negative numbers (two's complement)
    int256_value = int_value if int_value < 2 ** 255 else int_value - 2 ** 256

    possible_types = [
        ("bytes", decoded_hex.hex()),
        ("string", decoded_hex.decode(errors='ignore')),
        ("uint256", uint256_value),
        ("int256", int256_value),
    ]

    # Check if the last 40 characters (20 bytes) could be an address
    possible_address = '0x' + hex_string[-40:]
    if is_ethereum_address(possible_address):
        possible_types.append(("address", possible_address))

    return possible_types


def check_for_signature(data_list_types):
    last_v, last_r, last_s = data_list_types[-3:]
    if len(last_v) > 0 and len(last_r) > 0 and len(last_s) > 0:
        signature = (last_v, last_r, last_s)
        # Remove the signature from the data_list_types
        # data_list_types = data_list_types[:-3]
    else:
        signature = None
    return signature


def decode_transaction_data(data):
    function_signature = data[:10]
    inputs = data[10:]

    data_list = [inputs[n:n + 64] for n in range(0, len(inputs), 64)]

    data_list_types = [hex_to_possible_types(data) for data in data_list]

    # Check the last three items for signature
    try:
        signature = check_for_signature(data_list_types)
    except ValueError:
        signature = None

    return function_signature, data_list_types, signature


if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument('data', type=str)
    args = args.parse_args()
    s, l, sig = decode_transaction_data(args.data)
    print('[+] Selector:', s)
    print('[+] Parameters: ')
    for x, param in enumerate(l):
        print(f'[+] Parameter {x} possible data types: ')
        for possible_data_type in param:
            print(possible_data_type)
    if sig:
        if len(sig):
            final_signature_string = ''
            for x in sig:
                for _type in x:
                    if _type[0] == 'bytes':
                        final_signature_string += _type[1]
            print('[+] Signature', final_signature_string)
