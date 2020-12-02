#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "utilities.h"
#include "pizza.h"

#define MAX_ORDER 5

struct {
    int  cost;
    char name[MAX_NAME];
} orderBasket[MAX_ORDER];
int nOrder = 0;

void help( void ) {
    printf("You can enter the following:\n");
    printf("  Type LIST to see the available menu\n");
    printf("  Type the pizza name to add to your order\n");
    printf("  Type DEL to delete the last option\n");
    printf("  Type VIEW view your current basket\n");
    printf("  Type HELP to view this help\n");
    printf("  Type CHECKOUT to proceed to checkout\n");
    printf("  Type EXIT to exit this program\n");
    printf("\n");
    printf("  or just press ENTER to finish\n");
}

int totalCost( void ) {
    int t = 0;
    for (int ii=0; ii<nOrder; ii++ ) {
        t += orderBasket[ii].cost;
    }
    return t;
}

int _main( int argc, char **argv ) {
    char  pizzaName[MAX_NAME];
    char *pizzaIngredients;

    readPizzas();

    printf("Pizza Delivery Inc.\n");
    printf("\n");
    help();

    while (1) {
        printf("> \n");
        fgets(pizzaName,sizeof(pizzaName),stdin);
        removeTrailingChar(pizzaName,'\n');
        printf("\n");

        if (0==stricmp(pizzaName,"list")) {
            printf("Cost  | Name             | Ingredients\n");
            printf("------+------------------+----------------------------------------------------------------------------\n");
            for (int ii=0; ii<nrPizzas; ii++ ) {
                printf("%2.2f  | %-16.16s | %-80.80s\n",pizza[ii].cost/100.0,pizza[ii].name,pizza[ii].ingredients);
            }
            printf("------+------------------+----------------------------------------------------------------------------\n");
            continue;
        }
        if (0==stricmp(pizzaName,"help")) {
            help();
            continue;
        }
        if (0==stricmp(pizzaName,"exit")) {
            break;
        }
        if (0==stricmp(pizzaName,"del")) {
            if (nOrder>0) nOrder--;
            continue;
        }
        if (0==stricmp(pizzaName,"checkout")) {
            if (0==nOrder) {
                printf("You have a sad basket because its empty!\n");
                break;
            } else {
                (1==nOrder) && printf("You have ordered 1 pizza.\n");
                (1<nOrder)  && printf("You have ordered %d pizzas.\n",nOrder);
                printf("Here is your total: %2.2f.\n", totalCost()/100.0);
            }
            continue;
        }
        if (0==stricmp(pizzaName,"view")) {
            if (nOrder>0) {
                printf("Here is your current basket\n\n");
                printf("Cost  | Name             | Ingredients\n");
                printf("------+------------------+----------------------------------------------------------------------------\n");
                for (int ii=0; ii<nOrder; ii++ ) {
                    printf("%2.2f  | %-16.16s | %-80.80s\n",
                            orderBasket[ii].cost/100.0,
                            orderBasket[ii].name,
                            getPizzaIngredients(orderBasket[ii].name));
                }
                printf("------+------------------+----------------------------------------------------------------------------\n");
                printf("\nTotal Cost: %2.2f\n",totalCost()/100.0);
            } else {
                printf("Your basket is currently empty.\n");
            }
            continue;
        }

        pizzaIngredients = getPizzaIngredients(pizzaName);
        if (pizzaIngredients) {
            if (nOrder>=MAX_ORDER) {
                printf("Cannot add pizza - your basket is currently full!\n");
                continue;
            }
            printf("Adding %s to your basket... ", pizzaName);
            orderBasket[nOrder].cost = getPizzaCost(pizzaName);
            strncpy(orderBasket[nOrder].name,pizzaName,MAX_NAME);
            nOrder++;
            printf("done.\n");
        } else {
            printf("Did not get that...\nif you need, just type HELP.\n");
        }
        printf("\n");
    }
    printf("\n");
    printf("Thank you and goodbye!\n");
    return 0;
}
