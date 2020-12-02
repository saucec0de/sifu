#include <iostream>
#include <complex>
#include <new>
#include "factoryComplex.h"

FactoryComplex::FactoryComplex(int _max): max(_max){
    if(_max <= 0) throw "Max length can not be negative!";
    position = 0;
    complexContainer = new std::complex<int> [max];
}

std::complex<int>& FactoryComplex::create(int x, int y) {
  if (complexContainer == nullptr) throw "Container has been emptied!";

  if(position >= max) throw "Max size exceeded!";

  complexContainer[position] = std::complex<int>(x,y);
  position++;

  return complexContainer[position-1];
}

std::complex<int>& FactoryComplex::get(int index){
  if (complexContainer == nullptr) throw "Container has been emptied!";

  if(index <= 0 || index >position) throw "Bad index!";

  return complexContainer[index - 1];
}


//double call of empty :D
void FactoryComplex::empty(){
  delete [] complexContainer;
  complexContainer = nullptr;
}

FactoryComplex::~FactoryComplex(){
  delete []complexContainer;
}