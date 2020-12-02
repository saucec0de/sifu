/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <iostream>
#include <fstream>
#include <sstream>
#include <fstream>
#include <iostream>
#include <ctime> 
#include <exception>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>
#include <complex>
#include "factoryComplex.h"
#include "utils.h"
#include "redirect.h"

int timerExpire(void)         { return 2; }
char *timerErrorMessage(void) { return "This code contains undefined behaviour"; }
char *timerTag(void)          { return "INCREMENTAL_4_FUN6610374294_"; }
std::ostringstream            strCout;
extern int enableLoggingFunction;
    
void Test_1(void) {
    int result = 0;
    try {
        int random_integer = rand()%100; 
        random_integer = random_integer - 100;
        FactoryComplex f (random_integer);
    } catch(...){
        result = 1;
       
    }
    testResult( result
               ,"TEST_130"
               ,"Max size of the container can't be negative."
               ,""
               ,""
               ,"NO_TAG" );
}


//Test create
void Test_2(void) {

    int result = 1;
    try {
        int random_integer_size = rand()%100; 
        int random_integer_x = rand()%100; 
        int random_integer_y = rand()%100; 

        auto compare_element = std::complex<int>(random_integer_x,random_integer_y);
        FactoryComplex f (random_integer_size);
        auto element = f.create(random_integer_x,random_integer_y);
        if (element != compare_element){
            result = 0;
        }
        f.empty();
    } catch(...){
        
        testResult( 0
               ,"TEST_105"
               ,"Not expected exception caught, check corner cases."
               ,""
               ,""
               ,"NO_TAG" );
        
    }
    testResult( result
               ,"TEST_110"
               ,"Method 'create' doesnt't work as specified."
               ,""
               ,""
               ,"NO_TAG" );
}

//Test when container is full
void Test_3(void) {
    int result = 0;

    try {
        
        int random_integer_size = rand()%100; 
        int random_integer_x,random_integer_y; 
        FactoryComplex f (random_integer_size);

        for(int i = 0; i < random_integer_size; i++){
            random_integer_x = rand()%100; 
            random_integer_y = rand()%100; 
           
            auto element = f.create(random_integer_x,random_integer_y);

        }
        random_integer_x = rand()%100; 
        random_integer_y = rand()%100; 

        //+1 elemnt as available
        f.create(random_integer_x,random_integer_y);
       
    } catch(...){
        result = 1;

    }
    testResult( result
               ,"TEST_120"
               ,"Container's max size should not be exceeded."
               ,""
               ,""
               ,"NO_TAG" );
}

//Test get on empty container
void Test_4(void) {
    int result = 0;

    try {
        int random_integer_size = rand()%100 + 10; 

        FactoryComplex f (random_integer_size);
        f.get(random_integer_size - 5);
    } catch(...){
        result = 1;

    }
    testResult( result
               ,"TEST_105"
               ,"Undefined behaviour: When a complex number wasn't added by the user then it shouldn't be returned."
               ,""
               ,""
               ,"INCREMENTAL_2_FACTORY_COMPLEX_INDEX_" );
}

//Test get on index which is out of the range
void Test_5(void) {

    int result = 0;
    try {
        int random_integer_size = rand()%100 +1; 
        int random_integer_x,random_integer_y; 
        FactoryComplex f (random_integer_size);

        for(int i = 0; i < random_integer_size; i++){
            random_integer_x = rand()%100; 
            random_integer_y = rand()%100; 
           
            auto element = f.create(random_integer_x,random_integer_y);

        }
        auto element = f.get(random_integer_size + 1);


    } catch(...){
        result = 1;
    }
    testResult( result
               ,"TEST_105"
               ,"Guarantee that container indices and iterators are within the valid range!"
               ,""
               ,""
               ,"INCREMENTAL_2_FACTORY_COMPLEX_INDEX_" );
}
//Test get
void Test_6(void) {

    int result = 1;
    int random_integer_size = rand()%100 +1; 
    int random_integer_x,random_integer_y; 
    try{
        FactoryComplex f (random_integer_size);
    
        for(int i = 0; i < random_integer_size; i++){
            random_integer_x = rand()%100; 
            random_integer_y = rand()%100; 
            
            auto element = f.create(random_integer_x,random_integer_y);
            element = f.get(i + 1);
            if(element != std::complex<int>(random_integer_x, random_integer_y)){
                result = 0;
            }
        }
    } catch(...){
        testResult( 0
               ,"TEST_105"
               ,"Not expected exception caught, check corner cases."
               ,""
               ,""
               ,"NO_TAG" );
    }
    testResult( result
               ,"TEST_105"
               ,"Method GET doesn't work as specified."
               ,""
               ,""
               ,"NO_TAG" );
}

//Empty method and get after

void Test_7(){
 int result = 0;
    try {
        int random_integer_size = rand()%100; 
        int random_integer_x = rand()%100; 
        int random_integer_y = rand()%100; 

        auto compare_element = std::complex<int>(random_integer_x,random_integer_y);
        FactoryComplex f (random_integer_size);
        auto element = f.create(random_integer_x,random_integer_y);
        f.empty();
        f.get(1);
         element = f.create(random_integer_x,random_integer_y);

    } catch(...){
        
        result = 1;
        
    }
    testResult( result
               ,"TEST_110"
               ,"After method EMPTY has been called, all other methods can't be execudeed, HINT: Throw an exception if that happens"
               ,""
               ,""
               ,"NO_TAG" );
}

//Empty method and create after

int main( void ) {
    srand((unsigned)time(0)); 

    //Test constructor
    Test_1(); 

    //Test create
    Test_2(); 

    //Test when the container is full
    Test_3(); 
                                
    //Test get on empty container
    Test_4(); 

    //Test get on index which is out of the range
    Test_5(); 

    //Test get

    Test_6(); 

    //Test empty
    Test_7(); 

    return 0;
}
