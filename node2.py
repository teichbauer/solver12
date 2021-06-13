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
        bits = self.clean_vk1s(vkm, self.sat)
        self.sh.drop_vars(bits)
        self.set_bvk()

    def clean_vk1s(self, vkm, sat={}):
        bits = []
        while len(vkm.kn1s) > 0:
            vk1 = vkm.remove_vk1()
            bit = vk1.bits[0]
            sat[bit] = int(not vk1.dic[bit])
            bits.append(bit)
        return bits

    def set_bvk(self):
        if self.sh.ln == 0 or len(self.vkm.kn2s) == 0:
            self.vsdic = None
            return
        # vkdic has only vk2s in it
        tbit = sorted(self.vkm.bdic.keys())[-1]  # take highst bit at the end
        # take a vk2 with top bit
        self.bvk = self.vkm.remove_vk2(self.vkm.bdic[tbit][0])
        self.crvs = set([self.bvk.compressed_value()])
        sh = self.sh.clone().drop_vars(self.bvk.bits)
        ssat = {**self.sat, **{self.bvk.bits[0]: 0, self.bvk.bits[1]: 0}}
        self.vsdic = {
            0: {
                'sat': ssat,
                'sh': sh.clone(),
                'vkm': VK12Manager(Center.maxnov)
            },
            1: {
                'sat': {**ssat, **{self.bvk.bits[1]: 1}},
                'sh': sh.clone(),
                'vkm': VK12Manager(Center.maxnov)
            },
            2: {
                'sat': {**ssat, **{self.bvk.bits[0]: 1}},
                'sh': sh.clone(),
                'vkm': VK12Manager(Center.maxnov)
            },
            3: {
                'sat': {**ssat, **{self.bvk.bits[0]: 1, self.bvk.bits[1]: 1}},
                'sh': sh.clone(),
                'vkm': VK12Manager(Center.maxnov)
            }
        }
        bdic = self.vkm.bdic
        # collect vk1s - first round
        touched = set(bdic[self.bvk.bits[0]] + bdic[self.bvk.bits[1]])
        for tkn in touched:
            vk = self.vkm.remove_vk2(tkn)
            cvs, vk1 = self.cvs_vs(vk)
            if vk1:
                for v in cvs:
                    self.vsdic[v]['vkm'].add_vk1(vk1)
            else:
                self.crvs.add(cvs[0])  # cvs has only 1 value

        if len(self.vkm.vkdic) > 0:
            for v in self.vsdic:
                self.vsdic[v]['vkm'].add_vkdic(self.vkm.vkdic)

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

    def spawn(self):
        if self.sh.ln == 0:
            ssats = [self.sat]
        elif self.vsdic == None:
            while self.sh.ln > 0:
                b = self.sh.pop()
                self.sat[b] = 2
            ssats = [self.sat]
        else:
            ssats = []
            for v in (0, 1, 2, 3):
                if v in self.crvs:
                    del self.vsdic[v]
                    continue
                dic = self.vsdic[v]
                if dic['vkm'].valid and dic['sh'].ln > 0:
                    if len(dic['vkm'].kn1s) > 0:
                        bits = self.clean_vk1s(dic['vkm'], dic['sat'])
                        dic['sh'].drop_vars(bits)
                        if dic['sh'].ln == 0:
                            ssats.append(dic['sat'])
                            continue
                    if len(dic['vkm'].kn2s) == 0:
                        while dic['sh'].ln > 0:
                            b = dic['sh'].pop()
                            dic['sat'][b] = 2
                    else:
                        node2 = Node2(dic['vkm'], dic['sh'], dic['sat'])
                        ssats2 = node2.spawn()
                        pass
                ssats.append(dic['sat'])
        return ssats
