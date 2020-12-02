The global variable "switch_colour_exe_path" contains
the path to the executable file that changes the light
colour. If, for example, the exe path is "./set_lamp",
it needs to be called as follows:
    ./set_lamp -c <colour>
The exe only supports the colours "red", "green" and "blue".
The exe will have exit code 0 on success (i.e. if the colour
is supported and the light colour was successfully switched)
and a non-zero value otherwise.

Tip: if you need to use a standard library function,
make sure the corresponding header is included.

Another tip: you can assume switch_colour_exe_path always has the path to the exe file. That is, you can assume this variable is trusted.
