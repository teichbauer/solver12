from vk12mgr import VK12Manager
from node12 import Node12
from center import Center
from basics import nov_val, get_bit


class PathManager:
    # debug = False
    debug = True
    ''' -----------------------------------------------------------------------
       Each tnode has self.pthmgr(instance of PathManager class), with *.dic:
         {<vkey>:<vkmgr>,...}, where <vkey> is concadinated key(hp isnt top):
         <tnode.val>-<higher-level-tn.val>-<hl-tn.val>... last tn is top-level
       <vkmgr> is the result of mergings of all tn.vkdic along the way,
       including self.tnode.vkdic. If merging not valid, then this
       tnode.pthmgr.dic entry will not be created.
       ---------------------------------------------------------------------'''

    def __init__(self, tnode, final=False):  # snode.done==final
        # constructed only for tnode, with its holder being non-top level
        self.tnode = tnode
        if self.debug:
            print(f'making pth-mgr for {tnode.name}')
        self.dic = {}
        hp_chdic = tnode.holder.parent.chdic
        if tnode.holder.parent.is_top():  # holder.parent: a top-level snode
            for va, tn in hp_chdic.items():
                tn_vk12_residue_vkdic = tn.check_sat(tnode.hsat)
                # if tnode.hsat not allowed by tn, return value is None
                # or, it is a vk12dic from tn, filtered by tnode.hsat
                if tn_vk12_residue_vkdic != None:  # {} or {..}
                    vk12m = tnode.find_path_vk12m(tn_vk12_residue_vkdic)
                    if vk12m:
                        names = [tn.name]
                        if final:
                            self.finalize(vk12m, names)
                        else:
                            names.insert(0, tnode.name)
                            self.dic[tuple(names)] = vk12m
                # else:   # tn_vk12_residue_vkdic == None
                #   pass  # dump it
        else:
            # holder.parent is not top-level snode, its tnodes has pthmgr
            for va, tn in hp_chdic.items():
                pathdic = tnode.filter_paths(tn.pthmgr)

                # debug info print out
                if self.debug:
                    ks = list(pathdic.keys())
                    print(f'{tnode.name}+{tn.name} path-keys: {ks}')

                for pname, vkm in pathdic.items():
                    if final:
                        self.finalize(vkm, pname)
                    else:
                        self.dic[pname] = vkm

    # def finalize(self, vkm, pathname):
    #     n12 = Node12(self, self.tnode.sh.clone(),
    #                  self.tnode.hsat, vkm)
    #     n12.path_name = pathname
    #     if n12.done:
    #         n12.collect_sat()
    #     else:
    #         n12.spawn()

    def vk2sat(self, vk2, sat, bitSet):
        pass

    def finalize(self, vkm, pathname):
        bit_set = set(range(Center.maxnov))
        sat = {}
        for kn in vkm.kn1s:
            bit = vkm.vkdic[kn].bits[0]
            v = vkm.vkdic[kn].dic[bit]
            sat[bit] = [1, 0][v]
            if bit in bit_set:
                bit_set.remove(bit)

        for kn in vkm.kn2s:
            self.vk2sat(vkm.vkdic[kn], sat, bit_set)

        for name in pathname:
            nov, val = nov_val(name)
            bits = Center.snodes[nov]['choice']
            vals = [get_bit(val, 2), get_bit(val, 1), get_bit(val, 0]
            for ind, b in enumerate(bits):
                sat[b]=vals[ind]
                if b in bit_set:
                    bit_set.remove(b)

        n=len(bit_set)
        if n > 0:
            lst=tuple(bit_set)
            for v in range(n):
                ssat=sat.copy()
                for k in n:
                    ssat[lst[k]]=get_bit(v, k)
                Center.sats.append(ssat)
        else:
            Center.sats.append(sat)
