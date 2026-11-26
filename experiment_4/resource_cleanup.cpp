#include <cstddef>
#include <cstdint>
#include <memory>
static volatile uint8_t observed;
// Controlled demo: 0xB4 header, operation code, optional payload.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
    if (size < 2 || data[0] != 0xB4) return 0;
#ifdef FIXED
    std::unique_ptr<uint8_t[]> resource(new uint8_t[64]);
    resource[0] = data[1];
    observed = resource[0];
    asm volatile("" : : "r"(resource.get()) : "memory");
    if ((data[1] & 0x80) != 0) return 0; // RAII releases on every exit.
#else
    uint8_t* resource = new uint8_t[64];
    resource[0] = data[1];
    observed = resource[0];
    asm volatile("" : : "r"(resource) : "memory");
    if ((data[1] & 0x80) != 0) return 0; // Bug: early return leaks the allocation.
    delete[] resource;
#endif
    return 0;
}
