import hashlib
from settings import __m__

def in_range(a :int, range :str):
    ''' 
        range: string, in form of "[1, 2]" or "(1, 2]" ... 
        return true if a do in $range, else false
        
        TODO: if range== '[1,1]', it means the point k==1 or means the full circle
    '''
    range = range.strip()
    left, right = range[0], range[-1]
    range = range[1:-1].split(',')
    
    brac = ['[', ']', '(', ')']
    assert left in brac and right in brac and len(range) == 2
    range = [int(i) for i in range]
    b, c = range[0], range[1]

    a %= 1<<__m__
    b %= 1<<__m__
    c %= 1<<__m__

    if left == '[' and right == ']':
        return ( a>=b and a<=c ) if b < c else ( a>=b or a<=c )
    if left == '[' and right == ')':                                              
        return ( a>=b and a<c ) if b < c else ( a>=b or a<c )
    if left == '(' and right == ')':  
        return ( a>b and a<c ) if b < c else ( a>b or a<c )   
    if left == '(' and right == ']': 
        return ( a>b and a<=c ) if b < c else ( a>b or a<=c )


def hash_m(a :str):
    # if(__m__ >= 8):
    #     return int(hashlib.shake_256(a.encode('utf-8')).hexdigest(__m__ >> 3), 16) % (1 << __m__)
    # b = bin(int(hashlib.shake_256(a.encode('utf-8')).hexdigest(1), 16))
    # return int(b[2 : 2+__m__], 2) % (1 << __m__)
    return int(hashlib.sha1(a.encode('utf-8')).hexdigest(), 16) % (1 << __m__)



if __name__ == '__main__':
    # print('test in_range(), __m__ = ', __m__)
    # print('7 in [5,2]', in_range(7, '[5,2]'))
    # print('9 in [5,2]', in_range(9, '[5,2]'))
    print(1 << __m__)
    print(hash_m('127.0.0.1:5000'))
    print(hash_m('127.0.0.1:5001'))
    print(hash_m('abc'))
    print(hash_m('0.0.0.0:5000'))


         
