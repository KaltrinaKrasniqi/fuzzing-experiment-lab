#include <cstdint>
#include <cstddef>
#include <memory>
#include <fstream>
#include <vector>
#include <iterator>
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
 if (size < 1) return 0;
 std::unique_ptr<uint8_t[]> buf(new uint8_t[8]{});
 const size_t index = data[0] % 12;
#ifndef FIXED
 volatile uint8_t* p = buf.get(); p[index] = data[0];
#else
 if (index < 8) { volatile uint8_t* p = buf.get(); p[index] = data[0]; }
#endif
 return 0;
}
#ifdef REPLAY
int main(int argc,char**argv){if(argc!=2)return 2;std::ifstream f(argv[1],std::ios::binary);std::vector<uint8_t> d((std::istreambuf_iterator<char>(f)),{});return LLVMFuzzerTestOneInput(d.data(),d.size());}
#endif
