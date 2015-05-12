#!/usr/bin/python
# coding=utf-8

"""
加密解密carID
"""


class Xcrypt:

    def __init__(self, key=993.141592653589):
        self.key = key
        self.length = 12
        self.strbase = "5z1GydOFmAU2is7JQIk0BV9EuhWbwZXNjSo3cRgDqCtvfrK4xe\
        lanMpH8L6TPY"
        self.codelen = self.strbase[0:self.length]
        self.codenums = self.strbase[self.length:self.length + 10]
        self.codeext = self.strbase[self.length + 10:]

    def encode(self, nums):
        if type(nums) != str:
            nums = str(nums)
        if not nums.isdigit():
            return nums
        rtn = ""
        numslen = len(nums)
        begin = self.codelen[numslen - 1:numslen]

        extlen = self.length - numslen - 1
        temp = "%.12f" % (int(nums) / self.key)
        temp = temp.replace('.', '')
        temp = temp[-extlen:]

        arrnumsTemp = list(self.codenums)
        arrnums = list(nums)

        for v in arrnums:
            rtn += arrnumsTemp[int(v)]

        arrextTemp = list(self.codeext)
        arrext = list(temp)
        for v in arrext:
            rtn += arrextTemp[int(v)]

        return begin + rtn

    def decode(self, code):
        if len(code) != self.length:
            return ''

        begin = code[0:1]
        rtn = ''
        length = self.codelen.find(begin)
        if length != -1:
            length += 1
            arrnums = list(code[1:1 + length])
            for v in arrnums:
                rtn += str(self.codenums.find(v))
        return rtn


def encode(nums):
    en = Xcrypt()
    return en.encode(nums)


def decode(code):
    en = Xcrypt()
    return en.decode(code)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='xcrypt module')
    parser.add_argument('action', type=str, choices=('decode', 'encode'), help='crypt action')
    parser.add_argument('chiper', type=str, help='string to be decoded/encoded')
    args = parser.parse_args()
    en = Xcrypt()
    if args.action == 'encode':
        print en.encode(args.chiper)
    else:
        print en.decode(args.chiper)
