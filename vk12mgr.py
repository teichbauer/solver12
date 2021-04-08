from vklause import VKlause
from basics import get_bit, oppo_binary


class VK12Manager:
    # debug = True
    debug = False

    def __init__(self, nov, vkdic=None, raw=False):
        self.nov = nov
        self.valid = True  # no sat possible/total hit-blocked
        if not raw:
            self.reset()  # set vkdic, bdic, kn1s, kn2s
        if vkdic and len(vkdic) > 0:
            self.add_vkdic(vkdic)

    def reset(self):
        self.bdic = {}
        self.vkdic = {}
        self.kn1s = []
        self.kn2s = []
        self.info = []

    def clone(self):
        # self.valid must be True. Construct with: no vkdic, raw=True(no reset)
        vk12m = VK12Manager(self.nov, None, True)
        vk12m.bdic = {k: lst[:] for k, lst in self.bdic.items()}
        vk12m.kn1s = self.kn1s[:]
        vk12m.kn2s = self.kn2s[:]
        vk12m.info = []  # info starts fresh, no taking from self.info
        vk12m.vkdic = {kn: vk.clone() for kn, vk in self.vkdic.items()}
        return vk12m

    def add_vkdic(self, vkdic):
        for vk in vkdic.values():
            self.add_vk(vk)

    def add_vk(self, vk):
        if vk.nob == 1:
            self.add_vk1(vk)
        elif vk.nob == 2:
            self.add_vk2(vk)
    # end of def add_vk(self, vk):

    def add_vk1(self, vk):
        if self.debug:
            print(f'adding vk1: {vk.kname}')
        bit = vk.bits[0]
        knames = self.bdic.setdefault(bit, [])
        # kns for loop usage. can't use knames directly, for knames may change
        kns = knames[:]  # kns for loop:can't use knames, for it may change.
        for kn in kns:
            if kn in self.kn1s:
                if kn not in self.bdic[bit]:  # bdic may have been updated, so
                    continue  # kn may no more be in there on this bit any more
                vk1 = self.vkdic[kn]
                if self.debug and bit != vk1.bits[0]:
                    print(f'bit: {bit} vs. {vk1.bits[0]}')
                    raise Exception("bit conflict")
                if vk1.bits[0] != bit:
                    debug = 1
                # if self.vkdic[kn].dic[bit] != vk.dic[bit]:
                if vk1.dic[bit] != vk.dic[bit]:
                    self.valid = False
                    msg = f'vk1:{vk.kname} vs {kn}: valid: {self.valid}'
                    self.info.append(msg)
                    if self.debug:
                        print(msg)
                    return False
                else:  # self.vkdic[kn].dic[bit] == vk.dic[bit]
                    self.info.append(f'{vk.kname} duplicats {kn}')
                    if self.debug:
                        print(self.info[-1])
                    return False
            elif kn in self.kn2s:
                vk2 = self.vkdic[kn]
                if bit in vk2.bits:
                    if vk2.dic[bit] == vk.dic[bit]:
                        # a vk2 has the same v on this bit: remove vk2
                        self.info.append(f'{vk.kname} removes {kn}')
                        if self.debug:
                            print(self.info[-1])
                        self.remove_vk2(kn)
                    else:  # vk2 has diff val on this bit
                        self.info.append(f'{vk.kname} made {kn} vk1 ')
                        if self.debug:
                            print(self.info[-1])
                        # remove vk2
                        # drop bit from it(it becomes vk1)
                        # add it back as vk1
                        self.remove_vk2(kn)
                        vk2.drop_bit(bit)
                        self.add_vk1(vk2)
        # add the vk
        self.vkdic[vk.kname] = vk
        self.kn1s.append(vk.kname)
        knames.append(vk.kname)
        return True

    def add_vk2(self, vk):
        if self.debug:
            print(f'adding vk2: {vk.kname}')
        # if an existing vk1 covers vk?
        for kn in self.kn1s:
            b = self.vkdic[kn].bits[0]
            if b in vk.bits:
                if self.vkdic[kn].dic[b] == vk.dic[b]:
                    # vk not added. but valid is this still
                    self.info.append(f'{vk.kname} blocked by {kn}')
                    if self.debug:
                        print(self.info[-1])
                    return False
                else:  # vk1 has diff value on this bit
                    # drop this bit, this vk1 becomes vk1. Add this vk1
                    self.info.append(f'{kn} makes {vk.kname} vk1')
                    if self.debug:
                        print(self.info[-1])
                    vk.drop_bit(b)
                    return self.add_vk1(vk)
        # find vk2s withsame bits
        pair_kns = []
        for kn in self.kn2s:
            if self.vkdic[kn].bits == vk.bits:
                pair_kns.append(kn)
        bs = vk.bits
        for pk in pair_kns:
            pvk = self.vkdic[pk]
            if pvk.bits != vk.bits:  # pvk may have been modified, and
                continue  # is no more a pair with vk. In that case, jump over
            if vk.dic[bs[0]] == pvk.dic[bs[0]]:
                if vk.dic[bs[1]] == pvk.dic[bs[1]]:
                    self.info.append(f'{vk.kname} douplicates {kn}. not added')
                    if self.debug:
                        print(self.info[-1])
                    return False  # vk not added
                else:  # b0: same value, b1 diff value
                    msg = f'{vk.kname} + {pvk.kname}: {pvk.kname}->vk1'
                    self.info.append(msg)
                    self.info.append(f'{vk.kname} not added')
                    if self.debug:
                        print(self.info[-1])
                        print(self.info[-2])
                    # remove pvk
                    self.remove_vk2(pvk.kname)
                    pvk.drop_bit(bs[1])
                    self.add_vk(pvk)  # validity made when add pvk as vk1
                    return False   # vk not added.
            else:  # b0 has diff value
                if vk.dic[bs[1]] == pvk.dic[bs[1]]:
                    # b1 has the same value
                    msg = f'{vk.kname} + {pvk.kname}: {pvk.kname}->vk1'
                    self.info.append(msg)
                    self.info.append(f'{vk.kname} not added')
                    if self.debug:
                        print(self.info[-1])
                        print(self.info[-2])
                    # remove pvk
                    self.remove_vk2(pvk.kname)
                    # add pvk back as vk1, after dropping bs[1]
                    pvk.drop_bit(bs[0])
                    return self.add_vk(pvk)
                    return False    # vk not added
                else:  # non bit from vk has the same value as pvk's
                    pass
        for b in bs:
            self.bdic.setdefault(b, []).append(vk.kname)
        self.kn2s.append(vk.kname)
        self.vkdic[vk.kname] = vk
        return True

    def remove_vk2(self, kname):
        if kname not in self.kn2s or kname not in self.vkdic:
            raise Exception(f'{kname} not in for removal')
        self.kn2s.remove(kname)
        vk = self.vkdic.pop(kname)
        for b in vk.bits:
            self.bdic[b].remove(kname)
        return vk

    def pick_bvk(self):
        if len(self.kn1s) > 0:
            return self.vkdic[self.kn1s[0]]
        else:
            return self.vkdic[self.kn2s[0]]

    def morph(self, n12):
        n12.vk12dic = {}
        chs = {}
        excl_cvs = set([])
        # all possible values: for 2 bits:(0,1,2,3); for 1 bit: (0,1)
        allvalues = [(0, 1), (0, 1, 2, 3)][n12.sh.ln == 2]
        tdic = {}

        for kn, vk in self.vkdic.items():
            bs = vk.bits[:]
            out_bits = set(bs) - set(n12.sh.varray)
            if len(out_bits) == 0:
                if vk.nob == n12.sh.ln:
                    excl_cvs.add(vk.compressed_value())
                elif vk.hit(n12.hsat):
                    raise Exception(f'Wrong vk: {vk.kname}')
                else:
                    pass  # drop this vk
            elif len(out_bits) == vk.nob:
                # vk is totally outside of sh
                tdic.setdefault(allvalues, []).append(vk)
            else:
                # vk divided: in sh 1 bit, out 1 bit
                outb = out_bits.pop()
                vk12 = VKlause(vk.kname, {outb: vk.dic[outb]}, vk.nov)
                bs.remove(outb)  # bs now has only 1 of vk that is in sh
                in_index = n12.sh.varray.index(bs[0])
                vs = []
                for v in allvalues:
                    if get_bit(v, in_index) == vk.dic[bs[0]]:
                        vs.append(v)
                tdic.setdefault(tuple(vs), []).append(vk12)

        for val in allvalues:
            if val in excl_cvs:
                continue
            sub_vk12dic = {}
            for cvr in tdic:
                if val in cvr:  # kv does have outside bit
                    vks = tdic[cvr]
                    for vk in vks:
                        sub_vk12dic[vk.kname] = vk.clone()
            vkm = VK12Manager(self.nov - n12.sh.ln, sub_vk12dic)
            if vkm.valid:
                node = n12.__class__(
                    n12,               # n12 is parent-node
                    n12.next_sh,       # sh
                    n12.sh.get_sats(val),  # val -> hsat
                    vkm)
                chs[val] = node
        return chs  # for making chdic with tnodes
