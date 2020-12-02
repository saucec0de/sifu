#include <stdio.h>
#include <complex>

#ifndef __FACTORYCOMPLEX__
#define __FACTORYCOMPLEX__

class FactoryComplex{

    std::complex<int>* complexContainer;
    const int max;
    int position;

public:

    FactoryComplex(int max);
    std::complex<int>& create(int x, int y);
    std::complex<int>& get(int index);
    void empty();
};

#endif
