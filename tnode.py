from vk12mgr import VK12Manager
from pathmgr import PathManager
from center import Center


class TNode:
    # class-variable repo holds all tnode
    repo = {}   # {<tnode>.name:<tnode-instance>,...}

    def __init__(self, vk12dic, holder_snode, val):
        self.val = val
        self.holder = holder_snode
        self.sh = holder_snode.next_sh
        self.name = f'{self.holder.nov}.{val}'
        self.hsat = holder_snode.sh.get_sats(val)
        self.vkm = VK12Manager(self.sh.ln, vk12dic)

    def check_sat(self, sdic):
        vk12dic = {}
        for kn, vk in self.vkm.vkdic.items():
            total_hit, vk12 = vk.partial_hit_residue(sdic)
            if total_hit:
                return None
            elif vk12:
                vk12dic[kn] = vk12
        return vk12dic

    def find_path_vk12m(self, pnode_leftover_vk12dic):
        vk12m = self.vkm.clone()  # use a clone, don't touch self.vkm.vks
        if not self.add_ancvks(vk12m):
            return None  # anc-vks make vk12m invalid -> negative return
        for kn, vk12 in pnode_leftover_vk12dic.items():
            vk12m.add_vk(vk12)
            if not vk12m.valid:
                return None
        return vk12m

    def filter_paths(self, pathmgr):
        # pathmgr is from higher-level snode.chdic[i].pthmgr
        total_hit = False
        pathdic = {}
        for pthname, vkm in pathmgr.dic.items():
            # if not pathmgr.anchor_verify(vkm.vkdic, pthname):
            #     continue
            if len(self.vkm.vkdic) > 0:
                pvkm = self.vkm.clone()
                if not self.add_ancvks(pvkm):
                    # anc-vks make pvkm invalue -> go next pthname
                    continue
                for kn, vk in vkm.vkdic.items():
                    total_hit, vk12 = vk.partial_hit_residue(self.hsat)
                    if total_hit:
                        break  # -> go next pthname
                    elif vk12:
                        pvkm.add_vk(vk12)
                        if not pvkm.valid:
                            break
            else:  # self.vkm.vkdic is empty, take over vkm
                pvkm = vkm  # dont need to clone(), pvkm will not be modified

            if (not total_hit) and pvkm.valid and len(pvkm.vkdic) > 0:
                pname = list(pthname)
                pname.insert(0, self.name)
                pathdic[tuple(pname)] = pvkm
        return pathdic

    def add_ancvks(self, vkm):
        for nv, vks in Center.anchor_vks.items():
            if nv < self.holder.nov:
                # for anc-vks(all vk3s) of the lower snodes:
                # if any vk1 in vkm can make a anc-vk vk2
                # then add this new vk2 to vkm
                # ----------------------------------------------
                vk1s = self.vkm.vk1s()  # get all vk1 from vkm
                for vk in vks:
                    for vk1 in vk1s:
                        b = vk1.bits[0]
                        # this vk1-bit in vk, and vk[b] has diff value
                        # in that case vk becomes vk2. Add this new vk2
                        if b in vk.bits and vk.dic[b] != vk1.dic[b]:
                            vk2 = vk.clone(vk1.bits)
                            vkm.add_vk(vk2)
        return vkm.valid
