import struct
a = b'\x0f\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x14\x00abcdefghi\x00'
struct_ = struct.unpack('<qih10s', a)
print(struct_)
print(struct_[3].decode("ASCII"))
