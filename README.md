# protoseed - Bitcoin seed phrases and 2FA

A protoseed is simply a data-like URI containing entropy that is used to either backup
a Bitcoin wallet seed (or any crypto wallet), or provide true 2FA protection
(something you know and something you have) for an otherwise software-only wallet. The
details are explained below.

The preferred physical form of a protoseed is in a QR-code that is either 3D printed or
laser etched on to metal. Because this process may be outsourced to 3rd parties, it is
obvious that the data contained in a protoseed is not necessarily fully private. This is
compensated for by combining the protoseed with a user-known pass phrase. A pass phrase
of 4 or 5 randomly generated words of common English should provide decades or more of
security.

This method of wallet seed protection will be compared below to these other approaches
in use today:

 - Exported seed phrase
 - Seedless solutions (like Tangem or Bitkey)

![](src/round.png)

## Anatomy of a Protoseed

A protoseed URI starts with `protoseed:/` and comes in two forms:

 - Complete seed (`protoseed:/p/...`)
 - Shamir-based seed shard (`protoseed:/s/...`)

Below is a 32-byte entropy protoseed:

    protoseed:/p/BrpEG4mDZeSPMp7P3q8qAksfpMDdK9LvCTqVQK3PL5v7

The following are 3 shards (of 2 required) for that protoseed:

    protoseed:/s/1/2/320/2BfRVypkqQgfgVTobALSJsnoRdSVMdKwFHcRfq8duGxrPjHTEGMcEyM
    protoseed:/s/2/2/320/3NKqzxeWfp9frs8VyzFxzLvHaFxPWfNaU1eYFR4fvF3CBZRMTZ6CPh1
    protoseed:/s/3/2/320/4YzGVwUGWDcg3EoCNpBVfp3mitUHfhRDgjgepzzhwD7XyPZFgqpnYQf

A more typical protoseed contains 96-bytes of entropy (144 character URI):

    protoseed:/p/XbzReEu7tajf173v87GgrEP9B5Vm149WdE5Tnbk1PUyGUkiNbDU4UPqWaR72YzLzp2G6TqznkCriVkgCKVYhFj9SjSGFtSEHdNRzTLcHtBGTd2y4QKwmgAkCVzNM8ty528A

Here are 5 protoseed shards (of 3 required) for the above protoseed (197 character URI):

    protoseed:/s/1/3/1024/V9d3cPcDaPWWAVTTsTvHoVLTqK7jcqYnA93z92jrRbyUT5ZwwCWLFV6ghT5v2D2LWjwtrLtGTikDdStqj25pSKdVUAxZYKNS4DJud7BYyjF6mShfmnoGy9cWzbq5DapnvYjPX96AtnH9C73PGbxZBCLkG7pk3rgnXjnBUjLNTpm1wA
    protoseed:/s/2/3/1024/AdKRSDRdqoUBqjERLCG2HtT2a3shSviL91v5eQAHKPPEDjUc8gFmThEZmaP5Fim2ojbwAjm11B7eMFQnVDgxB68J1axDP88GxPCMJrbSZAPoqyJ66j4AwpqAZ6dP66zm552jtkAKVub2F1R33VedpPpFzhYwZr7DBvAo6VYKmtDij9H
    protoseed:/s/3/3/1024/2E765afCa1PfH65H69MsHAQNm2U63XdPqacVoNBPW7ZomaNB5iA5tk8pDo9dPkb8hyLkY4Qb8GmbHgUuPstjNDDpDxT7iYd7d6t2wkHbGHgYPGY4v3QAgVNvuS35yRwtFtKBdk3Uc7mzTn24VnwhN6t4Z5tBxtLcoaA3nwT7VBpZrPa
    protoseed:/s/4/3/1024/2Uuw4wYBhs1JYrAeFYntyiq5bPJwcpah7qwtdTJJJNwmyebtUrgVBn8jCz87gQhnDA6eAH5rH65HtkZhfGDqP3CJoFzYbNMs1JgEuq4U9WxehNbKKPjjmHG3KKmFr6AMfr7XqNSxd24vVyp4U61MnQ7cCzmBWWXggAaqtpx56csA674
    protoseed:/s/5/3/1024/BPjxQJ4bFNK7f1WWpQZ7PZj958QGAoaDyovG8fX1iBX8qxBkL7pyLoEJj9JY7h6yKHsc3PnnTd2kATfBHNgGDa3mjVaW1bLX6zayD6v5CrE8nHTqJn4tCCUVnmoti5eBJxRnVdNmYcTpMco2xNqd5HWtxSBvCigQohTBQA3CcBMVSHj

As a QR-code, a protoseed URI can be associated with a wallet application that will be
launched whenever the user scans a protoseed.

## Use Cases

### Mobile / Software Wallets

A typical software wallet (often called a "hot" wallet) generates and locally stores a seed
phrase that is used to generate wallet private keys, public keys, addresses, etc.. Many
software wallets offer optional integration with hardware devices that allow the seed phrase
(and generated private keys) to reside only on the hardware device, for added security.

#### 1 - Import Wallet

In this use case, the Wallet will use a protoseed (typically scanned from a QR-code) and a
pass phrase provided by the user to generate the final wallet seed phrase (the exact derivation
process is documented below) and store it locally. In this case, the protoseed acts like a
backup of the Wallet. The Wallet is still classified as "hot" since it has the necessary keys
to sign transactions.

#### 2 - Watch-only Wallet w/2FA signing

In this use case, the Wallet scans the protoseed and gathers the pass phrase from the user as
above, however, the Wallet only stores what is need to watch for transactions. Optionally, the
Wallet could store the pass phrase, but would NOT store the final seed phrase or private keys.
This means that the Wallet cannot sign transactions, but only show balances.

To sign a transaction, the Wallet must ask the user to provide the protoseed (QR-code) and
possibly re-enter the pass phrase. The Wallet would then derive the seed phrase / private key
and use it to sign the transaction. The Wallet would not store these keys once the transaction
had been signed, so further transactions would also need to scan the protoseed and/or ask for
the pass phrase.

This configuration means that the Wallet is no longer a "hot" wallet. It could be described as
"cold" at rest, or possibly a "warm" wallet. The protoseed QR-code acts as a passive 2FA device
(something you have), and if the pass phrase is not stored, it is multi-factor.

### Hardware Wallets

If the hardware wallet has a camera, it can scan the protoseed QR-code and import the wallet
as would a software wallet. The difference is that the secrets are stored in the hardware
device as normal, but there is no longer a need to view the seed phrase and write it down or
etch it on metal plates, etc.. The protoseed acts as a backup for the hardware wallet, but
it is better than a normal seed phrase backup in that an exposed protoseed does not reveal
anything sensitive about the wallet. Compare this to a normal, clear text seed phrase.
