#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "utilities.h"
#include "pizza.h"

// global variables
struct PizzaStruct pizza[MAX_PIZZA];
int nrPizzas = 0;

char *pizzaFileName = "pizzas.txt";

// read from "pizzas.txt" unto local variable
void readPizzas(void) {
    FILE *fp;
    char buf[2*(MAX_NAME+MAX_ING)];
    char *pizzaCost;
    char *pizzaName;
    char *pizzaIngredients;
    int   ii;

    fp = fopen(pizzaFileName,"r");
    if (errno!=0) {
        printf("WARNING: could not load any pizza\n");
        return;
    }
    while (1) {
        fgets(buf,2*(MAX_NAME+MAX_ING),fp);
        if (feof(fp)) break;
        pizzaCost = strtok(buf,",");
        pizzaName = strtok(NULL,":");
        removeLeadingChar(pizzaName,' ');
        pizzaIngredients = strtok(NULL,"");
        removeLeadingChar(pizzaIngredients,' ');
        removeTrailingChar(pizzaIngredients,'\n');
        ii = atoi(pizzaCost);
        pizza[nrPizzas].cost = ii;
        strncpy(pizza[nrPizzas].name,pizzaName,MAX_NAME);
        strncpy(pizza[nrPizzas].ingredients,pizzaIngredients,MAX_ING);
        nrPizzas++;
    }
    fclose(fp);
}

// go over the loaded pizzas and fetch the
// ingredients of "pizzaName"
char *getPizzaIngredients( char *pizzaName ){
    int ii;

    for (ii=0; ii<nrPizzas; ii++) {
        if (stricmp(pizza[ii].name,pizzaName)==0) {
            return pizza[ii].ingredients;
        }
    }
    return NULL;
}

// go over the loaded pizzas and fetch the
// cost of "pizzaName"
int getPizzaCost( char *pizzaName ){
    int ii;

    for (ii=0; ii<nrPizzas; ii++) {
        if (stricmp(pizza[ii].name,pizzaName)==0) {
            return pizza[ii].cost;
        }
    }
    return -1;
}

