# Copyright 2002 by Katharine Lindner.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

"""
Hetero, Crystal and Chain exist to represent the NDB Atlas structure.  Atlas is a minimal
subset of the PDB format.  Heteo supports a 3 alphameric code.
The NDB web interface is located at http://ndbserver.rutgers.edu/NDB/index.html
"""


import string, array, copy
from Bio.Seq import Seq
from Bio.Seq import MutableSeq

def wrap_line( line ):
    output = ''
    for i in range( 0, len( line ), 80 ):
        output = output + '%s\n' % line[ i: i + 80 ]
    return output

def validate_key( key ):
    if( type( key ) != type( '' ) ):
        raise CrystalError( 'chain requires a string label' )
    if( len( key ) != 1 ):
        raise CrystalError( 'chain label should contain one letter' )

class Error( Exception ):
    """
    """
    def __init__( self ):
        pass

class CrystalError( Error ):

    """
        message - description of error
    """

    def __init__( self, message ):
        self.message = message

class Hetero:
    """
    This class exists to support the PDB hetero codes.  Supports only the 3 alphameric code.
    The annotation is available from http://alpha2.bmc.uu.se/hicup/
    """
    def __init__(self, data):
        # Enforce string storage
        if( type(data) != type("") ):
            raise CrystalError( 'Hetero data must be an alphameric string' )
        if( data.isalnum() == 0 ):
            raise CrystalError( 'Hetero data must be an alphameric string' )
        if( len( data ) > 3 ):
            raise CrystalError( 'Hetero data may contain up to 3 characters' )
        if( len( data ) < 1 ):
            raise CrystalError( 'Hetero data must not be empty' )

        self.data = data[:].lower()

    def __eq__(self, other):
        return (self.data == other.data )


    def __ne__(self, other):
        """Returns true iff self is not equal to other."""
        return not self.__eq__(other)

    def __repr__(self):
        return "%s" % self.data

    def __str__(self):
        return "%s" % self.data


    def __len__(self): return len(self.data)

class Chain:
    def __init__(self, residues = '' ):
        self.data = []
        if( type( residues ) == type( '' ) ):
            residues = residues.replace( '*', ' ' )
            residues = residues.strip()
            elements = residues.split()
            self.data = map( Hetero, elements )
        elif( type( residues ) == type( [] ) ):
            for element in residues:
                if( not isinstance( element, Hetero ) ):
                    raise CrystalError( 'Text must be a string' )
            for residue in residues:
                self.data.append( residue )
        elif( isinstance( residues, Chain ) ):
            for residue in residues:
                self.data.append( residue )
        self.validate()

    def validate( self ):
        data = self.data
        for element in data:
            self.validate_element( element )

    def validate_element( self, element ):
        if(  not isinstance( element, Hetero ) ):
            raise TypeError

    def __str__( self ):
        output = ''
        i = 0
        for element in self.data:
            output = output + '%s ' % element
        output = output.strip()
        output = wrap_line( output )
        return output


    def __eq__(self, other):
        if( len( self.data ) != len( other.data ) ):
            return 0
        ok = reduce( lambda x, y: x and y, map( lambda x, y: x == y, self.data, other.data ) )
        return ok

    def __ne__(self, other):
        """Returns true iff self is not equal to other."""
        return not self.__eq__(other)

    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]

    def __setitem__(self, i, item):
        try:
            self.validate_element( item )
        except TypeError:
            item = Hetero( item.lower() )
        self.data[i] = item

    def __delitem__(self, i):
        del self.data[i]

    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        return self.__class__(self.data[i:j])

    def __setslice__(self, i, j, other):
        i = max(i, 0); j = max(j, 0)
        if isinstance(other, Chain):
            self.data[i:j] = other.data
        elif isinstance(other, type(self.data)):
            self.data[i:j] = other
        elif type( other ) == type( '' ):
            self.data[ i:j ] = Chain( other ).data
        else:
            raise TypeError

    def __delslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        del self.data[i:j]

    def __contains__(self, item):
        try:
            self.validate_element( item )
        except TypeError:
            item = Hetero( item.lower() )
        return item in self.data

    def append(self, item):
        try:
            self.validate_element( item )
        except TypeError:
            item = Hetero( item.lower() )
        self.data.append(item)

    def insert(self, i, item):
        try:
            self.validate_element( item )
        except TypeError:
            item = Hetero( item.lower() )
        self.data.insert(i, item)

    def remove(self, item):
        item = Hetero( item.lower() )
        self.data.remove(item)

    def count(self, item):
        try:
            self.validate_element( item )
        except TypeError:
            item = Hetero( item.lower() )
        return self.data.count(item)

    def index(self, item):
        try:
            self.validate_element( item )
        except TypeError:
            item = Hetero( item.lower() )
        return self.data.index(item)

    def __add__(self, other):
        if isinstance(other, Chain):
            return self.__class__(self.data + other.data)
        elif type( other ) == type( '' ):
            return self.__class__(self.data + Chain( other).data )
        else:
            raise TypeError

    def __radd__(self, other):
        if isinstance(other, Chain):
            return self.__class__( other.data + self.data )
        elif type( other ) == type( '' ):
            return self.__class__( Chain( other ).data + self.data )
        else:
            raise TypeError

    def __iadd__(self, other):
        if isinstance(other, Chain ):
            self.data += other.data
        elif type( other ) == type( '' ):
            self.data += Chain( other ).data
        else:
            raise TypeError
        return self

class Crystal:
    def __init__(self, data = {} ):
        # Enforcestorage
        if( type( data ) != type( {} ) ):
            raise CrystalError( 'Crystal must be a dictionary' )
        self.data = data
        self.fix()

    def fix( self ):
        data = self.data
        for key in data.keys():
            element = data[ key ]
            if( isinstance( element, Chain ) ):
                pass
            elif type( element ) == type( '' ):
                data[ key ] = Chain( element )
            else:
                raise TypeError



    def __repr__(self):
        output = ''
        keys = self.data.keys()
        keys.sort()
        for key in keys:
            output = output +  '%s : %s\n' % ( key, self.data[ key ] )
        return output

    def __str__(self):
        output = ''
        keys = self.data.keys()
        keys.sort()
        for key in keys:
            output = output +  '%s : %s\n' % ( key, self.data[ key ] )
        return output

    def tostring(self):
        return self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, key): return self.data[key]
    def __setitem__(self, key, item):
        if isinstance( item, Chain ):
            self.data[key] = item
        elif type( item ) == type( '' ):
            self.data[ key ] = Chain( item )
        else:
            raise TypeError

    def __delitem__(self, key): del self.data[key]
    def clear(self): self.data.clear()
    def copy(self):
        return copy.copy(self)
    def keys(self): return self.data.keys()
    def items(self): return self.data.items()
    def values(self): return self.data.values()
    def has_key(self, key): return self.data.has_key(key)
    def get(self, key, failobj=None):
        return self.data.get(key, failobj)
    def setdefault(self, key, failobj=None):
        if not self.data.has_key(key):
            self.data[key] = failobj
        return self.data[key]
    def popitem(self):
        return self.data.popitem()
