#ifndef _MONTHS_H_
#define _MONTHS_H_

const char* get_month(int n) {
    const char* months[] = { "January",
                             "February",
                             "March",
                             "April",
                             // ...and so on
                             "December"};

    return months[n];
}

#endif /* _MONTHS_H_ */
