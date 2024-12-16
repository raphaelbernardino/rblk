#!/bin/bash
dirpath=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "$dirpath"

nice -17 python3 main.py >/dev/null 2>&1 &
#nice -17 python3 comparacao_qiskit_com_nosso.py >/dev/null 2>&1 &
