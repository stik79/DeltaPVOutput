DeltaPVOutput
=============

A series of python scripts to use RS485 Serial from Delta Inverter to PVOutput.org

DeltaInverter Module has two major functions:
Generation of Command Strings to be sent over RS485 to the inverter

Parsing of response strings received from the inverter, this is done in two forms:
1) Obtain the raw values using getValueFromResponse 
2) Obtain a formatted response using getFormattedResponse which will contain the instruction/value/unit tuple

A list of instructions known is also in the module, no doubt there's more but these were the ones I gleaned from Sorin/4lex/Raiki @ whirlpool.net.au

DeltaPVOutput - simply queries the inverter and posts the result to PVOutput.org