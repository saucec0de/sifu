#include <iostream>
#include <new>
#include "log.h"

//Don't change the existing class attributes and constructor

class Base
{
    int *containerBase;
public:
        Base(int len)
        {
            //Printing is just for help and debugging purpose
                logger("B constructor");
                containerBase = new int[len];
        }

        ~Base()
        {
            //Printing is just for help and debugging purpose
                logger("B Destroctur");
                delete [] containerBase;
        }
};

//Don't change the existing class attributes and constructor

class Derived : public Base
{
    int * containerDerived;

public:
        Derived(int lenBase, int lenDeriverd): Base(lenBase)
        {
              containerDerived = new int[lenDeriverd];
              //Printing is just for help and debugging purpose
              logger("D constructor");
        }

        ~Derived()
        {
                //Printing is just for help and debugging purpose
                logger("D destroctur");
                delete [] containerDerived;
        }
};

int _main()
{
      

        return 0;
}