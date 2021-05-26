from basics import get_bit


class Node2:
    def __init__(self, vkm, sat=None):
        self.vkm = vkm
        if not sat:
            self.sat = {}
        self.set_bvk()
        self.reduce()

    def set_bvk(self):
        bs = list(self.vkm.bdic.keys())
        bs.sort()  # highst bit at the end
        tbit = bs[-1]
        self.bvk = self.vkm.vkdic[self.vkm.bdic[tbit][0]]

    def cvs_vs(self, vk):
        ' return: 1 or 2 covered-values in [0..3], and vk1(or None) '
        cvs = []
        if vk.bits == self.bvk.bits:
            cvs.append(vk.compressed_value())
            return tuple(cvs), None
        sbit = self.bvk_bset.intersection(vk.bits).pop()
        vk.drop_bit(sbit)
        ind = self.bvk.bits.index(sbit)
        if ind == 0:
            if vk.dic[sbit] == 0:
                cvs.apend(0)
                cvs.apend(1)
            else:  # vk.dic[sbit] == 1
                cvs.apend(2)
                cvs.apend(3)
        else:
            if vk.dic[sbit] == 0:
                cvs.apend(0)
                cvs.apend(2)
            else:  # vk.dic[sbit] == 1
                cvs.apend(1)
                cvs.apend(3)
        return tuple(cvs), vk

    def reduce(self):
        ' break off topbit '
        bdic = self.vkm.bdic
        self.bvk_bset = set(self.bvk.bits)
        self.crvs = set([self.bvk.compressed_value()])
        hit_kns = set(bdic[self.bvk.bits[0]]).union(bdic[self.bvk.bits[1]])
        hit_kns.remove(self.bvk.kname)
        self.vkm.remove_vk2(self.bvk.kname)
        kns = self.vkm.kn2s
        tdic = {}
        for kn in kns:
            if kn in hit_kns:
                cvs, vk = self.cvs_vs(self.vkm.vkdic[kn])
                if vk:
                    tdic.setdefault(cvs, []).append(vk)
                self.vkm.remove_vk2(kn)
        vsdic = {
            0: {self.bvk.bits[0]: 0, self.bvk.bits[1]: 0},
            1: {self.bvk.bits[0]: 0, self.bvk.bits[1]: 1},
            2: {self.bvk.bits[0]: 1, self.bvk.bits[1]: 0},
            3: {self.bvk.bits[0]: 1, self.bvk.bits[1]: 1}
        }
        for v in vsdic:
            if v in self.crvs:
                continue
            sat = {}
            for b in (0, 1):
                sat[self.bvk.bits[b]] = get_bit(v, b)
            for tvs, vks in tdic.items():
                if v in tvs:
                    for vk1 in vks:
                        b = vk1.bits[0]
                        sat[b] = [1, 0][vk1.dic[b]]

        for kn in kns:
            pass
