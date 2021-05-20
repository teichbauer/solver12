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
        self.topbit = bs[-1]
        self.bvk = self.vkm.vkdic[self.vkm.bdic[self.topbit][0]]

    def reduce(self):
        ' break off topbit '
        kns = self.vkm.kn1s + self.vkm.kn2s  # only kn2 exist?
        hit_kns = self.vkm.bdic[self.topbit]
        for kn in hit_kns:
            kns.remove(kn)
            vk = self.vmk.vkdic[kn]
            if self.topbit in vk.bits:
                if vk.dic[self.topbit] == self.bvk[self.topbit]:
                    pass
                else:
                    pass
        for kn in kns:
            pass
