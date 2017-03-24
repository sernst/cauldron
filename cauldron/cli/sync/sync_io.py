import binascii
import math
import os
import zlib


def pack_chunk(source_data: bytes) -> str:
    """
    Packs the specified binary source data by compressing it with the Zlib
    library and then converting the bytes to a base64 encoded string for
    non-binary transmission.

    :param source_data:
        The data to be converted to a compressed, base64 string
    """

    chunk_compressed = zlib.compress(source_data)
    return binascii.b2a_base64(chunk_compressed).decode('utf-8')


def unpack_chunk(chunk_data: str) -> bytes:
    """
    Unpacks a previously packed chunk data back into the original
    bytes representation

    :param chunk_data:
        The compressed, base64 encoded string to convert back to the
        source bytes object.
    """

    chunk_compressed = binascii.a2b_base64(chunk_data.encode('utf-8'))
    return zlib.decompress(chunk_compressed)


def read_file_chunks(file_path: str, chunk_size: int = 1000000) -> str:
    """
    Reads the specified file in chunks and returns a generator where
    each returned chunk is a compressed base64 encoded string for sync
    transmission

    :param file_path:
        The path to the file to read in chunks
    :param chunk_size:
        The size, in bytes, of each chunk. The final chunk will be less than
        or equal to this size as the remainder.
    """

    if not os.path.exists(file_path):
        return ''

    file_size = os.path.getsize(file_path)
    chunk_count = max(1, math.ceil(file_size / chunk_size))

    with open(file_path, mode='rb') as fp:
        for chunk_index in range(chunk_count):
            source = fp.read(chunk_size)
            chunk = pack_chunk(source)
            yield chunk


def write_file_chunk(file_path: str, chunk_data: str, append: bool = True):
    """
    Write or append the specified chunk data to the given file path, unpacking
    the chunk before writing. If the file does not yet exist, it will be
    created. Set the append argument to False if you do not want the chunk
    to be appended to an existing file.

    :param file_path:
        The file where the chunk will be written or appended
    :param chunk_data:
        The packed chunk data to write to the file
    :param append:
        Whether or not the chunk should be appended to the existing file. If
        False the chunk data will overwrite the existing file.
    """

    mode = 'ab' if append else 'wb'
    with open(file_path, mode=mode) as f:
        f.write(unpack_chunk(chunk_data))