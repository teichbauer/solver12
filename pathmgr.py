from vk12mgr import VK12Manager
from node12 import Node12


class PathManager:
    sats = []
    limit = 10
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

    def finalize(self, vkm, pathname):
        n12 = Node12(self, self.tnode.sh.clone(),
                     self.tnode.hsat, vkm)
        n12.path_name = pathname
        if n12.done:
            n12.collect_sat()
        else:
            n12.spawn()
