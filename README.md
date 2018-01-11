## TuringHardware

## Prerequisite

1. python3

### How to use

1. python -m venv .
2. pip install -r requirement.txt
3. [Optional (for testing)] pip install -r test_requirement.txt
4. cd src/
5. python main.py config.yaml


### Testing

#### Auto testing

1. pytest

#### Manual testing

##### max31856

* PYTHONPATH=`pwd` python manual_hardware_check/max31856_check.py

##### max31865

* PYTHONPATH=`pwd` python manual_hardware_check/max31865_check.py

##### process to point translator

* PYTHONPATH=`pwd` python backend/test_process_translate.py

### Known Issues

1. Mixed water PID need to adjust.
