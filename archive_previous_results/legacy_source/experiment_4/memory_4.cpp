#include <cstdint>
#include <cstddef>
#include <fstream>
#include <vector>
#include <iterator>
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size){
 if(size == 0)return 0;
 volatile uint8_t* p = new uint8_t[64];
 p[0] = data[0];
#ifndef FIXED
 if ((data[0] & 3) == 2) return 0; // omitted delete
#endif
 delete[] const_cast<uint8_t*>(p);
 return 0;
}
#ifdef REPLAY
int main(int argc,char**argv){if(argc!=2)return 2;std::ifstream f(argv[1],std::ios::binary);std::vector<uint8_t> d((std::istreambuf_iterator<char>(f)),{});return LLVMFuzzerTestOneInput(d.data(),d.size());}
#endif
