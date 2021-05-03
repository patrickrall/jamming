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
            elif isinstance(arg, Mat):
                l = [v for (_,_,v) in arg.T()]
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
        assert isinstance(other, Mat)

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

    # xyzw
    def __setattr__(self, name,value):
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


    # xyzw
    def __getattr__(self, name):
        for c in name:
            if c not in "xyzw01": raise AttributeError
            if c == "y" and len(self) < 2: raise AttributeError
            if c == "z" and len(self) < 3: raise AttributeError
            if c == "w" and len(self) < 4: raise AttributeError

        out = zeros(len(name),dtype=self.dtype)
        for i in range(len(name)):
            if name[i] == "x": out[i] = self[0]
            if name[i] == "y": out[i] = self[1]
            if name[i] == "z": out[i] = self[2]
            if name[i] == "w": out[i] = self[3]
            if name[i] == "0": out[i] = 0
            if name[i] == "1": out[i] = 1

        if len(name) == 1: return out[0]
        else: return out


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


class Mat():
    # either a list of lists/vectors
    # if a list of vecs, then the vectors are rows
    # if just a bunch of vecs, then the vectors are columns
    def __init__(self,*args,dtype='float32'):
        assert dtype in _dtypes
        self._dtype = dtype
        assert len(args) > 0

        transpose = True
        if isinstance(args[0], list):
            if len(args[0]) >= 0 and \
                    (isinstance(args[0][0], list) or\
                    isinstance(args[0][0], Vec)):
                transpose = False
                assert len(args) == 1

                args = args[0]
                assert len(args) > 0

        cols = len(args)
        rows = None

        for arg in args:
            if isinstance(arg, list) or isinstance(arg, Vec):
                if rows is None: rows = len(arg)
                assert len(arg) == rows
                continue
            assert isinstance(arg, Mat)
            r,c = arg.shape
            if rows is None: rows = r
            assert r == rows
            cols += c-1

        if not transpose: cols,rows = rows,cols

        self.buffer = (_dtypes[dtype]*(cols*rows))(0)
        i = 0
        for arg in args:
            if isinstance(arg, list) or isinstance(arg, Vec):
                j = 0
                for x in arg:

                    if transpose: k = j*cols + i
                    else: k = i*cols + j

                    if 'bool' in dtype: self.buffer[k] = float(x) != 0.
                    if 'int' in dtype: self.buffer[k] = int(x)
                    if 'float' in dtype: self.buffer[k] = float(x)

                    j += 1
            else:
                assert isinstance(arg, Mat)

                for (ii,jj,x) in arg:
                    if transpose: k = ii*cols + i+jj
                    else: k = (i+ii)*cols + ii
                    if 'bool' in dtype: self.buffer[k] = float(x) != 0.
                    if 'int' in dtype: self.buffer[k] = int(x)
                    if 'float' in dtype: self.buffer[k] = float(x)

                i += arg.shape[1]-1

            i += 1

        self._shape = rows,cols

    @property
    def size(self):
        return ctypes.sizeof(_dtypes[self._dtype])*self._shape[0]*self._shape[1]

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return self._shape

    def __str__(self):
        r,c = self.shape
        ll = []
        for i in range(r):
            l = []
            for j in range(c):
                l.append(str(self.buffer[i*c + j]))
            ll.append("["+" ".join(l)+"]")
        return "\n".join(ll) + " " + self.dtype

    # by value, not by pointer, ignoring type
    # if you want to compare pointers, call u.buffer == v.buffer
    def __eq__(self, other):
        if not isinstance(other, Mat): return False
        if self.shape != other.shape: return False
        r,c = self.shape
        for i in range(r*c):
            if float(self[i]) != float(other[i]): return False
        return True

    def __iter__(self):
        r,c = self.shape
        for i in range(r):
            for j in range(c):
                yield (i,j,self.buffer[i*c + j])

    def __contains__(self,item):
        for _,_,v in self:
            if item == v: return True
        return False

    @property
    def T(self):
        r,c = self.shape
        out = zeros(c,r,dtype=self.dtype)
        for i,j,v in self:
            out[j,i] = v
        return out


    def __getitem__(self,key):
        assert isinstance(key,tuple)
        assert len(key) == 2
        i,j = key
        r,c = self.shape

        if not isinstance(i,slice) and not isinstance(j,slice):
            assert i >= 0 and i < r
            assert j >= 0 and j < r
            return self.buffer[i*c+j]

        if isinstance(i,slice): i = range(*i.indices(r))
        else: i = [i]
        if isinstance(j,slice): j = range(*j.indices(c))
        else: j = [j]

        assert len(i) > 0 and len(j) > 0

        out = zeros(len(i),len(j),dtype=self.dtype)
        ii = 0 # indices within out
        for iii in i: # indices within self
            jj = 0
            for jjj in j:
                out.buffer[ii*len(j)+jj] = self.buffer[iii*c+jjj]
                jj += 1
            ii += 1
        return out

    def __setitem__(self,key,value):
        assert isinstance(key,tuple)
        assert len(key) == 2
        i,j = key
        r,c = self.shape

        if not isinstance(i,slice) and not isinstance(j,slice):
            assert i >= 0 and i < r
            assert j >= 0 and j < r
            k = i*c+j
            if 'u' in self.dtype: assert int(value) >= 0
            if 'bool' in self.dtype: self.buffer[k] = float(value) != 0.
            if 'int' in self.dtype: self.buffer[k] = int(value)
            if 'float' in self.dtype: self.buffer[k] = float(value)
            return

        assert isinstance(value,Mat)

        if isinstance(i,slice): i = range(*i.indices(r))
        else: i = [i]
        if isinstance(j,slice): j = range(*j.indices(c))
        else: j = [j]

        assert value.shape == (len(i),len(j))

        ii = 0 # indices within value
        for iii in i: # indices within self
            jj = 0
            for jjj in j:
                self[iii,jjj] = value.buffer[ii*len(j)+jj]
                jj += 1
            ii += 1

    def __add__(self,other):
        assert isinstance(other, Mat)
        assert self.shape == other.shape
        assert self.dtype == other.dtype
        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            if self.dtype == "bool":
                out[i,j] = (v + other[i,j]) % 2
            else:
                out[i,j] = v + other[i,j]
        return out

    def __iadd__(self,other):
        assert isinstance(other, Mat)
        assert self.shape == other.shape
        assert self.dtype == other.dtype

        for i,j,v in self:
            if self.dtype == "bool":
                self[i,j] = (v + other[i,j]) % 2
            else:
                self[i,j] = v + other[i,j]
        return self

    def __sub__(self,other):
        assert isinstance(other, Mat)
        assert self.shape == other.shape
        assert self.dtype == other.dtype
        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            if self.dtype == "bool":
                out[i,j] = (v + other[i,j]) % 2
            else:
                if 'u' in self.dtype: assert v >= other[i]
                out[i,j] = v - other[i,j]
        return out

    def __isub__(self,other):
        assert isinstance(other, Mat)
        assert self.shape == other.shape
        assert self.dtype == other.dtype

        for i,j,v in self:
            if self.dtype == "bool":
                self[i,j] = (v + other[i,j]) % 2
            else:
                if 'u' in self.dtype: assert v >= other[i]
                self[i,j] = v - other[i,j]
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

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = v*other
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

        for i,j,v in self:
            self[i,j] = v*other
        return self

    def __matmul__(self,other):
        if isinstance(other, Mat):
            assert self.shape[1] == other.shape[0]
            r,l = self.shape
            _,c = other.shape

            out = zeros(r,c,dtype=self.dtype)
            for i in range(r):
                for j in range(c):
                    for k in range(l):
                        out.buffer[i*c+j] += other.buffer[i*l+k] * self.buffer[k*c+j]
            return out

        assert isinstance(other, Vec)
        r,l = self.shape
        assert l == len(other)
        out = zeros(r,dtype=self.dtype)
        for i in range(r):
            for k in range(l):
                out[i] += self[i,k] * other[k]
        return out

    # multiplies from the left, not from the right,
    # A @= B turns A into BA.
    def __imatmul__(self,other):
        assert isinstance(other, Mat)

        assert other.shape[1] == self.shape[0]
        r,l = other.shape
        _,c = self.shape

        # by hand
        out = zeros(r,c,dtype=self.dtype)
        for i in range(r):
            for j in range(c):
                for k in range(l):
                    out.buffer[i*c+j] += other.buffer[i*l+k] * self.buffer[k*c+j]

        self.buffer = out.buffer
        self._shape = out.shape
        return self


    def __truediv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            assert 'int' not in self.dtype or int(v/other) == v/other
            out[i,j] = v/other
        return out

    def __itruediv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        for i,j,v in self:
            assert 'int' not in self.dtype or int(v/other) == v/other
            self[i,j] = v/other
        return self

    def __floordiv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = v // other
        return out

    def __ifloordiv__(self,other):
        assert self.dtype != 'bool'

        other = float(other)
        assert 'u' not in self.dtype or other >= 0

        for i,j,v in self:
            assert 'int' not in self.dtype or int(v/other) == v/other
            self[i,j] = v // other
        return self

    def __neg__(self):
        assert 'u' not in self.dtype and self.dtype != "bool"
        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = -v
        return out

    def __abs__(self):
        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = abs(v)
        return out

    # for boolean vectors
    def __and__(self,other):
        assert isinstance(other, Mat)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert self.shape == other.shape

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = (v == 1.) & (other[i,j] == 1.)
        return out

    def __iand__(self,other):
        assert isinstance(other, Mat)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert self.shape == other.shape

        for i,j,v in self:
            self[i,j] = (v == 1.) & (other[i,j] == 1.)
        return self

    def __xor__(self,other):
        assert isinstance(other, Mat)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert self.shape == other.shape

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = (v == 1.) ^ (other[i,j] == 1.)
        return out

    def __ixor__(self,other):
        assert isinstance(other, Mat)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert self.shape == other.shape

        for i,j,v in self:
            self[i,j] = (v == 1.) ^ (other[i,j] == 1.)
        return self

    def __or__(self,other):
        assert isinstance(other, Mat)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert self.shape == other.shape

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = (v == 1.) | (other[i,j] == 1.)
        return out

    def __ior__(self,other):
        assert isinstance(other, Mat)
        assert self.dtype == 'bool'
        assert other.dtype == 'bool'
        assert self.shape == other.shape

        for i,j,v in self:
            self[i,j] = (v == 1.) | (other[i,j] == 1.)
        return self

    def __invert__(self):
        assert self.dtype == 'bool'

        out = zeros(*self.shape,dtype=self.dtype)
        for i,j,v in self:
            out[i,j] = not (v == 1.)
        return out

    #######################

    # remove i'th row and j'th column
    def minor(self,i,j):
        assert i >= 0
        assert j >= 0
        assert self.shape[0] > i
        assert self.shape[1] > j
        out = zeros(self.shape[0]-1,self.shape[1]-1,dtype=self.dtype)
        for ii in  range(self.shape[0]-1):
            for jj in  range(self.shape[0]-1):
                iii = ii
                jjj = jj
                if ii >= i: iii += 1
                if jj >= j: jjj += 1
                out[ii,jj] = self[iii,jjj]
        return out


    def det(self):
        assert self.shape[0] == self.shape[1]
        if self.shape[0] == 1:
            return self[0,0]

        # https://en.wikipedia.org/wiki/Laplace_expansion
        out = 0
        for j in range(self.shape[0]):
            out += (-1)**j * self[0,j] * self.minor(0,j).det()

        if self.dtype == 'bool': return out % 2
        return out

    def inverse(self):
        # should implement inverse over F2 if type is bool
        assert "int" not in self.dtype

        # https://semath.info/src/inverse-cofactor-ex4.html
        # A^{-1} = adjugate(A) / det(A)
        # adjugate(A)_(i,j) = (-1)^(i-j) * A.minor(j,i).det()

        det = self.det()
        assert det != 0

        out = zeros(*self.shape,dtype=self.dtype)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                out[i,j] = (-1)**(i-j) * self.minor(j,i).det()  / det

        return out


def zeros(*args,dtype='float32'):
    assert dtype in _dtypes
    assert len(args) in [1,2]

    for x in args:
        assert x == int(x)
        assert x > 0

    if len(args) == 1:
        v = Vec(0,dtype=dtype)
        v.buffer = (_dtypes[dtype]*int(args[0]))(0)
        return v

    r,c = args
    assert int(r) == r
    assert int(c) == c
    assert r > 0
    assert c > 0

    out = Mat([0],dtype=dtype)
    out.buffer = (_dtypes[dtype]*(r*c))(0)
    out._shape = r,c
    return out

def eye(size,dtype='float32'):
    out = zeros(size,size,dtype=dtype)
    for i in range(size):
        out.buffer[i*size+i] = 1
    return out


# implements the permutation
# XYZW -> perm
# can also do signed permutations: XZ-YW
def permutation(perm,dtype='float32'):
    assert len(perm.replace("-","")) == 4
    for s in "XYZW": assert s in perm
    for s in perm: assert s in "XYZW-"

    out = zeros(4,4,dtype=dtype)
    idx = 0
    sign = 1
    for i in range(4):
        while perm[idx] == "-":
            sign *= -1
            idx += 1
        out["XYZW".index(perm[idx]),i] = sign
        sign = 1
        idx += 1
    return out




