'''Little-endian 16bit integer'''
def lint16(b):
    return (b[1] <<8) | b[0]

def lint16a(n):
    return bytes([n % 256, n // 256])

'''Little-endian 32bit integer'''
def lint32(b):
    return (((((b[3] <<8) | b[2]) <<8) | b[1]) <<8) | b[0]

def lint32a(n):
    return bytes([n%256, (n>>8)%256, (n >> 16)%256, (n>>24)%256])

'''Big-endian 16bit integer'''
def bint16(b):
    return (b[0] <<8) | b[1]

'''Big-endian 32bit integer'''
def bint32(b):
    return (((((b[0] <<8) | b[1]) <<8) | b[2]) <<8) | b[3]
 
'''decode a null-terminated string'''
str0 = lambda z: z[:z.index(0)].decode('ascii')   


