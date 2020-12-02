/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
function elFootprint(q) {
    elem = $(q);
    elw    = elem.width();
    elh    = elem.height();
    elTL   = elem.offset();
    left_1 = elTL["left"]
    left_2 = elTL["left"]+elw
    top_1  = elTL["top"]
    top_2  = elTL["top"]+elh

    return { "tl_left" : left_1
            ,"tl_top"  : top_1
            ,"br_left" : left_2
            ,"br_top"  : top_2
           }
}

function between(val, min, max){
    return (val >= min) && (val <= max);
}

function coordInside(left,top,q) {
    footprint = elFootprint(q);
    return between( left, footprint["tl_left"], footprint["br_left"] ) &&
           between( top,  footprint["tl_top"],  footprint["br_top"]  )

}

function elInsideEl(q1,q2) {
    e1Pos = $(q1).offset();
    return coordInside( e1Pos["left"], e1Pos["top"], q2);
}
