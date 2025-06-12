#!/usr/bin/env python3
import sys
import base58

from Shamir import Shamir

b58 = lambda b: base58.b58encode(b).decode('ascii')
un58 = base58.b58decode


def parseShard(shard):
    p = shard.split('/s/', 1)[1:]

    if p:
        i, k, modulus, share = p[0].split('/')

        return Shamir(modulus=int(modulus), threshold=int(k), shares={
            int(i): un58(share)
        })


def main(*args):
    i = 0
    kn = args[i] if args else ''

    if kn and kn[0] == '-':
        i += 1
    else:
        kn = '--2/3'

    kn = kn.strip('-').split('/')
    k, n = map(int, kn)
    # print(f'k={k} n={n}')

    if i < len(args):
        inp = args[i]
    else:
        inp = sys.stdin.read()

    # print(f'[{len(inp)}] {inp}')

    if inp.startswith('protoseed:/p/'):
        payload = un58(inp.split('/p/', 1)[1])
    else:
        payload = inp.encode('utf-8')

    vv = Shamir.split(payload, k, n)

    shards = [
        f'protoseed:/s/{i}/{k}/{vv.modulus}/{b58(sh)}'
        for i, sh in vv.shares.items()
    ]

    for s in shards:
        print(f'[{len(s)}] {s}')

    xx = None

    for s in shards[:k]:
        s = parseShard(s)

        if xx is None:
            xx = s
        else:
            assert xx.modulus == s.modulus, f'share modulus mismatch {xx.modulus} != {s.modulus}'
            assert xx.threshold == s.threshold, f'share threshold mismatch {xx.threshold} != {s.threshold}'
            xx.shares.update(s.shares)

    zz = xx.recover()
    rr = f'protoseed:/p/{b58(zz)}'
    print(f'[{len(rr)}] {rr}')


if __name__ == "__main__":
    #main(*sys.argv[1:])
    #main('--2/3', 'protoseed:/p/BrpEG4mDZeSPMp7P3q8qAksfpMDdK9LvCTqVQK3PL5v7')
    main('--3/5', 'protoseed:/p/XbzReEu7tajf173v87GgrEP9B5Vm149WdE5Tnbk1PUyGUkiNbDU4UPqWaR72YzLzp2G6TqznkCriVkgCKVYhFj9SjSGFtSEHdNRzTLcHtBGTd2y4QKwmgAkCVzNM8ty528A')
