from os import SEEK_HOLE
from basics import get_bit


class Node2:
    def __init__(self, vkm, sh, sat=None):
        self.vkm = vkm
        self.sh = sh
        if sat:
            self.sat = sat
        else:
            self.sat = {}
        self.set_bvk()
        self.chdic = self.reduce()

    def set_bvk(self):
        # vkdic has only vk2s in it
        tbit = sorted(self.vkm.bdic.keys())[-1]  # take highst bit at the end
        # take a vk2 with top bit
        self.bvk = self.vkm.remove_vk2(self.vkm.bdic[tbit][0])
        self.crvs = set([self.bvk.compressed_value()])
        self.sh.drop_vars(self.bvk.bits)
        self.vsdic = {
            0: {
                'sat': {self.bvk.bits[0]: 0, self.bvk.bits[1]: 0},
                'sh': self.sh.clone(),
                'child': None
            },
            1: {
                'sat': {self.bvk.bits[0]: 0, self.bvk.bits[1]: 1},
                'sh': self.sh.clone(),
                'child': None
            },
            2: {
                'sat': {self.bvk.bits[0]: 1, self.bvk.bits[1]: 0},
                'sh': self.sh.clone(),
                'child': None
            },
            3: {
                'sat': {self.bvk.bits[0]: 1, self.bvk.bits[1]: 1},
                'sh': self.sh.clone(),
                'child': None
            }
        }
        bdic = self.vkm.bdic
        touched = set(bdic[self.bvk.bits[0]] + bdic[self.bvk.bits[1]])
        while len(touched) > 0:
            tkn = touched.pop(0)
            vk = self.vkm.remove_vk2(tkn)
            cvs, vk1 = self.cvs_vs(vk)
            if vk1:
                new_vk1 = self.trim_vk1(cvs, vk1)
                if new_vk1:
                    touched.append(new_vk1)
            else:
                self.crvs.add(cvs[0])

    def trim_vk1(self, cvs, vk1):
        for v in cvs:
            bit = vk1.bits[0]
            self.vsdic[v]['sat'][bit] = int(not vk1.dic[bit])
            self.vsdic[v]['sh'].drop_vars(bit)
        kn2s = self.vkm.bdic[bit]

    def cvs_vs(self, vk):
        ''' on the 2 bits of bvk, vk hit 1 or 2. In case of vk
            a: hitting 1 bit: 2 values in self.vsdic-keys are returned
              and a vk1 for the not-hit bit
            b: hitting 2 bits: return 1 value (in cvs), sitting on these
               2 bits, and vk1 == None
            return: [<cvs], vk1
            '''
        cvs = []
        if vk.bits == self.bvk.bits:
            cvs.append(vk.compressed_value())
            return tuple(cvs), None
        bvk_bset = set(self.bvk.bits)
        sbit = bvk_bset.intersection(vk.bits).pop()
        ind = self.bvk.bits.index(sbit)
        if ind == 0:
            if vk.dic[sbit] == 0:
                cvs.append(0)
                cvs.apend(1)
            else:  # vk.dic[sbit] == 1
                cvs.append(2)
                cvs.append(3)
        else:
            if vk.dic[sbit] == 0:
                cvs.append(0)
                cvs.append(2)
            else:  # vk.dic[sbit] == 1
                cvs.append(1)
                cvs.append(3)
        vk.drop_bit(sbit)
        return tuple(cvs), vk

    def reduce(self):
        ' break off topbit '
        bdic = self.vkm.bdic
        hit_kns = set(bdic[self.bvk.bits[0]]).union(bdic[self.bvk.bits[1]])
        hit_kns.remove(self.bvk.kname)
        self.vkm.remove_vk2(self.bvk.kname)
        kns = self.vkm.kn2s
        tdic = {}
        for kn in kns:
            if kn in hit_kns:
                knvk = self.vkm.vkdic.pop(kn)
                cvs, vk = self.cvs_vs(knvk)
                if vk:  # vk1 exists. cvs has 2 values
                    for v in cvs:
                        bt = vk.bits[0]
                        bv = vk.hbit_value()
                        self.vsdic[v]['sat'][bt] = int(not bv)
                        self.vsdic[v]['sh'].drop_vars(bt)
                    # tdic.setdefault(cvs, []).append(vk)
                else:
                    # kn has the same bits as bvk: 1 value add to crvs
                    self.crvs.add(cvs[0])
            else:
                pass
        for v in self.vsdic:
            if v in self.crvs:
                continue
            sat = self.vsdic[v]
            for tvs, vks in tdic.items():
                if v in tvs:
                    for vk1 in vks:
                        b = vk1.bits[0]
                        sat[b] = [1, 0][vk1.dic[b]]

        for kn in kns:
            pass
