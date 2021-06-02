from basics import get_bit, get_sdic, set_bits
from datetime import datetime


class SatHolder:
    ''' Manages variable-/bit-names. '''

    def __init__(self, varray):
        self.varray = varray
        self.ln = len(varray)

    def reduce(self, topbits):
        ''' reduce varray to just the given topbits. 
            return a new satholder with varray containing the bits dropped.
            After this.self.varray has reverse (high>low) bit-order. '''
        varray = [b for b in self.varray if b not in topbits]
        self.varray = list(reversed(topbits[:]))
        self.ln = len(topbits)
        return SatHolder(varray)

    def drop_vars(self, vars):  # drop 1 var or list/set of vars from varray
        if type(vars) == type(0):
            if vars in self.varray:
                self.varray.remove(vars)
                self.ln -= 1
        else:  # list or set
            for v in vars:
                self.drop_vars(v)

    def reduce_vk(self, vk):
        ''' return: vk12, vk3, cvr '''
        hit_bits = set(self.varray).intersection(set(vk.bits))
        ln = len(hit_bits)
        if ln == 0:  # vk is totally outside of sh
            vk3 = vk.clone()
            return None, vk3, None
        if ln == 3:  # vk is totally overlapping with sh
            return None, None, vk.compressed_value()
        # vk is partially in sh, producing a vk12, and cvs
        vk12 = None
        dic = {}  # part of vk.dic lying outside of sh
        for b, v in vk.dic.items():
            if b not in hit_bits:
                dic[b] = v
        vk12 = vk.__class__(vk.kname, dic, vk.nov)

        cvs = set([])
        vlst = range(2 ** self.ln)
        hit_dic = {hbit: self.varray.index(hbit) for hbit in hit_bits}
        for val in vlst:
            covered = True
            for hit_bit, position in hit_dic.items():
                if get_bit(val, position) != vk.dic[hit_bit]:
                    covered = False
                    break
            if covered:
                cvs.add(val)
        return vk12, None, list(cvs)

    def clone(self):
        return SatHolder(self.varray[:])

    def get_sats(self, val):
        assert(val < (2 ** self.ln))
        satdic = {}
        for ind, vn in enumerate(self.varray):
            v = get_bit(val, ind)
            satdic[vn] = v
        return satdic

    def full_sats(self):
        sats = {v: 2 for v in self.varray}
        return sats
