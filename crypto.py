from ecdsa import SigningKey, VerifyingKey, SECP256k1

def ecdsa_gen_pair_keys(curve=SECP256k1):
    sk = SigningKey.generate(curve)
    pk = sk.verifying_key

    sk_str = str(sk.to_string().hex())
    pk_str = "04" + str(pk.to_string().hex()) # 04 - uncompressed format

    return (sk_str, pk_str)