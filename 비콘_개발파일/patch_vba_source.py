"""
VBA 압축 소스코드까지 패치 (J1:K4 -> I1:K5, ws.Range("J1") -> ws.Range("I1"))
oletools의 VBA 압축/해제 사용
"""
import zipfile, shutil, os
from io import BytesIO

# oletools에서 VBA 압축/해제 함수 임포트
from oletools.olevba import VBA_Parser, decompress_stream

def compress_vba(data: bytes) -> bytes:
    """VBA 소스코드 압축 (MS-OVBA CompressedContainer format)"""
    # VBA 압축 알고리즘 구현
    # Signature byte: 0x01
    result = bytearray(b'\x01')
    i = 0
    decompressed = data

    while i < len(decompressed):
        # 청크 단위(4096바이트) 처리
        chunk_start = i
        chunk_end = min(i + 4096, len(decompressed))
        chunk = decompressed[chunk_start:chunk_end]

        # 청크를 압축
        compressed_chunk = _compress_chunk(chunk)
        result.extend(compressed_chunk)
        i = chunk_end

    return bytes(result)

def _compress_chunk(raw: bytes) -> bytes:
    """단일 4096바이트 청크 압축"""
    if not raw:
        return b''

    # RawChunk: CompressedFlag=0, 복사본 그대로
    if len(raw) < 3:
        # 너무 짧으면 raw chunk
        size = len(raw) - 1
        header = (size & 0x0FFF) | 0x0000  # CompressedFlag=0
        return bytes([header & 0xFF, (header >> 8) & 0xFF]) + raw + bytes(4096 - len(raw))

    # 간단한 압축 시도
    out = bytearray()
    pos = 0

    while pos < len(raw):
        flags = 0
        tokens = bytearray()

        for bit in range(8):
            if pos >= len(raw):
                tokens.append(raw[pos-1] if pos > 0 else 0)
                continue

            # 최대 길이/오프셋 계산
            copy_len = min(len(out) + pos, 4096)
            best_offset = 0
            best_length = 0

            if copy_len > 0:
                decompressed_so_far = bytes(raw[:pos])
                min_offset = max(1, pos - 4096)
                for offset in range(1, pos - min_offset + 1):
                    l = 0
                    while (l < 4096 and
                           pos + l < len(raw) and
                           raw[pos - offset + (l % offset)] == raw[pos + l]):
                        l += 1
                    if l >= 3 and l > best_length:
                        best_length = l
                        best_offset = offset

            if best_length >= 3:
                flags |= (1 << bit)
                # CopyToken
                decompressed_size = pos + 1
                if decompressed_size <= 16: length_mask, offset_mask, bit_count, max_length = 0xF, 0xFFF0, 12, 19
                elif decompressed_size <= 32: length_mask, offset_mask, bit_count, max_length = 0x1F, 0xFFE0, 11, 35
                elif decompressed_size <= 64: length_mask, offset_mask, bit_count, max_length = 0x3F, 0xFFC0, 10, 67
                elif decompressed_size <= 128: length_mask, offset_mask, bit_count, max_length = 0x7F, 0xFF80, 9, 131
                elif decompressed_size <= 256: length_mask, offset_mask, bit_count, max_length = 0xFF, 0xFF00, 8, 259
                elif decompressed_size <= 512: length_mask, offset_mask, bit_count, max_length = 0x1FF, 0xFE00, 7, 515
                elif decompressed_size <= 1024: length_mask, offset_mask, bit_count, max_length = 0x3FF, 0xFC00, 6, 1027
                elif decompressed_size <= 2048: length_mask, offset_mask, bit_count, max_length = 0x7FF, 0xF800, 5, 2051
                else: length_mask, offset_mask, bit_count, max_length = 0xFFF, 0xF000, 4, 4099

                length_field = min(best_length - 3, length_mask)
                offset_field = (best_offset - 1) << (16 - bit_count)
                copy_token = (offset_field | length_field) & 0xFFFF
                tokens.extend([copy_token & 0xFF, (copy_token >> 8) & 0xFF])
                pos += best_length
            else:
                tokens.append(raw[pos])
                pos += 1

        out.append(flags)
        out.extend(tokens[:min(len(tokens), 8 * 2)])  # rough

    # CompressedChunkHeader
    size = len(out)
    if size < len(raw):
        header = ((size - 1) & 0x0FFF) | 0xB000  # CompressedFlag=1, Signature=0xB
        return bytes([(header & 0xFF), ((header >> 8) & 0xFF)]) + bytes(out)
    else:
        # Raw chunk (uncompressed)
        header = ((len(raw) - 1) & 0x0FFF) | 0x0000
        padded = raw + bytes(4096 - len(raw))
        return bytes([(header & 0xFF), ((header >> 8) & 0xFF)]) + padded


# 실제로는 oletools 내부 구현을 사용하는 더 간단한 방법:
# OLE 스트림에서 직접 소스코드 위치 찾기
import struct

def find_and_patch_source_in_bin(vba_bin: bytes) -> bytes:
    """
    vbaProject.bin에서 압축된 VBA 소스코드를 찾아
    J1:K4 -> I1:K5, J1 anchor -> I1 로 패치

    VBA 모듈 압축 해제 후 수정, 재압축하는 방식은 복잡하므로
    oletools decompress_stream을 활용
    """
    from oletools import crypto
    import olefile
    from io import BytesIO

    # olefile로 OLE 구조 파싱
    ole = olefile.OleFileIO(BytesIO(vba_bin))

    # VBA 프로젝트 내 모든 스트림 목록
    streams = ole.listdir()

    patched_bin = bytearray(vba_bin)

    for stream_path in streams:
        stream_name = stream_path[-1] if stream_path else ''
        full_path = '/'.join(stream_path)

        # 모듈 스트림인지 확인 (Module3 등)
        try:
            data = ole.openstream(stream_path).read()
        except:
            continue

        # PerformanceCache 오프셋 (offset 3, uint32 LE)
        if len(data) < 8:
            continue

        try:
            perf_offset = struct.unpack_from('<I', data, 3)[0]
        except:
            continue

        if perf_offset >= len(data) or perf_offset < 7:
            continue

        # 압축된 소스코드 시작
        compressed = data[perf_offset:]
        if not compressed or compressed[0:1] != b'\x01':
            continue

        # 압축 해제 시도
        try:
            decompressed = decompress_stream(compressed)
        except:
            continue

        if not decompressed:
            continue

        # J1:K4 검색
        if b'J1:K4' not in decompressed and b'Range("J1")' not in decompressed and b'Range("J1"' not in decompressed:
            continue

        print(f'  소스 패치 대상: {full_path} ({len(decompressed)} bytes)')

        # 패치
        new_decompressed = decompressed
        new_decompressed = new_decompressed.replace(b'J1:K4', b'I1:K5')
        new_decompressed = new_decompressed.replace(b'Range("J1")', b'Range("I1")')
        new_decompressed = new_decompressed.replace(b'Range("J1",', b'Range("I1",')

        # 변경이 없으면 스킵
        if new_decompressed == decompressed:
            continue

        changes = decompressed.count(b'J1:K4') + decompressed.count(b'Range("J1")')
        print(f'    변경: {changes}개')

        # 다시 압축 (oletools의 compress_stream 사용)
        try:
            from oletools.olevba import compress_stream
            new_compressed = compress_stream(new_decompressed)
        except ImportError:
            print('    compress_stream 없음 - P-code 패치만 사용')
            continue

        # 새 스트림 데이터 = 헤더 + 새 압축 데이터
        new_data = data[:perf_offset] + new_compressed

        # vba_bin에서 원본 스트림 위치 찾아 교체
        # (olefile의 FAT을 통해 스트림 위치를 찾아야 하는데 복잡함)
        # 대신: 원본 compressed 바이트를 새 compressed 바이트로 교체
        if compressed in vba_bin:
            patched_bin = bytearray(patched_bin)
            idx = bytes(patched_bin).find(compressed)
            if idx >= 0:
                patched_bin[idx:idx+len(compressed)] = new_compressed
                print(f'    소스 스트림 교체 완료')

    ole.close()
    return bytes(patched_bin)


if __name__ == '__main__':
    # oletools에 compress_stream이 있는지 확인
    try:
        from oletools.olevba import compress_stream
        print('compress_stream 사용 가능')
    except ImportError:
        print('compress_stream 없음')
        # 직접 구현 필요하면 here

    # oletools에 decompress_stream 있는지 확인
    try:
        from oletools.olevba import decompress_stream
        print('decompress_stream 사용 가능')
    except ImportError:
        print('decompress_stream 없음')
