from basics import print_json, display_vkdic
from satholder import SatHolder
from pathmgr import PathManager
from center import Center


class SatNode:
    debug = False
    # debug = True

    def __init__(self, parent, sh, vkm):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm
        self.nov = vkm.nov
        self.next = None
        self.done = False
        self.prepare()

    def prepare(self):
        self.choice = self.vkm.choose_anchor()
        for bvkn in self.choice['ancs']:
            bvk = self.vkm.vkdic[bvkn]
            Center.anchor_vks.setdefault(self.nov, []).append(bvk)
        self.next_sh = self.sh.reduce(self.choice['bits'])

        self.vk12dic = {}  # store all vk12s, all tnode's vkdic ref to here
        self.tx_vkm, self.chdic = self.vkm.morph(self)  # tx_vkm: all vk3s
        self.done = (self.tx_vkm == None) or len(self.tx_vkm.vkdic) == 0
        if self.debug:
            ks = [f'{self.nov}.{k}' for k in self.chdic.keys()]
            print(f'keys: {ks}')
        Center.snodes[self.nov] = self
        self.make_paths()
        if self.parent:
            self.parent.chdic = {}
        # cnts = self.update_cnt()
    # end of def prepare(self):

    def spawn(self):
        # print(f'snode-nov{self.nov}')
        # after morph, vkm.vkdic only have vk3s left, if any
        if len(self.chdic) == 0:
            self.done = True
            return None
        else:
            self.next = SatNode(self, self.next_sh.clone(), self.tx_vkm)
            return self.next

    def make_paths(self):
        if not self.parent:  # do nothing for top-level snode
            return
        # collect higher-chs, and the ones being refed by this snode
        higher_vals_inuse = set([])
        dels = []   # for collecting tnode with no path
        for val, tnode in self.chdic.items():
            tnode.pthmgr = PathManager(tnode, self.done)
            if len(tnode.pthmgr.dic) == 0:
                dels.append(tnode)
            else:
                high_vals = [int(k[1].split('.')[1]) for k in tnode.pthmgr.dic]
                higher_vals_inuse.update(high_vals)
        # clean-up ch-tnodes, if its pthmgr.dic is empty
        for tnode in dels:
            self.chdic.pop(tnode.val)
            Center.repo.pop(tnode.name, None)
        # clean-up higher-chs not being used by any tnode
        self.parent.trim_chs(higher_vals_inuse)
        # cnts = self.update_cnt()
        x = 1

    def trim_chs(self, used_vals):
        ''' the chdic keys not in used_vals(a set), will be deleted. if this
            changs used val-set of parent level, recursiv-call on parent '''
        s = set(self.chdic.keys())
        if s != used_vals:
            delta = s - used_vals
            for v in delta:
                tn = self.chdic.pop(v, None)
                if tn:
                    Center.repo.pop(tn.name, None)
            if self.parent:
                # recursive call of parent.trim_chs
                higher_vals_inuse = set([])
                for tn in self.chdic.values():
                    vs = [int(k[1].split('.')[1]) for k in tn.pthmgr.dic]
                    higher_vals_inuse.update(vs)
                self.parent.trim_chs(higher_vals_inuse)

    def is_top(self):
        return self.nov == Center.maxnov

    def solve(self):
        return Center.sats

    def update_cnt(self):
        cnts = {}
        for nov, sn in Center.snodes.items():
            if nov < Center.maxnov:
                cnt = {v: len(tn.pthmgr.dic.keys())
                       for v, tn in sn.chdic.items()}
                cnts[nov] = cnt
        return cnts
