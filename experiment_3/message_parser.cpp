#include <cstddef>
#include <cstdint>
#include <memory>
// Controlled demo format: 0xA5, declared payload length, bytes of payload.
// Capacity of destination is 8 bytes. Fuzzer supplies arbitrary bytes.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
    if (size < 3 || data[0] != 0xA5) return 0;
    const size_t declared = data[1];
    const size_t actual = size - 2;
    if (declared > actual || declared == 0 || declared > 16) return 0;
    std::unique_ptr<uint8_t[]> buffer(new uint8_t[8]);
    volatile uint8_t* output = buffer.get();
#ifdef FIXED
    if (declared > 8) return 0;
#endif
    for (size_t i = 0; i < declared; ++i) {
        output[i] = data[2 + i];  // Buggy: missing capacity check.
    }
    return 0;
}
