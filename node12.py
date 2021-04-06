from basics import oppo_binary
from vk12mgr import VK12Manager
from satholder import SatHolder
from tnode import TNode


class Node12:
    def __init__(self, val, parent, sh, hsat, vkm=None):
        self.parent = parent
        self.hsat = hsat
        self.nov = sh.ln
        if vkm:
            self.vkmgr = vkm
        else:
            self.vkmgr = VK12Manager(self.nov)
        self.val = val
        self.chdic = {}
        self.sh = sh
        self.done = self.check_done()

    def check_done(self):
        if self.nov == 0:
            return True
        ln = len(self.vkmgr.vkdic)
        if ln == 0:
            self.tsat = {}
            for v in self.sh.varray:
                self.tsat[v] = 2
            return True
        elif ln == 1:
            self.tsat = {}
            vk = list(self.vkmgr.vkdic.values())[0]
            if vk.nob == 1:
                b = vk.bits[0]
                for v in self.sh.varray:
                    if v == b:
                        self.tsat[v] = oppo_binary(vk.dic[b])
                    else:
                        self.tsat[v] = 2
                return True
            else:   # vk.nob == 2
                b0, b1 = vk.bits
                # make 2 dicts: d0 and d1, so that
                # vk.hit(d0) == Flase, vk.hit(d1) == False
                d0 = vk.dic.copy()
                d0[b0] = oppo_binary(vk.dic[b0])  # twist b0-value
                d1 = vk.dic.copy()
                d1[b1] = oppo_binary(vk.dic[b1])  # twist b1-value
                # sat0: if hit b0/b1 take values from d0. otherwise value=2
                tsat0 = {}
                for v in self.sh.varray:
                    if v == b0:
                        tsat0[v] = d0[v]
                    elif v == b1:
                        tsat0[v] = d0[v]
                    else:
                        tsat0[v] = 2
                # sat1: if hit b0/b1 take values from d1. otherwise value=2
                tsat1 = {}
                for v in self.sh.varray:
                    if v == b0:
                        tsat1[v] = d1[v]
                    elif v == b1:
                        tsat1[v] = d1[v]
                    else:
                        tsat1[v] = 2

                self.tsat = [tsat0, tsat1]
                return True
        return False

    def collect_sat(self, tsat=None):
        if tsat == None:
            self.collect_sat(self.tsat)
        else:
            if type(tsat) == type([]):
                for ts in tsat:
                    self.collect_sat(ts)
            else:
                sat = tsat.copy()
                if len(self.hsat) < 3:
                    # if hsat has 3, it is duplicate of its parent /tnode
                    # that will be collected in the following while loop
                    sat.update(self.hsat)
                if isinstance(self.parent, Node12):
                    self.parent.collect_sat(sat)
                else:  # parent is PathManager with a class-var(list).sats
                    pthnames = self.path_name[:]
                    i = 0
                    while i < len(pthnames):
                        tn = TNode.repo[pthnames[i]]
                        sat.update(tn.hsat)
                        i += 1
                    self.parent.sats.append(sat)

    def spawn(self):
        self.bvk = self.vkmgr.pick_bvk()
        self.next_sh = self.sh.reduce(self.bvk.bits)

        # generate dic of Node12 instances, keyed by val
        self.chdic = self.vkmgr.morph(self)

        vals = list(self.chdic.keys())
        for val in vals:
            if self.chdic[val].done:
                self.chdic[val].collect_sat()
            else:
                self.chdic[val].spawn()
