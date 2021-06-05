from vk12mgr import VK12Manager
from center import Center
from basics import get_bit


class Node2:
    def __init__(self, vkm, sh, sat=None):
        self.vkm = vkm
        self.sh = sh
        if sat:
            self.sat = sat
        else:
            self.sat = {}
        self.valid = self.set_bvk()
        if self.valid:
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
        # collect vk1s - first round
        touched = set(bdic[self.bvk.bits[0]] + bdic[self.bvk.bits[1]])
        vk1m = VK12Manager(Center.maxnov)
        self.cvs_dic = {}  # {<cv>:[kn1,kn1,..], ...}
        for tkn in touched:
            vk = self.vkm.remove_vk2(tkn)
            cvs, vk1 = self.cvs_vs(vk)
            if vk1:
                vk1m.add_vk1(vk1)  # cvs has 2 values
                for v in cvs:
                    self.cvs_dic.setdefault(v, []).append(vk1)
            else:
                self.crvs.add(cvs[0])  # cvs has only 1 value
        if not vk1m.valid:
            return False

        # see if any left-over vk2 touched by any vk1 and becomes vk1
        bs = list(vk1m.bdic.keys())
        for b in bs:
            if b in self.vkm.bdic and len(self.vkm.bdic[b]) > 0:
                for kn in self.vkm.bdic[b]:
                    vk2 = self.vkm.remove_vk2(kn)
                    self.sh.drop_vars(vk2.bits)
                    added = vk1m.add_vk2(vk2)
                    if not vk1m.valid:
                        break
                    if added:
                        for v in (0, 1, 2, 3):
                            self.cvs_dic[v] = vk1m.vkdic[kn]
                if not vk1m.valid:
                    return False
        return True

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
        # vk1m has only vk1s in ti
        if len(self.vkm.kn2s) > 0:
            pass
        else:
            for v in (0, 1, 2, 3):
                if v in self.crvs:
                    del self.vsdic[v]
                    continue
                if v in self.cvs_dic:
                    for vk1 in self.cvs_dic[v]:
                        bit = vk1.bits[0]
                        self.vsdic[v]['sat'][bit] = int(not vk1.dic[bit])
                        self.vsdic[v]['sh'].drop_vars(bit)
                else:
                    for var in self.vsdic[v]['sh'].varray:
                        self.vsdic[v]['sat'][var] = 2
                    self.vsdic[v]['sh'] = None
