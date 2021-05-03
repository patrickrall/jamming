import numpy as np
import ctypes

# default: float32
_dtypes = {
    'bool': ctypes.c_bool,
    'int8': ctypes.c_int8,
    'uint8': ctypes.c_uint8,
    'int16': ctypes.c_int16,
    'uint16': ctypes.c_uint16,
    'int32': ctypes.c_int32,
    'uint32': ctypes.c_uint32,
    'int64': ctypes.c_int64,
    'uint64': ctypes.c_uint64,
    'float32': ctypes.c_float,
    'float64': ctypes.c_double,
}

class Vec():
    def __init__(self,*args,dtype='float32'):
        assert dtype in _dtypes
        self._dtype = dtype

        dat = []
        for arg in args:
            if isinstance(arg, Vec):
                l = arg
            elif isinstance(arg, list):
                l = arg
            elif isinstance(arg, np.ndarray):
                l = list(arg.flatten())
            else:
                l = [arg]
            for x in l:
                if 'u' in dtype: assert int(x) >= 0
                if 'bool' in dtype: dat.append(float(x) != 0.)
                if 'int' in dtype: dat.append(int(x))
                if 'float' in dtype: dat.append(float(x))


        assert len(dat) > 0

        self.buffer = (_dtypes[dtype]*len(dat))(*dat)

    @property
    def size(self):
        return ctypes.sizeof(_dtypes[self._dtype])*len(self)

    @property
    def dtype(self):
        return self._dtype

    def __str__(self):
        s = " ".join([str(x) for x in self.buffer])
        return "["+s+"] "+self.dtype

    # by value, not by pointer, ignoring type
    # if you want to compare pointers, call u.buffer == v.buffer
    def __eq__(self, other):
        if not isinstance(other, Vec): return False
        if len(self) != len(other): return False
        for i in range(len(self)):
            if float(self[i]) != float(other[i]): return False
        return True

    def __len__(self):
        return len(self.buffer)

    def __getitem__(self,key):
        return self.buffer[key]

    def __setitem__(self,key,value):
        if 'u' in self.dtype: assert int(value) >= 0
        if 'bool' in self.dtype: self.buffer[key] = (float(value) != 0.)
        if 'int' in self.dtype: self.buffer[key] = int(value)
        if 'float' in self.dtype: self.buffer[key] = float(value)

    def __iter__(self):
        for x in self.buffer:
            yield x

    def __reversed__(self):
        return Vec(*reversed(list(self)), dtype=self.dtype)

    def __add__(self,other):
        assert isinstance(other, Vec)
        assert len(self) == len(other)
        assert self.dtype == other.dtype
        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            if self.dtype == "bool":
                out[i] = (self[i] + other[i]) % 2
            else:
                out[i] = self[i] + other[i]
        return out

    def __iadd__(self,other):
        assert isinstance(other, Vec)
        assert len(self) == len(other)
        assert self.dtype == other.dtype

        for i in range(len(self)):
            if self.dtype == "bool":
                self[i] = (self[i] + other[i]) % 2
            else:
                self[i] = self[i] + other[i]
        return self

    def __sub__(self,other):
        assert isinstance(other, Vec)
        assert len(self) == len(other)
        assert self.dtype == other.dtype
        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            if self.dtype == "bool":
                out[i] = (self[i] + other[i]) % 2
            else:
                if 'u' in self.dtype: assert self[i] >= other[i]
                out[i] = self[i] - other[i]
        return out

    def __isub__(self,other):
        assert isinstance(other, Vec)
        assert len(self) == len(other)
        assert self.dtype == other.dtype

        for i in range(len(self)):
            if self.dtype == "bool":
                self[i] = (self[i] + other[i]) % 2
            else:
                if 'u' in self.dtype: assert self[i] >= other[i]
                self[i] = self[i] - other[i]
        return self

    def __mul__(self,other):
        if 'bool' in self.dtype:
            assert type(other) == bool
            other = int(other)
        if 'int' in self.dtype:
            assert int(other) == other
            other = int(other)
        if 'float' in self.dtype:
            other = float(other)

        assert ('u' not in self.dtype and self.dtype != 'bool') or other >= 0
        if self.dtype == 'bool': assert other in [0.,1.]

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = self[i] * other
        return out

    def __rmul__(self,other):
        return self*other

    def __imul__(self,other):
        if 'bool' in self.dtype:
            assert type(other) == bool
            other = int(other)
        if 'int' in self.dtype:
            assert int(other) == other
            other = int(other)
        if 'float' in self.dtype:
            other = float(other)

        assert ('u' not in self.dtype and self.dtype != 'bool') or other >= 0
        if self.dtype == 'bool': assert other in [0.,1.]

        for i in range(len(self)):
            self[i] = self[i] * other
        return self

    def __imatmul__(self,other):
        assert isinstance(other, np.ndarray)

        assert other.shape[1] == len(self)

        out = zeros(other.shape[0],dtype=self.dtype)
        for i in range(other.shape[0]):
            for j in range(len(self)):
                out[i] += other[i,j] * self[j]
        self.buffer = out.buffer
        return self

    def __truediv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            assert 'int' not in self.dtype or int(self[i]/other) == self[i]/other
            out[i] = self[i]/other
        return out

    def __itruediv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        for i in range(len(self)):
            assert 'int' not in self.dtype or int(self[i]/other) == self[i]/other
            self[i] = self[i]/other
        return self

    def __floordiv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = self[i] // other
        return out

    def __ifloordiv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        for i in range(len(self)):
            self[i] = self[i]//other
        return self

    def __neg__(self):
        assert 'u' not in self.dtype and self.dtype != "bool"
        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = -self[i]
        return out

    def __abs__(self):
        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = abs(self[i])
        return out

    # for boolean vectors
    def __and__(self,other):
        assert isinstance(other, Vec)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert len(self) == len(other)

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = (self[i] == 1.) & (other[i] == 1.)
        return out

    def __iand__(self,other):
        assert isinstance(other, Vec)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert len(self) == len(other)

        for i in range(len(self)):
            self[i] = (self[i] == 1.) & (other[i] == 1.)
        return self

    def __xor__(self,other):
        assert isinstance(other, Vec)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert len(self) == len(other)

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = (self[i] == 1.) ^ (other[i] == 1.)
        return out

    def __ixor__(self,other):
        assert isinstance(other, Vec)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert len(self) == len(other)

        for i in range(len(self)):
            self[i] = (self[i] == 1.) ^ (other[i] == 1.)
        return self

    def __or__(self,other):
        assert isinstance(other, Vec)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert len(self) == len(other)

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = (self[i] == 1.) | (other[i] == 1.)
        return out

    def __ior__(self,other):
        assert isinstance(other, Vec)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert len(self) == len(other)

        for i in range(len(self)):
            self[i] = (self[i] == 1.) | (other[i] == 1.)
        return self

    def __invert__(self):
        assert self.dtype == 'bool'

        out = zeros(len(self),dtype=self.dtype)
        for i in range(len(self)):
            out[i] = not (self[i] == 1.)
        return out

    def setswizzle(self,name,value):
        for c in name:
            if c not in "xyzw": return super().__setattr__(name, value)
            if c == "y" and len(self) < 2: return super().__setattr__(name, value)
            if c == "z" and len(self) < 3: return super().__setattr__(name, value)
            if c == "w" and len(self) < 4: return super().__setattr__(name, value)

        if not isinstance(value,list) and not isinstance(value,Vec):
            value = [value]

        for i in range(len(name)):
            if name[i] == "x": self[0] = value[i]
            if name[i] == "y": self[1] = value[i]
            if name[i] == "z": self[2] = value[i]
            if name[i] == "w": self[3] = value[i]

    def __setattr__(self,name,value):
        self.setswizzle(name,value)


    def swizzle(self,name):
        for c in name:
            if c not in "xyzw0123456789": raise AttributeError
            if c == "y" and len(self) < 2: raise AttributeError
            if c == "z" and len(self) < 3: raise AttributeError
            if c == "w" and len(self) < 4: raise AttributeError

        out = zeros(len(name),dtype=self.dtype)
        for i in range(len(name)):
            if name[i] == "x": out[i] = self[0]
            if name[i] == "y": out[i] = self[1]
            if name[i] == "z": out[i] = self[2]
            if name[i] == "w": out[i] = self[3]
            try:
                out[i] = int(name[i])
            except ValueError:
                pass

        if len(name) == 1: return out[0]
        else: return out


    # xyzw
    def __getattr__(self, name):
        return self.swizzle(name)



def dot(u,v):
    assert isinstance(u, Vec)
    assert isinstance(v, Vec)
    assert len(u) == len(v)

    t = 'bool'
    if 'int' in u.dtype: t = 'int'
    if 'int' in u.dtype: t = 'int'
    if 'float' in u.dtype: t = 'float'
    if 'float' in v.dtype: t = 'float'

    if t == 'bool':
        out = False
        for i in range(len(u)):
            out ^= u[i] & v[i]
    else:
        out = 0.0
        for i in range(len(u)):
            out += float(u[i]) * float(v[i])
        if t == 'int': out = int(out)

    return out

def cross(u,v,dtype='float32'):
    assert dtype != 'bool'
    assert isinstance(u, Vec)
    assert isinstance(v, Vec)
    assert len(u) == 3
    assert len(v) == 3

    out = zeros(len(name),dtype=dtype)
    assert 'u' not in dtype or u[1]*v[2] >= u[2]*v[1]
    out[0] = u[1]*v[2] - u[2]*v[1]
    assert 'u' not in dtype or u[0]*v[2] >= u[2]*v[0]
    out[1] = u[0]*v[2] - u[2]*v[0]
    assert 'u' not in dtype or u[0]*v[1] >= u[1]*v[0]
    out[2] = u[0]*v[1] - u[1]*v[0]
    return out

def zeros(n,dtype='float32'):
    return Vec([0]*n,dtype=dtype)


