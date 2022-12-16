import struct
a = b'\x0f\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x14\x00abcdefghi\x00'
struct_ = struct.unpack('<qih10s', a)
print(b"abcdefghijkabcdefghijk"*3000)
print(struct_[3].decode("ASCII"))
