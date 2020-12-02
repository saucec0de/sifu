#include <iostream>
#include <complex>

void func(void) {
  std::complex<int> nextValue;
  std::complex<int> Values[4] = {0};

  for (int i = 0; i < 4; i++, nextValue = Values[i]) {
    std::cout << i << std::endl;
  }
}
