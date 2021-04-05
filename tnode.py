from basics import verify_sat, oppo_binary
from restrict import Restrict
from vk12mgr import VK12Manager


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
        for kn, vk12 in pnode_leftover_vk12dic.items():
            vk12m.add_vk(vk12)
            if not vk12m.valid:
                return None
        return vk12m

    def filter_paths(self, pathmgr):
        pathdic = {}
        for pthname, vkm in pathmgr.dic.items():
            pvkm = self.vkm.clone()
            for kn, vk in vkm.vkdic.items():
                total_hit, vk12 = vk.partial_hit_residue(self.hsat)
                if total_hit:
                    break
                elif vk12:
                    pvkm.add_vk(vk12)
                    if not pvkm.valid:
                        break
            if (not total_hit) and pvkm.valid and len(pvkm.vkdic) > 0:
                pname = list(pthname)
                pname.insert(0, self.name)
                pathdic[tuple(pname)] = pvkm
        return pathdic
