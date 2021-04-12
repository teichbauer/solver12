
def verify_sat(vkdic, sat):
    for vk in vkdic.values():
        if vk.hit(sat):
            return False
    return True


def get_bit(val, bit):
    return (val >> bit) & 1


def set_bit(val, bit_index, new_bit_value):
    """ Set the bit_index (0-based) bit of val to x (1 or 0)
        and return the new val. the input param val remains unmodified.
        """
    mask = 1 << bit_index  # mask - integer with just the chosen bit set.
    val &= ~mask           # Clear the bit indicated by the mask (if x == 0)
    if new_bit_value:
        val |= mask        # If x was True, set the bit indicated by the mask.
    return val             # Return the result, we're done.


def set_bits(val, d):
    for b, v in d.items():
        val = set_bit(val, b, v)
    return val


def oppo_binary(binary_value):
    return (binary_value + 1) % 2


def get_sdic(filename):
    path = './configs/' + filename
    sdic = eval(open(path).read())
    return sdic


def ordered_dic_string(d):
    m = '{ '
    ks = sorted(d.keys(), reverse=True)
    for k in ks:
        m += str(k) + ': ' + str(d[k]) + ', '
    m = m.strip(', ')
    m += ' }'
    return m


def print_json(nov, vkdic, fname):
    sdic = {
        'nov': nov,
        'kdic': {}
    }
    for kn, vk in vkdic.items():
        sdic['kdic'][kn] = vk.dic
    ks = sorted(list(sdic['kdic'].keys()))

    with open(fname, 'w') as f:
        f.write('{\n')
        f.write('    "nov": ' + str(sdic['nov']) + ',\n')
        f.write('    "kdic": {\n')
        # for k, d in sdic['kdic'].items():
        for k in ks:
            msg = ordered_dic_string(sdic['kdic'][k])
            line = f'        "{k}": {msg},'
            f.write(f'{line}\n')
        f.write('    }\n}')


def topvalue(vk):
    # shift all bit to top positions and return that n-bits value
    # E.G. {7:1, 5:0, 0:1} -> 101/5
    bits = vk.bits[:]
    v = 0
    while bits:
        v = (v << 1) | vk.dic[bits.pop(0)]
    return v


def topbits(nov, nob):
    lst = list(range(nov)[-nob:])
    lst.reverse()
    return lst


def vkdic_remove(vkdic, kns):
    ''' remove vk from vkdic, if vk.kname is in kns(a list)
        '''
    kd = {}
    for kn, vk in vkdic.items():
        if kn not in kns:
            kd[kn] = vk
    return kd


def display_vkdic(vkd, title=None):
    if title:
        print(title)
    kns = list(vkd.keys())
    kns.sort()
    for kn in kns:
        vk = vkd[kn]
        print(f'{kn}: ' + ordered_dic_string(vk.dic))
    print('-------------')
