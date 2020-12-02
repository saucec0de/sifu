#include <iostream>
#include <complex>
#include <new>
#include "factoryComplex.h"

//Constructor allocates the complexContainer array of MAX elements 
FactoryComplex::FactoryComplex(int _max): max(_max){
    position = 0;
    complexContainer = new std::complex<int>[max];
}

//Creates a complex number, stores it in the container and returns a reference to that element
std::complex<int>& FactoryComplex::create(int x, int y) {
  std::complex<int> a = std::complex<int>(x,y);
  complexContainer[position++] = a;
  return a;
}
//Returns a reference to an element stored in the container with an index: index - 1
//If we call .get(1) -> we expect element complexContainer[0]
std::complex<int>& FactoryComplex::get(int index){
  return complexContainer[index - 1];
}

//Frees the allocated array, after calling this method 
//no further method calls should be allowed
//E.g. factoryComplex.get(index);
void FactoryComplex::empty(){
  delete complexContainer;
}
