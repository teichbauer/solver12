from basics import print_json
from vklause import VKlause
from tnode import TNode


class VKManager:
    def __init__(self, vkdic, nov, initial=False):
        self.vkdic = vkdic
        self.nov = nov
        if initial:
            self.make_bdic()

    def clone(self):
        vkdic = {kn: vk.clone() for kn, vk in self.vkdic.items()}
        vkm = VKManager(vkdic, self.nov)
        vkm.bdic = {b: s.copy() for b, s in self.bdic.items()}

    def printjson(self, filename):
        print_json(self.nov, self.vkdic, filename)

    def make_bdic(self):
        self.bdic = {}
        for kn, vk in self.vkdic.items():
            for b in vk.dic:
                if b not in self.bdic:      # hope this is faster than
                    self.bdic[b] = set([])  # bdic.setdefault(b,set([]))
                self.bdic[b].add(kn)

    def morph(self, snode):
        chs = {}  # {<cvr-val>: {kn, ..},..}
        excl_cvs = set([])
        kns = list(self.vkdic.keys())
        vk3dic = {}

        tdic = {}
        for kn in kns:
            vk = self.vkdic[kn]
            if vk.kname in snode.vk12dic:
                vk12 = snode.vk12dic
            else:
                vk12, vk3, cvr = snode.sh.reduce_vk(vk)
                if vk3:
                    vk3dic[kn] = vk3
                elif vk12:
                    vk12.cvr = cvr
                    snode.vk12dic[vk12.kname] = vk12
                else:
                    excl_cvs.add(cvr)
            if vk12:
                tdic.setdefault(tuple(vk12.cvr), []).append(vk12)

        if len(tdic) == 0:
            return None, None
        # 2**3 == 8 - number of possible children of the satnoe,
        for val in range(8):
            if val in excl_cvs:
                continue
            sub_vk12dic = {}
            for cvr in tdic:
                if val in cvr:  # touched kn/kv does have outside bit
                    vks = tdic[cvr]
                    for vk in vks:
                        sub_vk12dic[vk.kname] = vk.clone()
            # print(f'child-{val}')
            tnode = TNode(sub_vk12dic, snode, val)
            if tnode.vkm.valid:
                TNode.repo[tnode.name] = tnode
                chs[val] = tnode
        # re-make self.bdic, based on updated vkdic (now all 3-bit vks)
        self.make_bdic()  # bdic made here will be used for .next/bestchoice
        # for making chdic with tnodes
        return VKManager(vk3dic, self.nov - 3, True), chs
    # enf of def morph()

    def bestchoice(self):
        "return: {'bestkey': (tkn1, tkn2,),'bits': bits[,,],'touched':[,,..,]}"
        best_choice = None
        max_tsleng = -1
        max_tcleng = -1
        best_bits = None
        kns = set(self.vkdic.keys())  # candidates-set of kn for besy-key
        while len(kns) > 0:
            kn = kns.pop()
            vk = self.vkdic[kn]
            # sh_sets: {<bit>:<set of kns sharing this bit>,..} for each vk-bit
            sh_sets = {}  # dict keyed by bit, value is a set of kns on the bit
            bits = vk.bits
            for b in bits:
                sh_sets[b] = self.bdic[b].copy()
            # dict.popitem() pops a tuple: (<key>,<value>) from dict
            tsvk = sh_sets.popitem()[1]  # [0] is the bit/key, [1] is the set
            tcvk = tsvk.copy()
            for s in sh_sets.values():
                tsvk = tsvk.intersection(s)
                tcvk = tcvk.union(s)

            chc = (tsvk, tcvk - tsvk)
            kns -= tsvk  # take kns in tsvk out of candidates-set
            ltsvk = len(tsvk)
            if ltsvk < max_tsleng:
                continue
            ltcvk = len(tcvk)
            if not best_choice:
                best_choice = chc
                max_tsleng = ltsvk
                max_tcleng = ltcvk
                best_bits = bits
                # best_bitsum = sum(bits)
            else:
                if best_choice[0] == tsvk:
                    continue
                # see if to replace the best_choice?
                replace = False
                if max_tsleng < ltsvk:
                    replace = True
                elif max_tsleng == ltsvk:
                    if max_tcleng < ltcvk:
                        replace = True
                    elif max_tcleng == ltcvk:
                        if bits > best_bits:
                            replace = True
                if replace:
                    best_choice = chc
                    max_tsleng = ltsvk
                    max_tcleng = ltcvk
                    best_bits = bits
        result = {
            'bestkey': tuple(sorted(list(best_choice[0]))),
            'touched': best_choice[1],
            'bits': best_bits
        }
        return result
    # end of def bestchoice(self):
