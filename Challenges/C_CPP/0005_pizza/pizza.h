#ifndef __PIZZA__
#define __PIZZA__

#define MAX_PIZZA 50
#define MAX_NAME  40
#define MAX_ING   100

extern struct PizzaStruct {
    int  cost;
    char name[MAX_NAME];
    char ingredients[MAX_ING];
} pizza[MAX_PIZZA];
extern int nrPizzas;

void readPizzas(void);
char *getPizzaIngredients( char *pizzaName );
int getPizzaCost( char *pizzaName );

#endif
