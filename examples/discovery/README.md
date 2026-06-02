# Demo — discovery: what stays balanced?

> **Run:** `python examples/discovery/demo.py`

The core capability on synthesized datasets with known answers: it **discovers**
the conservation laws the data obeys (not declared up front), finds the breaks,
reports hidden **separate books**, and **honest-stops** when there is no
structure. An optional final section runs on real `petra-nn` Petri nets if you
pass a path to a petra-nn `examples/` directory:

```
python examples/discovery/demo.py /path/to/petra-nn/examples
```
