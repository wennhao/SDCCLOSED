# This function is used to convert a float to a list of bytes in IEEE 754 format
def convert_to_ieee754(value):
    res = list(bytearray(struct.pack("f", value))) + [0]*4
    print(res)
    return res
