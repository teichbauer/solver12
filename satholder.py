from basics import get_bit, get_sdic, set_bits
from datetime import datetime


class SatHolder:
    ''' Manages original variable names. Originally: [0,1,2,..<nov-1>]
        Instance owned by every branch as .sh. At the very beginning,
        br0.sh's array is nov long. br0 has 3 bit-cut, and has
        a tx :[(4,7,(2,6),(1,5),...]. br0.sh will call transfer(br0.tx),
        then cut its tail([0,1,...<nov-4>]) for giving it to br0's every child.
        Afterwards, br0.sh only keeps 3 [4,2,1]
        when br0 has children[1], children[5] (1,5 are sat-values for them),
        the part of sats for this 3-bit will be
        <sat0-1>: {4:0, 2:0, 1:0}  reflecting sat-value 001(1), and
        <sat0-5>: {4:1, 2:0, 1:1}  reflecting sat-value 101(5)
        if eventually r1 gets its sats (of length nov - 3), the total sats-set
        will then include this <sat0-1>, to have complete sats-set.
        This process is true for every child down the tree. So each br-m is done
        it will have a sh of length 1,2 or max:3, containing the variable-names
        for its 1,3 or 7 (2-1, 4-1,8-1) sat-values, and be one part of the
        whole sat-set (chain)
        '''

    def __init__(self, varray):
        self.varray = varray
        self.ln = len(varray)

    def val_gen(self):
        for x in range(2 ** self.ln):
            yield x

    def reduce(self, topbits):
        ''' reduce varray to just the given topbits. 
            return a new satholder with varray containing rest of the bits.
            After this.self.varray has reverse (high>low) bit-order. '''
        varray = [b for b in self.varray if b not in topbits]
        self.varray = list(reversed(topbits[:]))
        self.ln = len(topbits)
        return SatHolder(varray)

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

    # def reduce_vk12(self, vk):
    #     allvalues = set(range(2**self.ln))
    #     hit_bits = set(self.varray).intersection(set(vk.bits))
    #     ln = len(hit_bits)
    #     if ln == 0:
    #         return vk.clone(), allvalues
    #     else:
    #         total_hit, vk12 = vk.partial_hit_residue()

    #     elif ln == vk.nob:
    #         return None, vk.compressed_value()
    #     else:
    #         for b, v in vk.dic.items():
    #             if b in hit_bits:

    def next_sat(self, gen):
        d = {}
        try:
            x = next(gen)
            for b in range(self.ln):
                d[self.varray[b]] = get_bit(x, b)
            return d
        except:
            return False

    def reverse_sdic(self, sdic):
        ' for varray: [0,5,2], sdic{5:0, 2:1, 0:1} -> {1:0, 2:1, 0:1} '
        return {self.varray.index(k): v for k, v in sdic.items()}

    def clone(self):
        return SatHolder(self.varray[:])

    def spawn_tail(self, cutcnt):
        return self.varray[:-cutcnt]

    def transfer(self, txe):
        self.varray = txe.trans_varray(self.varray)

    def cut_tail(self, cutcnt):
        self.varray = self.varray[-cutcnt:]
        self.ln = cutcnt

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

    def bit_tx_map(self, target_sh):
        ''' for each positional bit in sh, find a bit in self.varray,
            the var-value of which is the same as in sh. 
            make a tx_dic = {
                <self-bit>: <target-bit in sh>
            }
            '''
        map_dic = {}
        for b, v in enumerate(target_sh.varray):
            if v in self.varray:
                bit = self.varray.index(v)
                map_dic[bit] = b
        return map_dic
