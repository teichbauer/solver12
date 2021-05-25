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

    def reduce(self):
        ' break off topbit '
        kns = self.vkm.kn2s  # there should be no kn1. only kn2 exist
        bdic = self.vkm.bdic
        bvk_bset = set(self.bvk.bits)
        hit_kns = set(bdic[self.bvk.bits[0]]).union(self.bvk.bits[1])
        hit_kns.remove(self.bvk.kname)
        crvs = [self.bvk.compressed_value()]
        for kn in kns:
            if kn in hit_kns:
                vk = self.vkm.vkdic[kn]
                if vk.bits == self.bvk.bits:
                    crvs.append(vk.compressed_value())
                else:
                    # the single shared bit (bvk and vk)
                    # sbit = bvk_bset.intersection(vk.bits).pop()
                    vs = vk.compressed_value(self.bvk.bits)
                kns.remove(kn)
            vk = self.vmk.vkdic.pop(kn)
            if vk.dic[self.topbit] == self.bvk[self.topbit]:
                vk.dic.pop(self.topbit)
            else:
                pass
        for kn in kns:
            pass
